from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="STUDYFORGE_")

    db_path: str = "data/studyforge.db"
    ollama_url: str = "http://localhost:11434"
    llm_model: str = "qwen3:14b"
    embed_model: str = "nomic-embed-text"
    num_ctx: int = 32768
    request_delay_seconds: float = 3.0
    user_agent: str = "StudyForge/0.1 (personal study tool)"


def get_settings() -> Settings:
    return Settings()
