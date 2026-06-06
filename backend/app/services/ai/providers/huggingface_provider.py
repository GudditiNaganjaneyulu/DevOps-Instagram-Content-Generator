import httpx
from app.config import get_settings
from app.core.exceptions import ProviderRateLimitError, ProviderError
from app.core.logging import get_logger

logger = get_logger(__name__)

# Classic Hosted Inference API — free tier, no "Inference Providers" permission needed
# SD 1.5 is reliably available on the free tier
HF_API_URL = "https://api-inference.huggingface.co/models/runwayml/stable-diffusion-v1-5"


class HuggingFaceProvider:
    name = "huggingface"

    async def generate(self, prompt: str, width: int = 512, height: int = 512) -> bytes:
        settings = get_settings()
        if not settings.huggingface_api_key:
            raise ProviderError(self.name, "API key not configured")
        try:
            async with httpx.AsyncClient(timeout=120) as client:
                resp = await client.post(
                    HF_API_URL,
                    headers={"Authorization": f"Bearer {settings.huggingface_api_key}"},
                    json={"inputs": prompt},
                )
                if resp.status_code == 429:
                    raise ProviderRateLimitError(self.name)
                if resp.status_code == 503:
                    raise ProviderError(self.name, "Model loading, retry later")
                if resp.status_code != 200:
                    raise ProviderError(self.name, f"HTTP {resp.status_code}: {resp.text[:200]}")
                logger.info("HuggingFace image generated", bytes=len(resp.content))
                return resp.content
        except (ProviderRateLimitError, ProviderError):
            raise
        except Exception as e:
            raise ProviderError(self.name, str(e))
