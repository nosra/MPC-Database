from django.db import models
from django.contrib.auth.models import AbstractUser
from django.templatetags.static import static
from django.core.files.storage import default_storage
from django.core.validators import FileExtensionValidator, MinValueValidator, MaxValueValidator
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db.models import Avg

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
# RATINGS
# -----------------------

class Rating(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    # changing this to FloatField to support 0.5, 1.5, etc.
    score = models.FloatField(validators=[MinValueValidator(0.5), MaxValueValidator(5.0)])
    
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    class Meta:
        unique_together = ('user', 'content_type', 'object_id')

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

class RatingMixin:
    def calculate_average_rating(self):
        # get all ratings for this specific object
        ratings = Rating.objects.filter(
            content_type=ContentType.objects.get_for_model(self),
            object_id=self.id
        )
        # calculate average
        aggregate = ratings.aggregate(Avg('score'))
        new_rating = aggregate['score__avg'] or 0.0
        
        # update the field on the model
        self.rating = new_rating
        self.save()

# an alternative plugin can be an alternative to many pro plugins, and a pro plugin can have many alternatives
class AlternativePlugin(models.Model, RatingMixin):
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

    # ratings system, to be modified by users
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    
    # fallback for no image
    @property
    def image_url(self):
        if self.image and default_storage.exists(self.image.name):
            return self.image.url
        # fallback to static default
        return static("plugins/default-plugin.jpg")


class ProPlugin(models.Model, RatingMixin):
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
    
    # ratings system, to be modified by users
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    
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
