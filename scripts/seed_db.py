"""Seed the database with sample templates and categories."""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone
import os

MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://root:devpassword@localhost:27017")
DB_NAME = os.getenv("MONGODB_DB_NAME", "devops_emotions")

SAMPLE_TEMPLATES = [
    {
        "name": "kubernetes_crashloop",
        "category": "kubernetes",
        "content_type": "meme",
        "tone": "sarcastic",
        "joke_text": "Me: Why is the pod crashing?\nKubernetes: CrashLoopBackOff.\nMe: But why?\nKubernetes: Yes.",
        "caption": "The most honest error message in all of DevOps.",
        "hashtags": ["kubernetes", "k8s", "devops", "cloudnative"],
        "created_at": datetime.now(timezone.utc),
    },
    {
        "name": "terraform_state",
        "category": "terraform",
        "content_type": "meme",
        "tone": "dark_humor",
        "joke_text": "Me: terraform apply\nTerraform: Error: state file locked.\nMe: By who?\nTerraform: You. 3 days ago.",
        "caption": "The ghost of deployments past.",
        "hashtags": ["terraform", "iac", "devops", "infrastructure"],
        "created_at": datetime.now(timezone.utc),
    },
]


async def seed():
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client[DB_NAME]
    for t in SAMPLE_TEMPLATES:
        await db.templates.update_one({"name": t["name"]}, {"$set": t}, upsert=True)
    print(f"Seeded {len(SAMPLE_TEMPLATES)} templates into {DB_NAME}")
    client.close()


if __name__ == "__main__":
    asyncio.run(seed())
