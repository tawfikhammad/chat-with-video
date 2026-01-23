from fastapi import FastAPI
from routes import base, data, rag
from utils.app_config import get_settings
from AI.VectorDB.VDBFactory import VDBFactory
from AI.LLM.LLMFactory import LLMProviderFactory
from AI.LLM.templates import TemplateParser
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

app = FastAPI()

@app.on_event("startup")
async def startup():
    settings = get_settings()

    postgres_conn = f"postgresql+asyncpg://{settings.POSTGRES_USERNAME}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_MAIN_DATABASE}"
    app.db_conn = create_async_engine(postgres_conn)
    app.db_client = sessionmaker(app.db_conn, class_=AsyncSession, expire_on_commit=False)

    llm_provider_factory = LLMProviderFactory(settings)
    vdb_provider_factory = VDBFactory(settings)

    # generation client
    app.generation_client = llm_provider_factory.create(provider=settings.GENERATION_BACKEND)
    app.generation_client.set_generation_model(model_id=settings.GENERATION_MODEL_ID)

    # embedding client
    app.embedding_client = llm_provider_factory.create(provider=settings.EMBEDDING_BACKEND)
    app.embedding_client.set_embedding_model(model_id=settings.EMBEDDING_MODEL_ID,
                                             embedding_size=settings.EMBEDDING_SIZE)
    
    # vector db client
    app.vectordb_client = vdb_provider_factory.create(provider=settings.VECTOR_DB_BACKEND)
    await app.vectordb_client.connect()

    app.template_parser = TemplateParser(
        language=settings.PRIMARY_LANG,
        default_language=settings.DEFAULT_LANG,
    )

@app.on_event("shutdown")
async def shutdown():
    app.db_conn.dispose()
    await app.vectordb_client.disconnect()

app.include_router(base.base_router)
app.include_router(data.data_router, tags=["Data"])
app.include_router(rag.rag_router, tags=["RAG"])
