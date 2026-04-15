import cloudinary.uploader
import cloudinary.api
from django.core.files.storage import Storage
from django.conf import settings
import cloudinary

class CloudinaryStorage(Storage):
    def _save(self, name, content):
        cloudinary.config(
            cloud_name=settings.CLOUDINARY_STORAGE['CLOUD_NAME'],
            api_key=settings.CLOUDINARY_STORAGE['API_KEY'],
            api_secret=settings.CLOUDINARY_STORAGE['API_SECRET'],
        )
        result = cloudinary.uploader.upload(content, public_id=name, overwrite=True)
        return result['public_id']

    def url(self, name):
        return cloudinary.CloudinaryImage(name).build_url()

    def exists(self, name):
        return False