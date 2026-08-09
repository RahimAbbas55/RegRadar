from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # LLM / embedding provider keys
    openai_api_key: str
    anthropic_api_key: str

    # Qdrant connection
    qdrant_host: str = "localhost"
    qdrant_port: int = 6333
    qdrant_collection_name: str = "regradar_fca"

    # App settings
    environment: str = "development"
    log_level: str = "INFO"

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)

# Single shared instance, imported wherever config is needed
settings = Settings()