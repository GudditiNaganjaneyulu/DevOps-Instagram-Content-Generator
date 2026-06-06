import uuid
from app.services.ai.providers.text_card_provider import TextCardProvider
from app.services.ai.providers.pollinations_provider import PollinationsProvider
from app.services.ai.providers.together_provider import StableHordeProvider
from app.services.ai.providers.huggingface_provider import HuggingFaceProvider
from app.services.ai.providers.gemini_image_provider import GeminiImageProvider
from app.core.cloudinary_client import upload_image_bytes
from app.core.exceptions import ProviderRateLimitError, ProviderError, AllProvidersExhaustedError
from app.core.logging import get_logger

logger = get_logger(__name__)


class ImageGenerationEngine:
    def __init__(self):
        # TextCard is always first — renders @runtimeemotions style cards via Pillow,
        # no API key, instant, always works. AI providers are fallbacks only.
        self.providers = [
            TextCardProvider(),
            PollinationsProvider(),
            StableHordeProvider(),
            HuggingFaceProvider(),
            GeminiImageProvider(),
        ]

    async def generate_and_store(self, prompt: str, folder: str = "devops-emotions") -> dict:
        image_bytes: bytes | None = None
        provider_used: str = ""

        for provider in self.providers:
            try:
                image_bytes = await provider.generate(prompt)
                provider_used = provider.name
                break
            except (ProviderRateLimitError, ProviderError) as e:
                logger.warning("Image provider failed", provider=provider.name, error=str(e))
                continue

        if not image_bytes:
            raise AllProvidersExhaustedError()

        public_id = f"{folder}/{uuid.uuid4().hex}"
        storage_result = await upload_image_bytes(image_bytes, public_id, folder)
        storage_result["provider_used"] = provider_used
        return storage_result
