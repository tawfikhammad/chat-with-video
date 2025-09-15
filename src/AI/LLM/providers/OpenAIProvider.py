from openai import OpenAI
from ..LLMInterface import LLMInterface
from ..LLMEnums import OpenAIEnums
from utils import logging


class OpenAIProvider(LLMInterface):
    def __init__(self, api_key: str,
                default_max_input_characters: int = 1000, 
                default_max_output_tokens: int=1000,
                default_temperature: float = 0.5):
        
        self.api_key = api_key
        self.client = OpenAI(api_key=api_key)

        self.default_max_input_characters = default_max_input_characters
        self.default_max_output_tokens = default_max_output_tokens
        self.default_temperature = default_temperature

        self.generation_model_id = None
        self.embedding_model_id = None
        self.embedding_size = None

        self.enums = OpenAIEnums
        self.logger = logging.get_logger(__name__)

    def set_generation_model(self, generation_model_id: str):
        self.generation_model_id = generation_model_id

    def set_embedding_model(self, embedding_model_id: str, embedding_size: int):
        self.embedding_model_id = embedding_model_id
        self.embedding_size = embedding_size

    async def process_text(self, text: str):
        return text[:self.default_max_input_characters].strip()

    async def generate(self, user_prompt: str, system_prompt: str, max_output_tokens: int = None, temperature: float = None):

        if self.generation_model_id is None:
            self.logger.error("Generation model ID is not set.")
            return None

        if self.client is None:
            self.logger.error("OpenAI client is not initialized.")
            return None
        
        try: 
            messages = [
                await self.construct_prompt(
                    prompt=system_prompt,
                    role=self.enums.SYSTEM.value
                ),
                await self.construct_prompt(
                    prompt=user_prompt,
                    role=self.enums.USER.value
                )
            ]
        
            response = self.client.chat.completions.create(
                model= self.generation_model_id,
                messages= messages,
                max_tokens= max_output_tokens or self.default_max_output_tokens,
                temperature= temperature or self.default_temperature,
            )

            if not response or not response.choices or len(response.choices) == 0 or not response.choices[0].message:
                self.logger.error("Error while generating text with OpenAI")
                return None
            
            return response.choices[0].message.content 
        
        except Exception as e:
            self.logger.error(f"Error in chat completion with OpenAI: {str(e)}")
            return None

    async def embed(self, text: str, document_type: str = None):
        if self.embedding_model_id is None:
            self.logger.error("Embedding model ID is not set.")
            return None

        if self.client is None:
            self.logger.error("OpenAI client is not initialized.")
            return None
        try: 
            response = self.client.embeddings.create(
                input=text,
                model=self.embedding_model_id,
                dimensions=self.embedding_size
            )

            if not response or not response.data or len(response.data) == 0 or not response.data[0].embedding:
                self.logger.error("Error while embedding text with OpenAI")
                return None
            
            return response.data[0].embedding
        
        except Exception as e:
            self.logger.error(f"Error embedding text with OpenAI: {str(e)}")
            return None

    async def construct_prompt(self, prompt: str, role: str):
        return [{
            "role": role,
            "content": prompt
        }]