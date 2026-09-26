"""
Central settings for the API Gateway.

MVP note: auth is a single shared-secret bearer token (see auth.py), not
Keycloak. Swap this module + auth.py when Keycloak is reintroduced in
Phase 2 - nothing else in the gateway should need to change since routes
depend on `get_current_tenant`, not on the auth mechanism directly.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+psycopg2://pvh:pvh_local_pw@localhost:5432/patientvectorhub"
    api_shared_secret: str = "change-me-local-dev-secret"

    ingestion_url: str = "http://localhost:8001"
    rag_engine_url: str = "http://localhost:8002"

    cors_origins: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]


settings = Settings()
