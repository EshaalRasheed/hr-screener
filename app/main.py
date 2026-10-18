"""HR Screener API: receives a job description + one CV and returns a scored assessment."""
import os

from fastapi import FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.llm import QuotaExceeded
from app.screener import screen_candidate

app = FastAPI(title="AI Hiring Screener", description="Scores CVs against a job description")

MAX_FILE_BYTES = 4 * 1024 * 1024        # Vercel's request limit is ~4.5 MB, so stay below it
MAX_JD_CHARS = 6000                     # job description length limit
MAX_CV_CHARS = 20000                    # pasted CV length limit


@app.exception_handler(QuotaExceeded)
async def quota_handler(request: Request, exc: QuotaExceeded):
    """Free AI quota used up: tell the user clearly instead of crashing."""
    return JSONResponse(status_code=429, content={"detail": "AI quota reached. Please try again later."})


@app.get("/api/health")
def health():
    """Used to check the API is alive."""
    return {"status": "ok"}


@app.post("/api/screen")
async def screen(
    job_description: str = Form(...),          # the role requirements
    cv_text: str = Form(""),                   # a pasted CV (optional)
    cv_file: UploadFile | None = File(None),   # or an uploaded CV file (optional)
):
    """Screen ONE candidate. The web page calls this once per CV, so each request stays small."""
    job_description = job_description.strip()
    if not job_description:
        raise HTTPException(status_code=400, detail="Job description is required")
    if len(job_description) > MAX_JD_CHARS:
        raise HTTPException(status_code=413, detail="Job description is too long")

    file_bytes, file_mime = None, None
    if cv_file is not None:
        data = await cv_file.read()
        if not data:
            raise HTTPException(status_code=400, detail="The uploaded file is empty")
        if len(data) > MAX_FILE_BYTES:
            raise HTTPException(status_code=413, detail="File too large (max 4 MB)")
        name = (cv_file.filename or "").lower()
        if name.endswith(".pdf") or cv_file.content_type == "application/pdf":
            file_bytes, file_mime = data, "application/pdf"   # Gemini reads PDFs directly
        elif name.endswith(".txt"):
            cv_text = data.decode("utf-8", errors="ignore")    # plain text: use as text
        else:
            raise HTTPException(status_code=415, detail="Please upload PDF or TXT files (save Word files as PDF)")

    cv_text = cv_text.strip()[:MAX_CV_CHARS]
    if not cv_text and not file_bytes:
        raise HTTPException(status_code=400, detail="Provide a CV as text or a file")

    # The AI call is blocking, so run it in a worker thread
    return await run_in_threadpool(screen_candidate, job_description, cv_text, file_bytes, file_mime)


# Serve the web page locally; on Vercel, public/ is served by the CDN instead.
if os.path.isdir("public"):
    app.mount("/", StaticFiles(directory="public", html=True), name="public")