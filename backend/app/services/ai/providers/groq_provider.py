import json
from groq import AsyncGroq
from app.config import get_settings
from app.core.exceptions import ProviderRateLimitError, ProviderError
from app.core.logging import get_logger

logger = get_logger(__name__)

MODELS = ["llama-3.3-70b-versatile", "deepseek-r1-distill-llama-70b", "qwen-qwq-32b"]


class GroqProvider:
    name = "groq"

    def __init__(self):
        self._client: AsyncGroq | None = None

    def _get_client(self) -> AsyncGroq:
        if not self._client:
            settings = get_settings()
            self._client = AsyncGroq(api_key=settings.groq_api_key)
        return self._client

    async def complete(self, system: str, user: str, model_index: int = 0) -> dict:
        if not get_settings().groq_api_key:
            raise ProviderError(self.name, "API key not configured")

        model = MODELS[model_index % len(MODELS)]
        try:
            client = self._get_client()
            response = await client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                temperature=0.85,
                max_tokens=1024,
            )
            raw = response.choices[0].message.content or ""
            # Strip markdown code fences if present
            raw = raw.strip()
            if raw.startswith("```"):
                raw = raw.split("```")[1]
                if raw.startswith("json"):
                    raw = raw[4:]
            return json.loads(raw.strip())
        except Exception as e:
            err = str(e)
            if "rate_limit" in err.lower() or "429" in err:
                raise ProviderRateLimitError(self.name)
            logger.warning("Groq error", model=model, error=err)
            raise ProviderError(self.name, err)
