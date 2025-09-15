
from .LLMEnums import LLMModel
from .providers import OpenAIProvider, CoHereProvider, GeminiProvider
from utils.app_enums import ResponseSignals

class LLMProviderFactory:
    def __init__(self, config: dict):
        self.config = config

    def create(self, provider: str):
        if provider == LLMModel.OPENAI.value:
            return OpenAIProvider(
                api_key = self.config.OPENAI_API_KEY,
                default_max_input_characters=self.config.DEFAULT_MAX_INPUT_CHARACTERS,
                default_max_output_tokens=self.config.DEFAULT_MAX_TOKENS,
                default_temperature=self.config.DEFAULT_TEMPERATURE
            )

        if provider == LLMModel.COHERE.value:
            return CoHereProvider(
                api_key = self.config.COHERE_API_KEY,
                default_max_input_characters=self.config.DEFAULT_MAX_INPUT_CHARACTERS,
                default_max_output_tokens=self.config.DEFAULT_MAX_TOKENS,
                default_temperature=self.config.DEFAULT_TEMPERATURE
            )
        
        if provider == LLMModel.GEMINI.value:
            return GeminiProvider(
                api_key=self.config.GEMINI_API_KEY,
                default_max_input_characters=self.config.DEFAULT_MAX_INPUT_CHARACTERS,
                default_max_output_tokens=self.config.DEFAULT_MAX_TOKENS,
                default_temperature=self.config.DEFAULT_TEMPERATURE
            )

        else:
            raise ValueError(ResponseSignals.UNSUPPORTED_LLM_PROVIDER.value)