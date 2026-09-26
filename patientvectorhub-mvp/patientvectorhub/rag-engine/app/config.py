from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    qdrant_url: str = "http://localhost:6333"
    qdrant_collection: str = "patient_documents"

    embedding_provider: str = "huggingface"
    embedding_model: str = "emilyalsentzer/Bio_ClinicalBERT"

    llm_provider: str = "ollama"  # "ollama" | "openai"
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.1:8b"

    openai_api_key: str = ""
    openai_chat_model: str = "gpt-4o-mini"
    openai_embedding_model: str = "text-embedding-3-small"

    default_top_k: int = 5


settings = Settings()
