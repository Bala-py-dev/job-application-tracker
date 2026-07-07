from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "Job Application Tracker"
    database_url: str = "sqlite:///./jobtracker.db"
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    reminder_default_days: int = 7
    log_level: str = "INFO"


settings = Settings()
