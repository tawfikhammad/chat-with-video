from utils.app_config import get_settings, settings
from utils.logging import get_logger
import os

class BaseController:
    def __init__(self):
        self.app_settings = get_settings()
