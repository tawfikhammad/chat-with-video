from utils.app_config import get_settings, settings
from utils.logging import get_logger
logger = get_logger(__name__)
import os

class BaseController:
    def __init__(self):
        self.app_settings = get_settings()
        self.logger = logger
        self.base_dir = os.path.dirname( os.path.dirname(__file__) )
        self.database_dir = os.path.join(
            self.base_dir,
            "assets/database"
        )

    def get_vdb_path(self, db_name: str):

        database_path = os.path.join(
            self.database_dir, db_name
        )

        if not os.path.exists(database_path):
            os.makedirs(database_path)

        return database_path