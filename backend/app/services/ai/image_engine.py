import uuid
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
        # Chain: fastest free-first → slowest last
        # Pollinations  — unlimited free, no key, bare URL
        # StableHorde   — free crowdsourced GPUs, 512px for anonymous
        # HuggingFace   — free hosted API (SD 1.5), classic endpoint
        # GeminiImage   — last resort, limited free quota
        self.providers = [
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
