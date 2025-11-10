from django.db import models
from django.contrib.auth.models import AbstractUser

# -----------------------
# USERS
# -----------------------

# inherits from AbstractUser, so it has:
# username, password, email, first_name, last_name
# is_staff, is_superuser, is_active
# last_login, date_joined
class CustomUser(AbstractUser):
    pass
    # add additional fields in here

    def __str__(self):
        return self.username

# -----------------------
# PLUGINS
# -----------------------

CATEGORIES = {
    ("EFX", "Effect"),
    ("SYN", "Synth"),
    ("CMP", "Compressor"),
    ("DST", "Distorter"),
}

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
    size = models.DecimalField(max_digits=5, decimal_places=2)
    download_link = models.CharField(max_length=99)

    def __str__():
        return self.name


class ProPlugin(models.Model):
    submitter = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=30)
    # Always use DateField with a datetime.date instance.
    date_released = models.DateField()
    category = models.CharField(max_length=3, choices=CATEGORIES)
    price = models.IntegerField()
    description = models.TextField()
    # size of the plugin in MB, this will be converted to KB, MB, GB at the app level
    size = models.DecimalField(max_digits=5, decimal_places=2)
    # implied this is a VST, so it should work on all OSes.
    download_link = models.CharField(max_length=99)
    alternatives = models.ManyToManyField(AlternativePlugin, related_name="pro_plugins")

    def __str__():
        return self.name
