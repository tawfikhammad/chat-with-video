from .base_controller import BaseController
from models.db_schemas import Video, Chunk
from AI.LLM.LLMEnums import DocumentTypeEnum
from typing import List
import json
from utils import logging
logger = logging.get_logger(__name__)

class RAGController(BaseController):

    def __init__(self, vectordb_client, generation_client, 
                 embedding_client, template_parser):
        super().__init__()

        self.vectordb_client = vectordb_client
        self.generation_client = generation_client
        self.embedding_client = embedding_client
        self.template_parser = template_parser

    def create_collection_name(self, video_id: str):
        return f"collection_{video_id}".strip()
    
    async def reset_vdb_collection(self, video_id: str):
        collection_name = self.create_collection_name(video_id=video_id)
        return await self.vectordb_client.delete_collection(collection_name=collection_name)
    
    async def create_vdb_collection(self, video_id: str, embedding_size: int, do_reset: bool = False):
        collection_name = self.create_collection_name(video_id=video_id)
        return await self.vectordb_client.create_collection(
            collection_name=collection_name,
            embedding_size=embedding_size,
            do_reset=do_reset,
        )

    async def get_vdb_collection_info(self, video_id: str):
        collection_name = self.create_collection_name(video_id=video_id)
        collection_info = await self.vectordb_client.get_collection_info(collection_name=collection_name)
        return json.loads(json.dumps(collection_info, default=lambda x: x.__dict__))
    
    async def index_into_vdb_collection(
            self,
            chunks: List[Chunk],
            collection_name: str,
    ):
        try:
            texts = [c.chunk_text for c in chunks]
            vectors = [
                await self.embedding_client.embed(text=text, document_type=DocumentTypeEnum.DOCUMENT.value)
                for text in texts
            ]

            if not vectors or len(vectors) == 0:
                logger.error(f"Error generating some embedding vectors for chunks")
                raise

            logger.info(f"Generated {len(vectors)} embedding vectors for {len(texts)} chunks")

            # insert into vector db
            await self.vectordb_client.insert_many(
                collection_name=collection_name,
                texts=texts,
                vectors=vectors,
                mongodb_ids=[str(c.id) for c in chunks]
            )
            logger.info(f"Inserted {len(texts)} items into vector DB collection: {collection_name}")
        
        except Exception as e:
            logger.error(f"Error indexing into vector DB: {e}")
            raise

    async def search_query(self, video: Video, query: str, limit: int = 5):

        try: 
            collection_name = self.create_collection_name(video_id=video.video_id)

            # get text embedding vector
            vector = await self.embedding_client.embed(
                text=query,
                document_type=DocumentTypeEnum.QUERY.value)

            if not vector or len(vector) == 0:
                logger.error(f"Error generating embedding vector for query: {query}")
                raise

            # do semantic search
            results = await self.vectordb_client.search(
                collection_name=collection_name,
                query_vector=vector,
                limit=limit
            )

            return results
        
        except Exception as e:
            logger.error(f"Error searching vector DB: {e}")
            raise
    
    async def answer_question(self, video: Video, query: str, limit: int = 5):
        
        try:
            answer, full_prompt = None, None

            # retrieve related documents
            retrieved_documents = await self.search_query(
                video=video,
                query=query,
                limit=limit
            )

            if not retrieved_documents or len(retrieved_documents) == 0:
                return answer, full_prompt
            
            # Construct LLM prompt
            system_prompt = self.template_parser.get("rag", "system_prompt")

            documents_prompts = "\n".join([
                self.template_parser.get("rag", "document_prompt", {
                    "doc_num": idx + 1,
                    "chunk_text": doc.text,
                })
                for idx, doc in enumerate(retrieved_documents)
            ])

            footer_prompt = self.template_parser.get("rag", "footer_prompt", {
                "title": video.title,
                "author": video.author,
                "query": query,
            })

            full_prompt = "\n\n".join([documents_prompts,  footer_prompt])

            # Retrieve the Answer
            answer = await self.generation_client.generate(
                user_prompt=full_prompt,
                system_prompt=system_prompt
            )

            return answer, full_prompt

        except Exception as e:
            logger.error(f"Error answering RAG question: {e}")
            raise