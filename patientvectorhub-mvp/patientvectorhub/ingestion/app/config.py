from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+psycopg2://pvh:pvh_local_pw@localhost:5432/patientvectorhub"
    qdrant_url: str = "http://localhost:6333"
    qdrant_collection: str = "patient_documents"

    embedding_provider: str = "huggingface"  # "huggingface" | "openai"
    embedding_model: str = "emilyalsentzer/Bio_ClinicalBERT"
    openai_api_key: str = ""
    openai_embedding_model: str = "text-embedding-3-small"

    chunk_size_tokens: int = 256
    chunk_overlap_tokens: int = 32


settings = Settings()
