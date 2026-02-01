from django.db import models
from django.contrib.auth.models import AbstractUser
from django.templatetags.static import static
from django.core.files.storage import default_storage
from django.core.validators import FileExtensionValidator

# -----------------------
# USERS
# -----------------------

# inherits from AbstractUser, so it has:
# username, password, email, first_name, last_name
# is_staff, is_superuser, is_active
# last_login, date_joined
class CustomUser(AbstractUser):
    # optional profile picture
    avatar = models.ImageField(
        upload_to="avatars/",
        null=True,
        blank=True
    )

    def __str__(self):
        return self.username

# -----------------------
# PLUGINS
# -----------------------

CATEGORIES = [
    ("EFX", "Effect"),
    ("SYN", "Synth"),
    ("CMP", "Compressor"),
    ("DST", "Distorter"),
    ("DAW", "Digital Audio Workstation"),
]

# an alternative plugin can be an alternative to many pro plugins, and a pro plugin can have many alternatives
class AlternativePlugin(models.Model):
    submitter = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=30)
    # Always use DateField with a datetime.date instance.
    date_released = models.DateField()
    category = models.CharField(max_length=3, choices=CATEGORIES)
    price = models.IntegerField()
    description = models.TextField()
    # size of the plugin in MB, this will be converted to KB, MB, GB at the app level
    size = models.DecimalField(max_digits=8, decimal_places=2)
    download_link = models.CharField(max_length=99)
    
    # using django's imagefield to upload an image
    image = models.ImageField(upload_to="plugin_images/", null=True, blank=True)
    
    # fallback for no image
    @property
    def image_url(self):
        if self.image and default_storage.exists(self.image.name):
            return self.image.url
        # fallback to static default
        return static("plugins/default-plugin.jpg")


class ProPlugin(models.Model):
    submitter = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=30)
    # Always use DateField with a datetime.date instance.
    date_released = models.DateField()
    category = models.CharField(max_length=3, choices=CATEGORIES)
    price = models.IntegerField()
    description = models.TextField()
    # size of the plugin in MB, this will be converted to KB, MB, GB at the app level
    size = models.DecimalField(max_digits=8, decimal_places=2)
    # implied this is a VST, so it should work on all OSes.
    download_link = models.CharField(max_length=99)
    
    # using django's imagefield to upload an image
    image = models.ImageField(upload_to="plugin_images/", null=True, blank=True)
    
    # fallback for no image
    @property
    def image_url(self):
        if self.image and default_storage.exists(self.image.name):
            return self.image.url
        # fallback to static default
        return static("plugins/default-plugin.jpg")
    
    # mtm with pro plugin
    alternatives = models.ManyToManyField(AlternativePlugin, related_name="pro_plugins", blank=True)

    def __str__(self):
        return self.name

# -----------------------
# AUDIO DEMOS 
# -----------------------

class AudioDemo(models.Model):
    title = models.CharField(max_length=60, blank=True)
    
    # actual audio file
    audio_file = models.FileField(
        upload_to="audio_demos/",
        validators=[FileExtensionValidator(allowed_extensions=["mp3", "wav", "ogg"])]
    )

    # setting up key for which plugin this belongs to
    pro_plugin = models.ForeignKey(
        "ProPlugin",
        on_delete = models.CASCADE,
        related_name = "audio_demos",
        null=True,
        blank=True,
    )

    alt_plugin = models.ForeignKey(
        "AlternativePlugin",
        on_delete = models.CASCADE,
        null=True,
        blank=True,
    )

    def __str__(self):
        return self.title or self.audio_file.name
