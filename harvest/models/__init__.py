from agno.models.google import Gemini
from agno.models.xai import xAI
from config import config


def get_gemini() -> Gemini:
    return Gemini(
        id=config.MODEL_ID,
        name="Gemini",
        provider="Google",
        api_key=config.API_KEY,
    )


def get_grok() -> xAI:
    return xAI(
        id=config.MODEL_ID,
        name="Grok",
        provider="xAI",
        api_key=config.API_KEY,
    )
