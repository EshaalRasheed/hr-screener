"""The screening logic: score one CV against a job description."""
from pydantic import BaseModel, Field

from app.llm import generate_structured

SCREEN_PROMPT = """
You are a fair, careful HR screening assistant.
Compare the candidate's CV with the job description and score the match from 1 to 10:
- 9-10: meets all must-have requirements and most nice-to-haves
- 7-8: meets all must-have requirements
- 5-6: meets some must-haves; worth a closer look
- 1-4: poor fit for this role

Fairness rules (very important):
- Judge ONLY skills, experience, education, and achievements relevant to the job.
- NEVER consider or mention age, gender, religion, ethnicity, nationality, caste,
  marital status, disability, photos, or appearance.
- If the CV is empty, unreadable, or not a CV, give score 1 and say so in the summary.

Keep strengths, gaps, and summary short (one sentence each) and specific to the job.
"""


class Screening(BaseModel):
    """What the AI returns for one candidate."""
    candidate_name: str = Field(description="Candidate's name from the CV, or 'Unknown'")
    score: int = Field(description="Match score from 1 (poor) to 10 (excellent)")
    strengths: str = Field(description="Key strengths for this job, one sentence")
    gaps: str = Field(description="Main missing requirements, one sentence")
    summary: str = Field(description="One-sentence overall assessment")


def recommendation_for(score: int) -> str:
    """Decide the recommendation in code (not by the AI), so it's always consistent."""
    if score >= 7:
        return "Interview"
    if score >= 5:
        return "Maybe"
    return "Reject"


def screen_candidate(job_description: str, cv_text: str = "", file_bytes=None, file_mime=None) -> dict:
    """Score one candidate. The CV comes either as text or as a file (PDF)."""
    user_text = f"JOB DESCRIPTION:\n{job_description}\n\n"
    user_text += f"CANDIDATE CV:\n{cv_text}" if cv_text else "CANDIDATE CV: see the attached file."

    result = generate_structured(SCREEN_PROMPT, user_text, Screening, file_bytes, file_mime)

    score = max(1, min(10, int(result.score)))  # keep the score inside 1-10, just in case
    return {
        "candidate_name": result.candidate_name or "Unknown",
        "score": score,
        "recommendation": recommendation_for(score),
        "strengths": result.strengths,
        "gaps": result.gaps,
        "summary": result.summary,
    }