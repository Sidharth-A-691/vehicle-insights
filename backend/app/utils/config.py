from dotenv import load_dotenv
import os

load_dotenv()

class Settings:
    AZURE_OPENAI_ENDPOINT: str = os.getenv("AZURE_OPENAI_ENDPOINT")
    AZURE_OPENAI_API_KEY: str = os.getenv("AZURE_OPENAI_API_KEY")
    AZURE_OPENAI_API_VERSION: str = os.getenv("AZURE_OPENAI_API_VERSION")
    AZURE_OPENAI_DEPLOYMENT: str = os.getenv("AZURE_OPENAI_DEPLOYMENT")
    
    AZURE_OPENAI_EMBED_API_ENDPOINT: str = os.getenv("AZURE_OPENAI_EMBED_API_ENDPOINT")
    AZURE_OPENAI_EMBED_API_KEY: str = os.getenv("AZURE_OPENAI_EMBED_API_KEY")
    AZURE_OPENAI_EMBED_MODEL: str = os.getenv("AZURE_OPENAI_EMBED_MODEL")
    AZURE_OPENAI_EMBED_VERSION: str = os.getenv("AZURE_OPENAI_EMBED_VERSION")

    DATABASE_URL: str = os.getenv("DATABASE_URL")

settings = Settings()