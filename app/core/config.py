from pydantic_settings import BaseSettings
from pydantic import PostgresDsn
import os
from dotenv import load_dotenv

load_dotenv()  
class Settings(BaseSettings):
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY")
    QDRANT_HOST: str = os.getenv("QDRANT_HOST")
    QDRANT_API_KEY: str = os.getenv("QDRANT_API_KEY")




settings = Settings()