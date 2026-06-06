import base64
from google import genai
from google.genai import types
from app.config import get_settings
from app.core.exceptions import ProviderError, ProviderRateLimitError
from app.core.logging import get_logger

logger = get_logger(__name__)


class GeminiImageProvider:
    name = "gemini-image"

    def _get_client(self) -> genai.Client:
        settings = get_settings()
        if not settings.google_ai_api_key:
            raise ProviderError(self.name, "GOOGLE_AI_API_KEY not configured")
        return genai.Client(api_key=settings.google_ai_api_key)

    async def generate(self, prompt: str, width: int = 1024, height: int = 1024) -> bytes:
        client = self._get_client()
        try:
            response = client.models.generate_content(
                model="gemini-2.0-flash-preview-image-generation",
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_modalities=["IMAGE", "TEXT"],
                ),
            )
            for part in response.candidates[0].content.parts:
                if part.inline_data is not None:
                    data = part.inline_data.data
                    # SDK may return raw bytes or base64 string
                    if isinstance(data, (bytes, bytearray)):
                        image_bytes = bytes(data)
                    else:
                        image_bytes = base64.b64decode(data)
                    logger.info("Gemini image generated", bytes=len(image_bytes))
                    return image_bytes
            raise ProviderError(self.name, "No image part in Gemini response")
        except ProviderError:
            raise
        except Exception as e:
            msg = str(e)
            if "429" in msg or "quota" in msg.lower() or "rate" in msg.lower():
                raise ProviderRateLimitError(self.name)
            raise ProviderError(self.name, msg[:200])
