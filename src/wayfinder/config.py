from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    region: str = "ap-southeast-2"

    orchestrator_model_id: str = "au.anthropic.claude-sonnet-4-5-20250929-v1:0"
    specialist_model_id: str = "au.anthropic.claude-haiku-4-5-20251001-v1:0"

    # AgentCore Memory resource; empty disables memory entirely.
    memory_id: str = ""

    user_agent: str = "wayfinder-dev/0.1 (+https://github.com/Krish-Parekh/wayfinder)"

    mcp_host: str = "127.0.0.1"
    mcp_port: int = 8000

    # Bind address for the A2A servers; 0.0.0.0 in a container.
    a2a_host: str = "127.0.0.1"
    route_planner_port: int = 9001
    places_researcher_port: int = 9002
    food_scout_port: int = 9003

    # Where the orchestrator finds each specialist. Defaults assume the
    # laptop fleet; in-cluster these become Service DNS names.
    route_planner_url: str = "http://127.0.0.1:9001"
    places_researcher_url: str = "http://127.0.0.1:9002"
    food_scout_url: str = "http://127.0.0.1:9003"

    @property
    def mcp_url(self) -> str:
        return f"http://{self.mcp_host}:{self.mcp_port}/mcp"


settings = Settings()
