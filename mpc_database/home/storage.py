import cloudinary.uploader
import cloudinary.api
from django.core.files.storage import Storage
from django.conf import settings
import cloudinary
import logging
import os

logger = logging.getLogger(__name__)
class CloudinaryStorage(Storage):
    def _save(self, name, content):
        cloudinary.config(
            cloud_name=settings.CLOUDINARY_STORAGE['CLOUD_NAME'],
            api_key=settings.CLOUDINARY_STORAGE['API_KEY'],
            api_secret=settings.CLOUDINARY_STORAGE['API_SECRET'],
        )
        public_id = os.path.splitext(name)[0] # strip extension
        result = cloudinary.uploader.upload(content, public_id=public_id, overwrite=True)
        return result['public_id']
    
    def url(self, name):
        public_id = os.path.splitext(name)[0]
        return cloudinary.CloudinaryImage(public_id).build_url()

    def exists(self, name):
        return False