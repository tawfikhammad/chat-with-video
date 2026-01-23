from pydantic_settings import BaseSettings

class settings(BaseSettings):

    APP_NAME: str 
    APP_VERSION: str 
    YOUTUBE_API: str

    GENERATION_BACKEND : str
    EMBEDDING_BACKEND : str

    OPENAI_API_KEY: str
    COHERE_API_KEY: str
    GEMINI_API_KEY: str

    GENERATION_MODEL_ID: str
    EMBEDDING_MODEL_ID: str
    EMBEDDING_SIZE: int 

    DEFAULT_MAX_INPUT_CHARACTERS: int
    DEFAULT_MAX_TOKENS: int
    DEFAULT_TEMPERATURE: float

    POSTGRES_USERNAME: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_MAIN_DATABASE: str

    PRIMARY_LANG : str = "en"
    DEFAULT_LANG : str = "en"

    class Config:
        env_file= "src/.env"

def get_settings() -> settings:
    return settings()
