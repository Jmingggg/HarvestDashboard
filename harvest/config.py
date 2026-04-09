import os
from pathlib import Path

BASE_DIR = Path(__file__).parent

class Config:
    GOOGLE_API_KEY: str = os.environ.get("API_KEY", "")
    MODEL_ID: str = "gemini-2.5-flash"
    INSTRUCTIONS_DIR: Path = BASE_DIR / "instructions"

config = Config()
