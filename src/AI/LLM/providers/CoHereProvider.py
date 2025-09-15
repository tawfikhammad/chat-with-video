from ..LLMInterface import LLMInterface
from ..LLMEnums import CoHereEnums, DocumentTypeEnum
import cohere
from utils import logging

class CoHereProvider(LLMInterface):

    def __init__(self, api_key: str,
                       default_max_input_characters: int=1000,
                       default_max_output_tokens: int=1000,
                       default_temperature: float=0.1):

        self.api_key = api_key
        self.client = cohere.Client(api_key=self.api_key)

        self.default_max_input_characters = default_max_input_characters
        self.default_max_output_tokens = default_max_output_tokens
        self.default_temperature = default_temperature

        self.generation_model_id = None
        self.embedding_model_id = None
        self.embedding_size = None

        self.enums = CoHereEnums
        self.logger = logging.get_logger(__name__)

    def set_generation_model(self, model_id: str):
        self.generation_model_id = model_id

    def set_embedding_model(self, model_id: str, embedding_size: int):
        self.embedding_model_id = model_id
        self.embedding_size = embedding_size

    async def process_text(self, text: str):
        return text[:self.default_max_input_characters].strip()

    async def generate(self, user_prompt: str, system_prompt: str, max_output_tokens: int=None,
                            temperature: float = None):

        if not self.client:
            self.logger.error("CoHere client was not set")
            return None

        if not self.generation_model_id:
            self.logger.error("Generation model for CoHere was not set")
            return None
        try:
            chat_history = [await self.construct_prompt(
                prompt=system_prompt,
                role=self.enums.SYSTEM.value
            )]
            response = self.client.chat(
                model=self.generation_model_id,
                chat_history=chat_history,
                message=await self.process_text(user_prompt),
                temperature=temperature or self.default_temperature,
                max_tokens=max_output_tokens or self.default_max_output_tokens,
            )

            if not response or not response.text:
                self.logger.error("Error while generating text with CoHere")
                return None

            return response.text
        
        except Exception as e:
            self.logger.error(f"Error in chat completion with CoHere: {str(e)}")
            return None

    async def embed(self, text: str, document_type: str = None):
        if not self.client:
            self.logger.error("CoHere client was not set")
            return None
        
        if not self.embedding_model_id:
            self.logger.error("Embedding model for CoHere was not set")
            return None
        
        try: 
            input_type = CoHereEnums.DOCUMENT
            if document_type == DocumentTypeEnum.QUERY:
                input_type = CoHereEnums.QUERY

            response = self.client.embed(
                model = self.embedding_model_id,
                texts = [self.process_text(text)],
                input_type = input_type,
                embedding_types=['float'],
            )

            if not response or not response.embeddings or not response.embeddings.float:
                self.logger.error("Error while embedding text with CoHere")
                return None
            
            return response.embeddings.float[0]
        
        except Exception as e:
            self.logger.error(f"Error embedding text with CoHere: {str(e)}")
            return None
    
    async def construct_prompt(self, prompt: str, role: str):
        return {
            "role": role,
            "text": self.process_text(prompt)
        }