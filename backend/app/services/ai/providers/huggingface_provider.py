import httpx
from app.config import get_settings
from app.core.exceptions import ProviderRateLimitError, ProviderError
from app.core.logging import get_logger

logger = get_logger(__name__)

# Serverless inference router — works on Render's free tier, no Pro required
HF_API_URL = "https://router.huggingface.co/hf-inference/models/stabilityai/stable-diffusion-xl-base-1.0"


class HuggingFaceProvider:
    name = "huggingface"

    async def generate(self, prompt: str, width: int = 1024, height: int = 1024) -> bytes:
        settings = get_settings()
        if not settings.huggingface_api_key:
            raise ProviderError(self.name, "API key not configured")
        try:
            async with httpx.AsyncClient(timeout=120) as client:
                resp = await client.post(
                    HF_API_URL,
                    headers={
                        "Authorization": f"Bearer {settings.huggingface_api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "inputs": prompt,
                        "parameters": {"width": width, "height": height},
                    },
                )
                if resp.status_code == 429:
                    raise ProviderRateLimitError(self.name)
                if resp.status_code in (503, 500):
                    raise ProviderError(self.name, f"Model unavailable: HTTP {resp.status_code}")
                if resp.status_code != 200:
                    raise ProviderError(self.name, f"HTTP {resp.status_code}: {resp.text[:200]}")
                logger.info("HuggingFace image generated", bytes=len(resp.content))
                return resp.content
        except (ProviderRateLimitError, ProviderError):
            raise
        except Exception as e:
            raise ProviderError(self.name, str(e))
