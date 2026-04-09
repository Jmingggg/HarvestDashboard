from agno.models.google import Gemini
from config import config


def get_gemini() -> Gemini:
    return Gemini(
        id=config.MODEL_ID,
        name="Gemini",
        provider="Google",
        api_key=config.GOOGLE_API_KEY,
    )
