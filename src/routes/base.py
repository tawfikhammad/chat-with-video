from fastapi import APIRouter, Depends
from utils.config import get_settings, settings

base_router = APIRouter()

@base_router.get("/welcome")
async def welcome(settings: settings = Depends(get_settings)):

    project_name = settings.APP_NAME
    version = settings.APP_VERSION
    
    return "Welcome to {project_name} API, version {version}".format(
        project_name=project_name,
        version=version
    )