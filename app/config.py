"""Settings, read from environment variables (.env on your PC, Vercel settings online)."""
import os

from dotenv import load_dotenv

load_dotenv()  # read .env when running locally; does nothing on Vercel

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
MODEL = os.getenv("MODEL", "gemini-3.8-flash")  # change in .env / Vercel if renamed