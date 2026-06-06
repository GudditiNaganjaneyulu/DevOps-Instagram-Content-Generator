import json
import httpx
from app.config import get_settings
from app.core.exceptions import ProviderRateLimitError, ProviderError
from app.core.logging import get_logger

logger = get_logger(__name__)

FREE_MODELS = [
    "meta-llama/llama-3.1-8b-instruct:free",
    "mistralai/mistral-7b-instruct:free",
    "google/gemma-2-9b-it:free",
]


class OpenRouterProvider:
    name = "openrouter"
    BASE_URL = "https://openrouter.ai/api/v1/chat/completions"

    async def complete(self, system: str, user: str, model_index: int = 0) -> dict:
        settings = get_settings()
        if not settings.openrouter_api_key:
            raise ProviderError(self.name, "API key not configured")

        model = FREE_MODELS[model_index % len(FREE_MODELS)]
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.post(
                    self.BASE_URL,
                    headers={
                        "Authorization": f"Bearer {settings.openrouter_api_key}",
                        "HTTP-Referer": "https://devops-runtime-emotions.vercel.app",
                        "X-Title": "DevOps Runtime Emotions",
                    },
                    json={
                        "model": model,
                        "messages": [
                            {"role": "system", "content": system},
                            {"role": "user", "content": user},
                        ],
                        "temperature": 0.85,
                        "max_tokens": 1024,
                    },
                )
                if resp.status_code == 429:
                    raise ProviderRateLimitError(self.name)
                if resp.status_code != 200:
                    raise ProviderError(self.name, f"HTTP {resp.status_code}")
                data = resp.json()
                raw = data["choices"][0]["message"]["content"].strip()
                if raw.startswith("```"):
                    raw = raw.split("```")[1]
                    if raw.startswith("json"):
                        raw = raw[4:]
                return json.loads(raw.strip())
        except (ProviderRateLimitError, ProviderError):
            raise
        except Exception as e:
            logger.warning("OpenRouter error", model=model, error=str(e))
            raise ProviderError(self.name, str(e))
