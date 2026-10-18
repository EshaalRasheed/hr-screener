"""Small helper around the Gemini API that returns structured (typed) results."""
from google import genai
from google.genai import errors, types

from app import config

_client = genai.Client(api_key=config.GEMINI_API_KEY)  # one client, reused


class QuotaExceeded(Exception):
    """Raised when Gemini's free quota is used up (HTTP 429)."""


def generate_structured(system_prompt, user_text, schema, file_bytes=None, file_mime=None):
    """Ask Gemini for JSON matching `schema` (a Pydantic model) and return it as an object.

    If `file_bytes` is given (e.g. a PDF CV), Gemini reads the file directly,
    so we don't need a separate PDF-parsing library.
    """
    contents = [user_text]
    if file_bytes:
        contents.insert(0, types.Part.from_bytes(data=file_bytes, mime_type=file_mime))

    try:
        response = _client.models.generate_content(
            model=config.MODEL,
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                response_mime_type="application/json",  # JSON only
                response_schema=schema,                 # exact fields we expect
                temperature=0.2,                        # consistent, fair scoring
            ),
        )
    except errors.ClientError as error:
        if error.code == 429:
            raise QuotaExceeded() from error
        raise
    return response.parsed