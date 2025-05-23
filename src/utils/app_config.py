from pydantic_settings import BaseSettings

class settings(BaseSettings):

    APP_NAME: str 
    APP_VERSION: str 
    YOUTUBE_API: str
    MONGO_URL: str
    MONGO_DB: str = "vidbot"

    GENERATION_BACKEND : str
    EMBEDDING_BACKEND : str

    OPENAI_API_KEY: str
    OPENAI_API_URL: str
    COHERE_API_KEY: str
    GEMINI_API_KEY: str

    GENERATION_MODEL_ID: str
    EMBEDDING_MODEL_ID: str
    EMBEDDING_MODEL_SIZE: int 

    INPUT_DAFAULT_MAX_CHARACTERS: int
    GENERATION_DAFAULT_MAX_TOKENS: int
    GENERATION_DAFAULT_TEMPERATURE: int

    VECTOR_DB_BACKEND : str
    VECTOR_DB_PATH : str
    VECTOR_DB_DISTANCE_METHOD : str

    PRIMARY_LANG : str = "en"
    DEFAULT_LANG : str = "en"

    class Config:
        env_file= "src/.env"

def get_settings() -> settings:
    return settings()
