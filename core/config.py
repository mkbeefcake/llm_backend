import os
from pathlib import Path

from dotenv import load_dotenv

env_path = Path(".") / ".env"
load_dotenv(dotenv_path=env_path)


class Settings:
    PROJECT_NAME: str = "Neo ChatBot"
    PROJECT_VERSION: str = "0.1.0"
    SECRET_KEY : str = os.getenv("SECRET_KEY")

settings = Settings()