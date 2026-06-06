import httpx
import feedparser
from datetime import datetime, timezone
from app.services.ai.text_engine import TextGenerationEngine
from app.services.ai.image_engine import ImageGenerationEngine
from app.models.trend import TrendSource, TrendRead, trend_from_doc
from app.core.redis_client import cache_get, cache_set
from app.core.logging import get_logger
import json

logger = get_logger(__name__)

text_engine = TextGenerationEngine()
image_engine = ImageGenerationEngine()

DEVOPS_SUBREDDITS = ["devops", "kubernetes", "aws", "Terraform", "docker", "sre"]
HN_DEVOPS_QUERIES = ["kubernetes", "terraform", "devops", "AWS outage", "docker"]
K8S_BLOG_RSS = "https://kubernetes.io/feed.xml"


async def fetch_reddit_trends(limit: int = 10) -> list[dict]:
    results = []
    async with httpx.AsyncClient(timeout=15, headers={"User-Agent": "DevOpsEmotions/1.0"}) as client:
        for sub in DEVOPS_SUBREDDITS[:3]:
            try:
                resp = await client.get(
                    f"https://www.reddit.com/r/{sub}/hot.json?limit=5",
                )
                if resp.status_code != 200:
                    continue
                posts = resp.json()["data"]["children"]
                for p in posts:
                    d = p["data"]
                    results.append({
                        "title": d["title"],
                        "url": f"https://reddit.com{d['permalink']}",
                        "source": TrendSource.reddit,
                        "score": d.get("score", 0),
                        "comments": d.get("num_comments", 0),
                        "category": _classify_category(d["title"]),
                        "fetched_at": datetime.now(timezone.utc),
                    })
            except Exception as e:
                logger.warning("Reddit fetch failed", subreddit=sub, error=str(e))
    return results[:limit]


async def fetch_hn_trends(limit: int = 10) -> list[dict]:
    results = []
    async with httpx.AsyncClient(timeout=15) as client:
        for query in HN_DEVOPS_QUERIES[:2]:
            try:
                resp = await client.get(
                    f"https://hn.algolia.com/api/v1/search?tags=story&query={query}&hitsPerPage=5"
                )
                if resp.status_code != 200:
                    continue
                for hit in resp.json().get("hits", []):
                    results.append({
                        "title": hit.get("title", ""),
                        "url": hit.get("url") or f"https://news.ycombinator.com/item?id={hit['objectID']}",
                        "source": TrendSource.hackernews,
                        "score": hit.get("points", 0),
                        "comments": hit.get("num_comments", 0),
                        "category": _classify_category(hit.get("title", "")),
                        "fetched_at": datetime.now(timezone.utc),
                    })
            except Exception as e:
                logger.warning("HN fetch failed", query=query, error=str(e))
    return results[:limit]


def _classify_category(title: str) -> str:
    title_lower = title.lower()
    for keyword, cat in [
        ("kubernetes", "kubernetes"), ("k8s", "kubernetes"),
        ("terraform", "terraform"), ("aws", "aws"), ("azure", "azure"),
        ("docker", "docker"), ("ci/cd", "cicd"), ("github actions", "cicd"),
        ("incident", "incident"), ("outage", "incident"),
    ]:
        if keyword in title_lower:
            return cat
    return "general"


async def get_trends(db, limit: int = 20) -> list[TrendRead]:
    cache_key = "trends:latest"
    cached = await cache_get(cache_key)
    if cached:
        docs = json.loads(cached)
        return [TrendRead(**d) for d in docs]

    reddit = await fetch_reddit_trends(10)
    hn = await fetch_hn_trends(10)
    all_trends = reddit + hn
    all_trends.sort(key=lambda x: x.get("score", 0), reverse=True)

    saved = []
    for t in all_trends[:limit]:
        result = await db.trends.insert_one({**t, "source": t["source"].value})
        t["_id"] = result.inserted_id
        saved.append(trend_from_doc(t))

    cache_payload = [t.model_dump(mode="json") for t in saved]
    await cache_set(cache_key, json.dumps(cache_payload, default=str), ttl=21600)
    return saved


async def generate_trend_meme(trend_id: str, user_id: str, db) -> dict:
    from bson import ObjectId
    doc = await db.trends.find_one({"_id": ObjectId(trend_id)})
    if not doc:
        return {"error": "Trend not found"}

    text_result, provider = await text_engine.generate_trend_content(
        title=doc["title"],
        source=doc["source"],
        category=doc.get("category", "general"),
    )

    image_url = None
    if text_result.get("image_prompt"):
        try:
            img = await image_engine.generate_and_store(
                text_result["image_prompt"], folder="devops-emotions/trends"
            )
            image_url = img["url"]
        except Exception as e:
            logger.warning("Trend image failed", error=str(e))

    await db.trends.update_one(
        {"_id": ObjectId(trend_id)},
        {"$set": {"image_url": image_url, "text_provider": provider}},
    )
    return {**text_result, "image_url": image_url, "trend_id": trend_id}
