import json
import httpx
from app.config import get_settings
from app.core.exceptions import ProviderRateLimitError, ProviderError
from app.core.logging import get_logger

logger = get_logger(__name__)

# gpt-4o-mini: best quality/cost ratio — ~$0.15/1M input tokens
# Falls back to gpt-3.5-turbo if 4o-mini is unavailable
MODELS = ["gpt-4o-mini", "gpt-3.5-turbo"]
API_URL = "https://api.openai.com/v1/chat/completions"


class OpenAIProvider:
    name = "openai"

    async def complete(self, system: str, user: str, model_index: int = 0) -> dict:
        settings = get_settings()
        if not settings.openai_api_key:
            raise ProviderError(self.name, "OPENAI_API_KEY not configured")

        model = MODELS[model_index % len(MODELS)]
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.post(
                    API_URL,
                    headers={
                        "Authorization": f"Bearer {settings.openai_api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": model,
                        "messages": [
                            {"role": "system", "content": system},
                            {"role": "user", "content": user},
                        ],
                        "temperature": 0.9,
                        "max_tokens": 1024,
                    },
                )
                if resp.status_code == 429:
                    raise ProviderRateLimitError(self.name)
                if resp.status_code == 401:
                    raise ProviderError(self.name, "Invalid API key")
                if resp.status_code == 402:
                    raise ProviderError(self.name, "Insufficient credits — top up at platform.openai.com")
                if resp.status_code != 200:
                    raise ProviderError(self.name, f"HTTP {resp.status_code}: {resp.text[:200]}")

                raw = resp.json()["choices"][0]["message"]["content"] or ""
                raw = raw.strip()
                if raw.startswith("```"):
                    raw = raw.split("```")[1]
                    if raw.startswith("json"):
                        raw = raw[4:]
                result = json.loads(raw.strip())
                logger.info("OpenAI generation succeeded", model=model)
                return result

        except (ProviderRateLimitError, ProviderError):
            raise
        except json.JSONDecodeError as e:
            raise ProviderError(self.name, f"JSON parse error: {e}")
        except Exception as e:
            err = str(e)
            if "429" in err or "rate" in err.lower():
                raise ProviderRateLimitError(self.name)
            raise ProviderError(self.name, err[:200])
