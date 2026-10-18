# 🧑‍💼 AI Hiring Screener

**🔗 Live demo:** [your-link.vercel.app](https://your-link.vercel.app)

AI Hiring Screener is a web app that screens CVs against a job description. Paste a job description, upload CVs as PDF or TXT files (or paste them as text), and the app uses Google Gemini to score each candidate from 1 to 10. Every candidate gets a recommendation (Interview, Maybe, or Reject) along with their key strengths, gaps, and a one-line summary. Results appear in a ranked shortlist that can be exported as a CSV file for Excel or Google Sheets.

Scoring considers only job-relevant skills and experience, and CVs are processed in memory without being stored. The app is built with Python, FastAPI, and Google Gemini structured outputs, and is deployed on Vercel.

---

## Steps to run locally

**1. Clone the repository**

```bash
git clone https://github.com/EshaalRasheed/hr-screener.git
cd hr-screener
```

**2. Create and activate a virtual environment**

```bash
python -m venv .venv
.venv\Scripts\Activate.ps1        # Windows PowerShell
# source .venv/bin/activate       # macOS / Linux
```

**3. Install the dependencies**

```bash
pip install -r requirements.txt
```

**4. Create a `.env` file** in the project folder with your Gemini API key and model name

```text
GEMINI_API_KEY=your-gemini-api-key
MODEL=your-gemini-model-name
```

You can get a free API key from [Google AI Studio](https://aistudio.google.com).

**5. Start the server**

```bash
uvicorn app.main:app --reload
```

**6. Open the app**

Go to http://localhost:8000, then click **Load sample job** → **Load sample CVs** → **Screen candidates**.

---

## Steps to deploy on Vercel

1. Push the project to a GitHub repository.
2. On [vercel.com](https://vercel.com), click **Add New → Project** and import the repository.
3. Set **Framework Preset** to **Other**.
4. Under **Environment Variables**, add `GEMINI_API_KEY` and `MODEL`.
5. Click **Deploy**.
6. Open `https://your-link.vercel.app/api/health` to confirm it shows `{"status":"ok"}`.

Every `git push` to the repository redeploys the app automatically.