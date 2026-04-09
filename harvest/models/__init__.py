from agno.models.google import Gemini
from harvest.config.model import ModelConfig

config = ModelConfig()


def get_gemini(api_key: str) -> Gemini:
    return Gemini(
        id=config.MODEL_ID,
        name="Gemini",
        provider="Google",
        api_key=api_key,
    )
