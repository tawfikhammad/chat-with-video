from fastapi import FastAPI
import uvicorn
from routes import base, data
from motor.motor_asyncio import AsyncIOMotorClient
from utils.app_config import get_settings

app = FastAPI()

@app.on_event("startup")
async def startup():
    settings = get_settings()
    app.mongodb_conn = AsyncIOMotorClient(settings.MONGO_URL)
    app.mongodb_client = app.mongodb_conn[settings.MONGO_DB]

@app.on_event("shutdown")
async def shutdown():
    app.mongodb_conn.close()

app.include_router(base.base_router)
app.include_router(data.data_router)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)