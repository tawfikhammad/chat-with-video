from qdrant_client import QdrantClient
from qdrant_client.http import models
from ..VDBInterface import VDBInterface
from models.db_schemas import RetrievedDocument
import logging
from typing import List
import uuid

class QdrantProvider(VDBInterface):
    def __init__(self, db_path:str, distance_metric:str):
        self.db_path = db_path
        self.distance_metric = None
        self.client = None

        if distance_metric == "cosine":
            self.distance_metric = models.Distance.COSINE
        elif distance_metric == "dot":
            self.distance_metric = models.Distance.DOT

    def connect(self):
        self.client = QdrantClient(path=self.db_path)
        logging.info("Connected to Qdrant database.")

    def disconnect(self):
        if self.client:
            self.client.close()
            logging.info("Disconnected from Qdrant database.")

    def is_collection_exist(self, collection_name) -> bool:
        return self.client.collection_exists(collection_name)

    def list_all_collections(self) -> List: 
        return self.client.get_collections()
    
    def get_collection_info(self, collection_name):
        if self.client.collection_exists(collection_name):
            return self.client.get_collection(collection_name=collection_name)
        else:
            logging.warning(f"Collection '{collection_name}' does not exist.")
            return None
        
    def delete_collection(self, collection_name):
        if self.client.collection_exists(collection_name):
            self.client.delete_collection(collection_name=collection_name)
            logging.info(f"Collection '{collection_name}' deleted.")
        else:
            logging.warning(f"Collection '{collection_name}' does not exist.")

    def create_collection(self, collection_name: str, embedding_size: int, do_reset: bool = False):
        if do_reset:
            _ = self.delete_collection(collection_name)

        if not self.client.collection_exists(collection_name):
            _ = self.client.create_collection(
                collection_name=collection_name,
                vector_size= embedding_size,
                distance=self.distance_metric,
            )
            logging.info(f"Collection '{collection_name}' created.")
        else:
            logging.warning(f"Collection '{collection_name}' already exists.")
        
    def insert_one(self, collection_name:str, text:str, vector:list, record_id:int = None):
        
        if self.client.collection_exists(collection_name):
            try:
                self.client.upsert(
                    collection_name=collection_name,
                    points=[
                        models.PointStruct(
                        id= record_id,
                        vector= vector, 
                        payload= {"text": text}
                )])
                logging.info(f"Inserted one document into collection '{collection_name}'.")

            except Exception as e:
                logging.error(f"Error inserting document into collection '{collection_name}': {e}")
                return False
        else:
            logging.warning(f"Collection '{collection_name}' does not exist. Cannot insert document.")

    def insert_many(self, collection_name:str, texts:list, vectors:list,
                record_ids:list = None, batch_size:int = 50):
        
        if not self.client.collection_exists(collection_name):
            logging.error(f"Collection '{collection_name}' does not exist.")
            return False

        record_ids = record_ids or [str(uuid.uuid4()) for _ in range(len(texts))]
        try:
            for i in range(0, len(texts), batch_size):
                batch_points = []
                for j in range(i, min(i + batch_size, len(texts))):
                    payload = {"text": texts[j]}

                    point = models.PointStruct(
                        id=record_ids[j],
                        vector=vectors[j],
                        payload=payload)

                    batch_points.append(point)

                self.client.upsert(
                    collection_name=collection_name,
                    points=batch_points,
                    batch_size=batch_size
                )

                logging.info(f"Inserted batch {i} to {i + len(batch_points)} into collection '{collection_name}'")

            return True

        except Exception as e:
            logging.error(f"Error inserting into collection '{collection_name}': {e}")
            return False
        
    
    def search(self, collection_name:str, query_vector:list, limit:int = 5):
        try:
            search_result = self.client.search(
                collection_name=collection_name,
                query_vector=query_vector,
                limit=limit
            )

            if not search_result or len(search_result) == 0:
                logging.warning(f"No results found in collection '{collection_name}'.")
                return None

            retrieved_reselt = [
            RetrievedDocument(**{
                "score": result.score,
                "text": result.payload["text"],})
            for result in search_result]

            logging.info(f"Search completed in collection '{collection_name}'.")
            return retrieved_reselt

        except Exception as e:
            logging.error(f"Error searching in collection '{collection_name}': {e}")
            return None