from abc import ABC, abstractmethod

class LLMInterface(ABC):

    @abstractmethod
    def set_genration_model(self, genration_model_id: str ):
        pass

    @abstractmethod
    def set_embedding_model(self, embedding_model_id: str, embedding_size: int):
        pass

    @abstractmethod
    async def process_text(self, text: str):
        pass

    @abstractmethod
    async def generate(self, user_prompt: str, system_prompt: str, max_output_tokens: int=None,
                            temperature: float = None):
        pass

    @abstractmethod
    async def embed(self, text: str, document_type: str = None):
        pass

    @abstractmethod
    async def construct_prompt(self, prompt: str, role: str):
        pass
