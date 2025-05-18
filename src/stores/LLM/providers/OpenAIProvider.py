from openai import OpenAI
from ..LLMInterface import LLMInterface
from ..LLMEnums import OpenAIEnums
import logging


class OpenAIProvider(LLMInterface):
    def __init__(self, api_key: str,
                base_url: str = None,
                default_max_output_tokens: int = 1000, 
                default_max_input_characters: int=1000,
                temperature: float = 0.5):
        
        self.api_key = api_key
        self.base_url = base_url
        self.client = OpenAI(api_key=api_key, api_base=base_url)

        self.default_max_output_tokens = default_max_output_tokens
        self.default_max_input_characters = default_max_input_characters
        self.temperature = temperature

        self.genration_model_id = None
        self.embedding_model_id = None
        self.embedding_size = None

        self.enums = OpenAIEnums

        self.logger = logging.getLogger(__name__)


    def set_genration_model(self, generation_model_id: str):
        self.generation_model_id = generation_model_id

    def set_embedding_model(self, embedding_model_id: str, embedding_size: int):
        self.embedding_model_id = embedding_model_id
        self.embedding_size = embedding_size

    def process_text(self, text: str):
        return text[:self.default_max_input_characters].strip()
    
    def generate(self, prompt: str,chat_history: list = [], max_output_tokens: int = None, temperature: float = None):

        if self.genration_model_id is None:
            self.logger.error("Generation model ID is not set.")
            return None

        if self.client is None:
            self.logger.error("OpenAI client is not initialized.")
            return None
        
        temperature = temperature if temperature else self.temperature
        max_output_tokens = max_output_tokens if max_output_tokens else self.default_max_output_tokens
        chat_history.append(self.construct_prompt(prompt, OpenAIEnums.USER.value))

        response = self.client.chat.completions.create(
            model= self.genration_model_id,
            messages= chat_history,
            max_tokens= max_output_tokens,
            temperature= temperature
        )

        if not response or not response.choices or len(response.choices) == 0 or not response.choices[0].message:
            self.logger.error("Error while generating text with OpenAI")
            return None
        
        return response.choices[0].message.content 


    def embed(self, text: str, embedding_size: int = None):
        if self.embedding_model_id is None:
            self.logger.error("Embedding model ID is not set.")
            return None

        if self.client is None:
            self.logger.error("OpenAI client is not initialized.")
            return None
        
        response = self.client.embeddings.create(
            input=text,
            model=self.embedding_model_id,
            )
        
        if not response or not response.data or len(response.data) == 0 or not response.data[0].embedding:
            self.logger.error("Error while embedding text with OpenAI")
            return None
        
        return response.data[0].embedding
    

    def construct_prompt(self, prompt: str, role: str):
        return [{
            "role": role,
            "content": prompt
        }]