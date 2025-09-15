from fastapi import FastAPI
import uvicorn
from routes import base, data, vdb, rag
from motor.motor_asyncio import AsyncIOMotorClient
from utils.app_config import get_settings
from AI.VectorDB.VDBFactory import VDBFactory
from AI.LLM.LLMFactory import LLMProviderFactory
from AI.LLM.templates import TemplateParser

app = FastAPI()

@app.on_event("startup")
async def startup():
    settings = get_settings()
    app.mongodb_conn = AsyncIOMotorClient(settings.MONGO_URL)
    app.mongodb_client = app.mongodb_conn[settings.MONGO_DB]

    llm_provider_factory = LLMProviderFactory(settings)
    vdb_provider_factory = VDBFactory(settings)

    # generation client
    app.generation_client = llm_provider_factory.create(provider=settings.GENERATION_BACKEND)
    app.generation_client.set_generation_model(model_id = settings.GENERATION_MODEL_ID)

    # embedding client
    app.embedding_client = llm_provider_factory.create(provider=settings.EMBEDDING_BACKEND)
    app.embedding_client.set_embedding_model(model_id=settings.EMBEDDING_MODEL_ID,
                                             embedding_size=settings.EMBEDDING_SIZE)
    
    # vector db client
    app.vectordb_client = vdb_provider_factory.create(provider=settings.VECTOR_DB_BACKEND)
    app.vectordb_client.connect()

    app.template_parser = TemplateParser(
        language=settings.PRIMARY_LANG,
        default_language=settings.DEFAULT_LANG,
    )

@app.on_event("shutdown")
async def shutdown():
    app.mongodb_conn.close()
    app.vectordb_client.disconnect()

app.include_router(base.base_router)
app.include_router(data.data_router, prefix="/data", tags=["Data"])
app.include_router(vdb.vdb_router, prefix="/{video_id}", tags=["VectorDB"])
app.include_router(rag.rag_router, prefix="/{video_id}", tags=["RAG"])



if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)