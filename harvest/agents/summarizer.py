from agno.agent import Agent
from harvest.models import get_gemini
from harvest.config import ModelConfig

config = ModelConfig()


def load_instructions(filename: str) -> str:
    path = config.INSTRUCTIONS_DIR / filename
    return path.read_text()


def build_summarizer_agent(api_key: str) -> Agent:
    return Agent(
        name="Summarizer",
        model=get_gemini(api_key=api_key),
        instructions=load_instructions("summarizer.md"),
        markdown=True
    )
