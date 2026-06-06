import pytest
from unittest.mock import AsyncMock, patch
from app.services.ai.text_engine import TextGenerationEngine
from app.core.exceptions import AllProvidersExhaustedError, ProviderError

MOCK_RESULT = {
    "joke_text": "DevOps: Why is the pod crashing?\nKubernetes: Have you tried turning it off and on again?",
    "caption": "When Kubernetes gives you the silent treatment at 3am.",
    "hashtags": ["devops", "kubernetes"],
    "image_prompt": "A frustrated engineer staring at a terminal.",
}


@pytest.mark.asyncio
async def test_generate_meme_uses_groq_first():
    engine = TextGenerationEngine()
    with patch.object(engine.providers[0], "complete", new_callable=AsyncMock) as mock_groq:
        mock_groq.return_value = MOCK_RESULT
        result, provider = await engine.generate_meme("kubernetes", "sarcastic")
        assert result == MOCK_RESULT
        assert "groq" in provider


@pytest.mark.asyncio
async def test_fallback_to_gemini_on_groq_failure():
    engine = TextGenerationEngine()
    with patch.object(engine.providers[0], "complete", side_effect=ProviderError("groq", "rate limit")):
        with patch.object(engine.providers[1], "complete", new_callable=AsyncMock) as mock_gemini:
            mock_gemini.return_value = MOCK_RESULT
            result, provider = await engine.generate_meme("kubernetes", "sarcastic")
            assert result == MOCK_RESULT
            assert "gemini" in provider


@pytest.mark.asyncio
async def test_all_providers_exhausted_raises():
    engine = TextGenerationEngine()
    for p in engine.providers:
        p.complete = AsyncMock(side_effect=ProviderError(p.name, "failed"))
    with pytest.raises(AllProvidersExhaustedError):
        await engine.generate_meme("kubernetes", "sarcastic")
