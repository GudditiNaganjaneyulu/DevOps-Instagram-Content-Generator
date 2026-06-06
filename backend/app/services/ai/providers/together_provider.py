import asyncio
import httpx
import base64
from app.config import get_settings
from app.core.exceptions import ProviderError, ProviderRateLimitError
from app.core.logging import get_logger

logger = get_logger(__name__)

HORDE_BASE = "https://stablehorde.net/api/v2"


class StableHordeProvider:
    name = "stablehorde"

    async def generate(self, prompt: str, width: int = 1024, height: int = 1024) -> bytes:
        settings = get_settings()
        # "0000000000" = anonymous key (free, lower priority); or use registered key
        api_key = getattr(settings, "stable_horde_api_key", None) or "0000000000"

        async with httpx.AsyncClient(timeout=30) as client:
            # Submit job
            submit = await client.post(
                f"{HORDE_BASE}/generate/async",
                headers={"apikey": api_key, "Content-Type": "application/json"},
                json={
                    "prompt": prompt,
                    "params": {
                        "width": 512,   # anonymous limit is 807px — stay safe
                        "height": 512,
                        "steps": 20,
                        "n": 1,
                    },
                    "models": ["stable_diffusion"],
                    "r2": False,
                },
            )
            if submit.status_code == 429:
                raise ProviderRateLimitError(self.name)
            if submit.status_code != 202:
                raise ProviderError(self.name, f"Submit HTTP {submit.status_code}: {submit.text[:200]}")

            job_id = submit.json()["id"]
            logger.info("StableHorde job submitted", job_id=job_id)

        # Poll for completion (max 90s)
        async with httpx.AsyncClient(timeout=30) as client:
            for _ in range(18):
                await asyncio.sleep(5)
                check = await client.get(
                    f"{HORDE_BASE}/generate/check/{job_id}",
                    headers={"apikey": api_key},
                )
                if check.status_code != 200:
                    continue
                state = check.json()
                if state.get("done"):
                    break
            else:
                raise ProviderError(self.name, "Timed out waiting for image")

            # Fetch result
            result = await client.get(
                f"{HORDE_BASE}/generate/status/{job_id}",
                headers={"apikey": api_key},
            )
            if result.status_code != 200:
                raise ProviderError(self.name, f"Result HTTP {result.status_code}")

            generations = result.json().get("generations", [])
            if not generations:
                raise ProviderError(self.name, "No generations in response")

            img_data = generations[0].get("img", "")
            if img_data.startswith("http"):
                img_resp = await client.get(img_data)
                image_bytes = img_resp.content
            else:
                image_bytes = base64.b64decode(img_data)

            logger.info("StableHorde image generated", bytes=len(image_bytes))
            return image_bytes
