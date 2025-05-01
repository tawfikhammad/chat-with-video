from utils.app_config import get_settings

class BaseModel:
    def __init__(self, db_client):
        self.db_client = db_client
        self.settings = get_settings()