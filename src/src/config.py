from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import computed_field

class Settings(BaseSettings):
    
    # .env
    ragdb_name: str
    ragdb_user: str
    ragdb_password: str
    ragdb_host: str
    ragdb_port: str
    openai_api_key: str
    redis_url: str
       
    embedding_api_url: str = "http://embeddings:80"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"  
        )
    
    retriever_k:int = 4
    
    @computed_field
    @property
    def ragdb_url(self) -> str:
        return(
            f"postgresql+psycopg://{self.ragdb_user}:{self.ragdb_password}@{self.ragdb_host}:{self.ragdb_port}/{self.ragdb_name}"
        )

settings = Settings()