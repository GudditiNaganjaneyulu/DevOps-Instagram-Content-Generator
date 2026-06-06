"""Quick smoke-test for all AI providers."""
import asyncio
import os


async def test_groq():
    from groq import AsyncGroq
    key = os.getenv("GROQ_API_KEY", "")
    if not key:
        print("GROQ: SKIP (no key)")
        return
    client = AsyncGroq(api_key=key)
    r = await client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": "Reply with only: OK"}],
        max_tokens=10,
    )
    print(f"GROQ: OK — {r.choices[0].message.content}")


async def test_pollinations():
    import httpx
    url = "https://image.pollinations.ai/prompt/a%20simple%20blue%20circle?width=64&height=64&nologo=true"
    async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
        r = await client.get(url)
        print(f"POLLINATIONS: {'OK' if r.status_code == 200 else 'FAIL'} — {r.status_code}, {len(r.content)} bytes")


async def main():
    print("Testing AI providers...\n")
    await test_groq()
    await test_pollinations()
    print("\nDone.")


if __name__ == "__main__":
    asyncio.run(main())
