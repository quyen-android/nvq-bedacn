from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # DATABASE
    DATABASE_URL: str
 
    SECRET_KEY:str
    ALGORITHM:str

    ACCESS_TOKEN_EXPIRE_MINUTES:int
    REFRESH_TOKEN_EXPIRE_DAYS:int
    RESET_TOKEN_EXPIRE_MINUTES:int

    EMAIL_HOST: str
    EMAIL_PORT: int
    EMAIL_USER: str
    EMAIL_PASS: str

    UPLOAD_FOLDER: str
    MAX_FILE_SIZE: int

    class Config:
        env_file = ".env"

settings = Settings()