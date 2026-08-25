from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    region: str = "ap-southeast-2"

    # The au.* inference-profile prefix is required; bare model IDs are rejected
    # in ap-southeast-2 because on-demand throughput is unavailable there.
    orchestrator_model_id: str = "au.anthropic.claude-sonnet-4-5-20250929-v1:0"
    specialist_model_id: str = "au.anthropic.claude-haiku-4-5-20251001-v1:0"


settings = Settings()
