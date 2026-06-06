from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from app.services.ai.providers.groq_provider import GroqProvider
from app.services.ai.providers.gemini_provider import GeminiProvider
from app.services.ai.providers.openrouter_provider import OpenRouterProvider
from app.services.ai.prompts.devops_prompts import (
    SYSTEM_PROMPT,
    build_meme_prompt,
    build_incident_prompt,
    build_trend_meme_prompt,
)
from app.core.exceptions import ProviderRateLimitError, ProviderError, AllProvidersExhaustedError
from app.core.logging import get_logger

logger = get_logger(__name__)


class TextGenerationEngine:
    def __init__(self):
        self.providers = [GroqProvider(), GeminiProvider(), OpenRouterProvider()]

    async def _try_providers(self, system: str, user: str) -> tuple[dict, str]:
        last_error = None
        for provider in self.providers:
            try:
                result = await provider.complete(system=system, user=user)
                logger.info("Text generation succeeded", provider=provider.name)
                return result, provider.name
            except (ProviderRateLimitError, ProviderError) as e:
                logger.warning("Provider failed, trying next", provider=provider.name, error=e.message)
                last_error = e
                continue
        raise AllProvidersExhaustedError()

    async def generate_meme(
        self,
        category: str,
        tone: str,
        context: str | None = None,
    ) -> tuple[dict, str]:
        user_prompt = build_meme_prompt(category, tone, context)
        return await self._try_providers(SYSTEM_PROMPT, user_prompt)

    async def generate_incident_content(self, error_type: str, raw_input: str) -> tuple[dict, str]:
        user_prompt = build_incident_prompt(error_type, raw_input)
        return await self._try_providers(SYSTEM_PROMPT, user_prompt)

    async def generate_trend_content(self, title: str, source: str, category: str) -> tuple[dict, str]:
        user_prompt = build_trend_meme_prompt(title, source, category)
        return await self._try_providers(SYSTEM_PROMPT, user_prompt)
