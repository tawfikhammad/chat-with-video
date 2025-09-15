from .base_controller import BaseController
from models.db_schemas import Video, Chunk
from AI.LLM.LLMEnums import DocumentTypeEnum
from typing import List
import json


class RAGController(BaseController):

    def __init__(self, vectordb_client, generation_client, 
                 embedding_client, template_parser):
        super().__init__()

        self.vectordb_client = vectordb_client
        self.generation_client = generation_client
        self.embedding_client = embedding_client
        self.template_parser = template_parser

    async def create_collection_name(self, video_id: str):
        return f"collection_{video_id}".strip()
    
    async def reset_vector_db_collection(self, video: Video):
        collection_name = await self.create_collection_name(video_id=video.video_id)
        return await self.vectordb_client.delete_collection(collection_name=collection_name)

    async def get_vector_db_collection_info(self, video: Video):
        collection_name = await self.create_collection_name(video_id=video.video_id)
        collection_info = await self.vectordb_client.get_collection_info(collection_name=collection_name)

        return json.loads(json.dumps(collection_info, default=lambda x: x.__dict__))
    
    async def index_into_vector_db(self, video: Video, chunks: List[Chunk],
                                   chunks_ids: List[int], 
                                   do_reset: bool = False):
        try:
            # step1: get collection name
            collection_name = await self.create_collection_name(video_id=video.video_id)

            # step2: manage items
            texts = [c.chunk_text for c in chunks]
            vectors = [
                await self.embedding_client.embed(text=text, document_type=DocumentTypeEnum.DOCUMENT.value)
                for text in texts
            ]

            if len(vectors) != len(texts):
                self.logger.error(f"Error generating embedding vectors for chunks")
                return False
            
            if not all(vectors):
                self.logger.error(f"Error generating some embedding vectors for chunks")
                return False
            
            self.logger.info(f"Generated {len(vectors)} embedding vectors for {len(texts)} chunks")

            # step3: create collection if not exists
            _ = await self.vectordb_client.create_collection(
                collection_name=collection_name,
                embedding_size=self.embedding_client.embedding_size,
                do_reset=do_reset,
            )

            # step4: insert into vector db
            _ = await self.vectordb_client.insert_many(
                collection_name=collection_name,
                texts=texts,
                vectors=vectors,
                record_ids=chunks_ids,
            )

            self.logger.info(f"Inserted {len(texts)} items into vector DB collection: {collection_name}")
            return True
        
        except Exception as e:
            self.logger.error(f"Error indexing into vector DB: {e}")
            return False

    async def search_vector_db_collection(self, video: Video, text: str, limit: int = 5):

        try: 
            collection_name = await self.create_collection_name(video_id=video.video_id)

            # get text embedding vector
            vector = await self.embedding_client.embed(
                text=text,
                document_type=DocumentTypeEnum.QUERY.value)

            if not vector or len(vector) == 0:
                self.logger.error(f"Error generating embedding vector for text: {text}")
                return None

            # do semantic search
            results = await self.vectordb_client.search(
                collection_name=collection_name,
                vector=vector,
                limit=limit)

            if not results:
                self.logger.error(f"No results found for vector DB search")
                return None

            self.logger.info(f"Found {len(results)} results from vector DB search")
            return results
        
        except Exception as e:
            self.logger.error(f"Error searching vector DB: {e}")
            return None
    
    async def answer_rag_question(self, video: Video, query: str, limit: int = 5):
        
        try:
            answer, full_prompt = None, None

            # retrieve related documents
            retrieved_documents = await self.search_vector_db_collection(
                video=video,
                text=query,
                limit=limit,)

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
            self.logger.error(f"Error answering RAG question: {e}")
            return None, None