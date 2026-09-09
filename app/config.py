import os

class Settings:
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")
    MODEL_NAME: str = os.getenv("MODEL_NAME", "qwen3:8b")

settings = Settings()