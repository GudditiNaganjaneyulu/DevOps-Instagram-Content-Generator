import asyncio
import json
from google import genai
from google.genai import types
from app.config import get_settings
from app.core.exceptions import ProviderRateLimitError, ProviderError
from app.core.logging import get_logger

logger = get_logger(__name__)


def _strip_fences(raw: str) -> str:
    raw = raw.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    return raw.strip()


class GeminiProvider:
    name = "gemini"

    def __init__(self):
        self._client: genai.Client | None = None

    def _get_client(self) -> genai.Client:
        if not self._client:
            settings = get_settings()
            if not settings.google_ai_api_key:
                raise ProviderError(self.name, "API key not configured")
            self._client = genai.Client(api_key=settings.google_ai_api_key)
        return self._client

    def _call_sync(self, system: str, user: str) -> str:
        client = self._get_client()
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=user,
            config=types.GenerateContentConfig(
                system_instruction=system,
                temperature=0.85,
                max_output_tokens=1024,
                response_mime_type="application/json",
            ),
        )
        return response.text or ""

    async def complete(self, system: str, user: str, **kwargs) -> dict:
        try:
            # Run sync SDK in threadpool — avoids blocking the event loop
            raw = await asyncio.to_thread(self._call_sync, system, user)
            return json.loads(_strip_fences(raw))
        except json.JSONDecodeError as e:
            raise ProviderError(self.name, f"JSON parse error: {e}")
        except Exception as e:
            err = str(e)
            if "quota" in err.lower() or "429" in err or "rate" in err.lower():
                raise ProviderRateLimitError(self.name)
            logger.warning("Gemini error", error=err)
            raise ProviderError(self.name, err)
