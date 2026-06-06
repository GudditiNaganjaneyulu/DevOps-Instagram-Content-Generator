import httpx
from urllib.parse import quote
from app.core.exceptions import ProviderError
from app.core.logging import get_logger

logger = get_logger(__name__)

BASE_URL = "https://image.pollinations.ai/prompt"


class PollinationsProvider:
    name = "pollinations"

    async def generate(self, prompt: str, width: int = 1080, height: int = 1080) -> bytes:
        encoded = quote(prompt)
        url = f"{BASE_URL}/{encoded}?width={width}&height={height}&nologo=true&enhance=true"
        try:
            async with httpx.AsyncClient(timeout=60, follow_redirects=True) as client:
                resp = await client.get(url)
                if resp.status_code != 200:
                    raise ProviderError(self.name, f"HTTP {resp.status_code}")
                content_type = resp.headers.get("content-type", "")
                if "image" not in content_type:
                    raise ProviderError(self.name, f"Non-image response: {content_type}")
                logger.info("Pollinations image generated", bytes=len(resp.content))
                return resp.content
        except (ProviderError,):
            raise
        except Exception as e:
            raise ProviderError(self.name, str(e))
