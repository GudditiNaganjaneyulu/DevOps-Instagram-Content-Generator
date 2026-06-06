import cloudinary
import cloudinary.uploader
from app.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)


def configure_cloudinary() -> None:
    settings = get_settings()
    cloudinary.config(
        cloud_name=settings.cloudinary_cloud_name,
        api_key=settings.cloudinary_api_key,
        api_secret=settings.cloudinary_api_secret,
        secure=True,
    )
    logger.info("Cloudinary configured", cloud=settings.cloudinary_cloud_name)


async def upload_image_bytes(
    image_bytes: bytes,
    public_id: str,
    folder: str = "devops-emotions",
) -> dict:
    result = cloudinary.uploader.upload(
        image_bytes,
        public_id=public_id,
        folder=folder,
        resource_type="image",
        transformation=[{"width": 1080, "height": 1080, "crop": "fill"}],
        eager=[{"width": 400, "height": 400, "crop": "fill", "quality": "auto"}],
        eager_async=False,
    )
    return {
        "url": result["secure_url"],
        "thumbnail_url": result["eager"][0]["secure_url"] if result.get("eager") else result["secure_url"],
        "public_id": result["public_id"],
        "width": result["width"],
        "height": result["height"],
        "bytes": result["bytes"],
        "format": result["format"],
    }


async def delete_image(public_id: str) -> bool:
    result = cloudinary.uploader.destroy(public_id)
    return result.get("result") == "ok"
