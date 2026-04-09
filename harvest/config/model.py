import os
from pathlib import Path
from harvest.utils import load_env

load_env()

BASE_DIR = Path(__file__).parent.parent

class ModelConfig:
    # API_KEY: str = os.environ.get("API_KEY", "")
    MODEL_ID: str = os.environ.get("MODEL", "")
    INSTRUCTIONS_DIR: Path = BASE_DIR / "instructions"
