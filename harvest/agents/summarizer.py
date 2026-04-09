from agno.agent import Agent
from ..models import get_gemini, get_grok
from harvest.config import ModelConfig

config = ModelConfig()


def load_instructions(filename: str) -> str:
    path = config.INSTRUCTIONS_DIR / filename
    return path.read_text()


def build_summarizer_agent() -> Agent:
    return Agent(
        name="Summarizer",
        model=get_gemini(),
        instructions=load_instructions("summarizer.md"),
        markdown=True
    )
