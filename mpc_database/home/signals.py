import cloudinary.uploader
from django.db.models.signals import post_delete
from django.dispatch import receiver
from .models import ProPlugin, AlternativePlugin, AudioDemo
from .cloudinary_utils import delete_cloudinary_file

@receiver(post_delete, sender=ProPlugin)
@receiver(post_delete, sender=AlternativePlugin)
def delete_plugin_image(sender, instance, **kwargs):
    if instance.image:
        delete_cloudinary_file(instance.image.name, default_resource_type="image")


@receiver(post_delete, sender=AudioDemo)
def delete_audio_demo(sender, instance, **kwargs):
    if instance.audio_file:
        delete_cloudinary_file(instance.audio_file.name, default_resource_type="video")