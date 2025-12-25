from pydantic import PostgresDsn
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_MINUTES: int
    

    SERVER_NAME: str
    SERVER_HOST: str

    PROJECT_NAME: str

    POSTGRES_SERVER: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    SQLALCHEMY_DATABASE_URI: str | None = None
    
    CELERY_BROKER_URL: str
    CELERY_RESULT_BACKEND: str
    
    RABBITMQ_DEFAULT_USER: str
    
    

    model_config = {
        "env_file": ".env",
        "case_sensitive": True,
         "extra":"allow" 
    }


settings = Settings()
