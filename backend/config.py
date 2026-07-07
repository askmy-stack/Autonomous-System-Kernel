
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Required
    openai_api_key: str

    # Model
    model_name: str = "gpt-4o-mini"
    temperature: float = 0.5

    # LangSmith observability (optional)
    langchain_tracing_v2: bool = False
    langchain_api_key: str | None = None
    langchain_project: str = "jarvis-chatbot"

    # Home Assistant smart home (optional)
    home_assistant_url: str | None = None
    home_assistant_token: str | None = None

    # Backend URL (consumed by Streamlit)
    backend_url: str = "http://localhost:8000"

    # Privacy and operations
    privacy_mode: str = "local_only"  # local_only | hybrid
    redact_pii: bool = True
    backup_dir: str = "./backups"


# Pydantic Settings loads OPENAI_API_KEY from the environment at runtime.
settings = Settings()  # type: ignore[call-arg]
