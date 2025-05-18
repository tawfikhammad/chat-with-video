from .providers import QdrantProvider
from controllers import BaseController
from .VDBEnums import VectorDBType
from utils.app_enums import ResponseSignals

class VDBFactory:
    def __init__(self, config):
        self.config = config
        self.base_controller = BaseController()

    def create(self, provider: str):
        db_path = self.base_controller.get_vdb_path(provider)
        if provider == VectorDBType.QDRANT.value:
            return QdrantProvider(db_path, self.config.VECTOR_DB_DISTANCE_METHOD)
        
        else:
            raise ValueError(ResponseSignals.UNSUPPORTED_VDB_PROVIDER.value)
        