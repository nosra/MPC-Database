import cloudinary.uploader
from django.db.models.signals import post_delete
from django.dispatch import receiver
from .models import ProPlugin, AlternativePlugin, AudioDemo

def _delete_cloudinary_file(name, default_resource_type="image"):
    # delete the cloudinary file handling the prefix
    if not name:
        return
    if ":" in name:
        resource_type, public_id = name.split(":", 1)
    else:
        public_id = name
        resource_type = default_resource_type
    
    try:
        cloudinary.uploader.destroy(public_id, resource_type=resource_type)
    except Exception as e:
        # log but don't crash. the DB row is already gone
        import logging
        logging.getLogger(__name__).warning(f"Failed to delete Cloudinary asset '{public_id}': {e}")


@receiver(post_delete, sender=ProPlugin)
@receiver(post_delete, sender=AlternativePlugin)
def delete_plugin_image(sender, instance, **kwargs):
    if instance.image:
        _delete_cloudinary_file(instance.image.name, default_resource_type="image")


@receiver(post_delete, sender=AudioDemo)
def delete_audio_demo(sender, instance, **kwargs):
    if instance.audio_file:
        _delete_cloudinary_file(instance.audio_file.name, default_resource_type="video")