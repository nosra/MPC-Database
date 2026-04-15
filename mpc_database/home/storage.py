import cloudinary.uploader
import cloudinary.api
from django.core.files.storage import Storage
from django.conf import settings
import cloudinary
import logging

logger = logging.getLogger(__name__)

class CloudinaryStorage(Storage):
    def _save(self, name, content):
        logger.error(f"CloudinaryStorage._save called with name: {name}")
        cloudinary.config(
            cloud_name=settings.CLOUDINARY_STORAGE['CLOUD_NAME'],
            api_key=settings.CLOUDINARY_STORAGE['API_KEY'],
            api_secret=settings.CLOUDINARY_STORAGE['API_SECRET'],
        )
        try:
            result = cloudinary.uploader.upload(content, public_id=name, overwrite=True)
            logger.error(f"Cloudinary upload result: {result}")
            return result['public_id']
        except Exception as e:
            logger.error(f"Cloudinary upload failed: {e}")
            raise

    def url(self, name):
        return cloudinary.CloudinaryImage(name).build_url()

    def exists(self, name):
        return False