
import os
from dotenv import load_dotenv

load_dotenv()

APP_NAME = os.getenv("APP_NAME", "LLM Gateway")
APP_HOST = os.getenv("APP_HOST", "127.0.0.1")
APP_PORT = int(os.getenv("APP_PORT", 8002))
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openrouter")

LLM_MODEL = os.getenv(
    "LLM_MODEL",
    "nvidia/nemotron-3.5-super-vl:free"
)

OPENROUTER_BASE_URL = os.getenv(
    "OPENROUTER_BASE_URL",
    "https://openrouter.ai/api/v1"
)

OPENROUTER_MODELS_URL = (
    "https://openrouter.ai/api/v1/models"
)

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

LLM_TEMPERATURE = float(
    os.getenv("LLM_TEMPERATURE", 0.7)
)

LLM_MAX_TOKENS = int(
    os.getenv("LLM_MAX_TOKENS", 2048)
)

LLM_TIMEOUT = int(
    os.getenv("LLM_TIMEOUT", 60)
)

MODEL_CACHE_SECONDS = int(
    os.getenv("MODEL_CACHE_SECONDS", 300)
)

if not OPENROUTER_API_KEY:
    raise ValueError(
        "OPENROUTER_API_KEY is missing in .env"
    )

if LLM_PROVIDER.lower() != "openrouter":
    raise ValueError(
        "Currently only OpenRouter is supported"
    )
