import base64
import httpx
from app.config import get_settings
from app.core.exceptions import ProviderError, ProviderRateLimitError
from app.core.logging import get_logger

logger = get_logger(__name__)

FAL_API_URL = "https://fal.run/fal-ai/flux/schnell"


class FalProvider:
    name = "fal"

    async def generate(self, prompt: str, width: int = 1024, height: int = 1024) -> bytes:
        settings = get_settings()
        if not settings.fal_api_key:
            raise ProviderError(self.name, "FAL_API_KEY not configured")
        try:
            async with httpx.AsyncClient(timeout=120) as client:
                resp = await client.post(
                    FAL_API_URL,
                    headers={
                        "Authorization": f"Key {settings.fal_api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "prompt": prompt,
                        "image_size": "square_hd",
                        "num_inference_steps": 4,
                        "num_images": 1,
                        "enable_safety_checker": False,
                    },
                )
                if resp.status_code == 429:
                    raise ProviderRateLimitError(self.name)
                if resp.status_code != 200:
                    raise ProviderError(self.name, f"HTTP {resp.status_code}: {resp.text[:200]}")
                data = resp.json()
                image_url = data["images"][0]["url"]
                # Download the image from the returned URL
                img_resp = await client.get(image_url)
                if img_resp.status_code != 200:
                    raise ProviderError(self.name, "Failed to download generated image")
                logger.info("Fal image generated", bytes=len(img_resp.content))
                return img_resp.content
        except (ProviderRateLimitError, ProviderError):
            raise
        except Exception as e:
            raise ProviderError(self.name, str(e))
