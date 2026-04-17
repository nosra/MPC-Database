import cloudinary.uploader
import cloudinary.api
from django.core.files.storage import Storage
from django.conf import settings
import cloudinary
import cloudinary.utils
import logging
import os

logger = logging.getLogger(__name__)

AUDIO_EXTENSIONS = {"mp3", "wav", "ogg", "flac", "aac", "m4a"}

class CloudinaryStorage(Storage):
    def _save(self, name, content):
        cloudinary.config(
            cloud_name=settings.CLOUDINARY_STORAGE['CLOUD_NAME'],
            api_key=settings.CLOUDINARY_STORAGE['API_KEY'],
            api_secret=settings.CLOUDINARY_STORAGE['API_SECRET'],
        )
        ext = os.path.splitext(name)[1].lstrip(".").lower()

        # cloudinary uses video for audio
        resource_type = "video" if ext in AUDIO_EXTENSIONS else "image" 

        public_id = os.path.splitext(name)[0]
        result = cloudinary.uploader.upload(
            content,
            public_id=public_id,
            overwrite=True,
            resource_type=resource_type,
        )

        # store resource_type in the public_id so url() can recover it
        return f"{resource_type}:{result['public_id']}"

    def url(self, name):
        # recover resource_type if stored as a prefix
        if ":" in name:
            resource_type, public_id = name.split(":", 1)
        else:
            public_id = os.path.splitext(name)[0]
            resource_type = "image"

        return cloudinary.utils.cloudinary_url(public_id, resource_type=resource_type)[0]

    def exists(self, name):
        return False