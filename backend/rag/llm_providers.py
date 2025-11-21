import logging
from abc import ABC, abstractmethod
from typing import Optional
import google.generativeai as genai
from groq import Groq

from config import settings

logger = logging.getLogger(__name__)


class LLMProvider(ABC):
    @abstractmethod
    def generate(self, prompt: str) -> str:
        pass


class GeminiProvider(LLMProvider):
    def __init__(self, model_name: Optional[str] = None):
        genai.configure(api_key=settings.google_api_key)
        self.model_name = model_name or settings.generation_model
        self.model = genai.GenerativeModel(self.model_name)
        logger.info(f"Initialized Gemini provider with model: {self.model_name}")

    def generate(self, prompt: str) -> str:
        try:
            response = self.model.generate_content(prompt)

            if not response or not response.parts:
                logger.error("Gemini returned empty response")
                if hasattr(response, "prompt_feedback"):
                    logger.error(f"Prompt feedback: {response.prompt_feedback}")
                raise ValueError("Empty response from Gemini")

            return response.text.strip()
        except Exception as e:
            logger.error(f"Error generating with Gemini: {e}", exc_info=True)
            raise


class GroqProvider(LLMProvider):
    def __init__(self, model_name: Optional[str] = None):
        if not settings.groq_api_key:
            raise ValueError("GROQ_API_KEY not configured")

        self.client = Groq(api_key=settings.groq_api_key)
        self.model_name = model_name or settings.groq_generation_model
        logger.info(f"Initialized Groq provider with model: {self.model_name}")

    def generate(self, prompt: str) -> str:
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=1024,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Error generating with Groq: {e}")
            raise


class LLMFactory:
    AVAILABLE_MODELS = {
        "gemini": ("gemini-2.5-flash", GeminiProvider),
        "gemini-2.5-flash": ("gemini-2.5-flash", GeminiProvider),
        "gemini-2.5-pro": ("gemini-2.5-pro", GeminiProvider),
        "groq-llama3": ("llama-3.1-8b-instant", GroqProvider),
        "groq-llama-8b": ("llama-3.1-8b-instant", GroqProvider),
        "groq-llama-70b": ("llama-3.1-70b-versatile", GroqProvider),
        "groq-mixtral": ("mixtral-8x7b-32768", GroqProvider),
    }

    @classmethod
    def create_provider(cls, model_key: Optional[str] = None) -> LLMProvider:
        if not model_key or model_key == "gemini":
            return GeminiProvider()

        if model_key not in cls.AVAILABLE_MODELS:
            logger.warning(f"Unknown model key '{model_key}', falling back to Gemini")
            return GeminiProvider()

        model_name, provider_class = cls.AVAILABLE_MODELS[model_key]

        try:
            return provider_class(model_name)
        except ValueError as e:
            logger.warning(
                f"Failed to initialize {provider_class.__name__}: {e}. Falling back to Gemini"
            )
            return GeminiProvider()

    @classmethod
    def get_available_models(cls):
        models = []
        for key in cls.AVAILABLE_MODELS.keys():
            models.append(key)
        return models
