import random
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from home.models import CustomUser, AlternativePlugin, ProPlugin, CATEGORIES

# constants for generating random data
ADJECTIVES = ["Analog", "Digital", "Vintage", "Modern", "Harmonic", "Dynamic", "Spectral"]
NOUNS = ["Compressor", "EQ", "Limiter", "Verb", "Synth", "Drive", "Engine"]
DESCRIPTIONS = [
    "This plugin adds warmth and character to your sound.",
    "A transparent tool for precise mixing.",
    "Emulates the classic hardware from the 80s.",
    "Essential for any modern producer's toolkit."
]

class Command(BaseCommand):
    help = "Generates test data for the app"

    @transaction.atomic
    def handle(self, *args, **kwargs):
        self.stdout.write("Deleting old data...")
        # clear old data to avoid duplicates (Optional)
        ProPlugin.objects.all().delete()
        AlternativePlugin.objects.all().delete()
        CustomUser.objects.exclude(is_superuser=True).delete()

        self.stdout.write("Creating Users...")
        users = []
        for i in range(5):
            user = CustomUser.objects.create_user(
                username=f'producer_{i}',
                email=f'producer_{i}@example.com',
                password='password123'
            )
            users.append(user)

        self.stdout.write("Creating Alternative Plugins...")
        alt_plugins = []
        for i in range(100):
            p = AlternativePlugin(
                submitter=random.choice(users),
                name=f"{random.choice(ADJECTIVES)} {random.choice(NOUNS)} Free",
                date_released=timezone.now().date(),
                category=random.choice(CATEGORIES)[0], # gets the key (e.g. 'EFX')
                price=0, # alternativs usually free or cheap
                description=random.choice(DESCRIPTIONS),
                size=random.uniform(5.0, 500.0),
                download_link="https://github.com/example/plugin"
            )
            p.save()
            alt_plugins.append(p)

        self.stdout.write("Creating Pro Plugins...")
        for i in range(50):
            pro = ProPlugin(
                submitter=random.choice(users),
                name=f"{random.choice(ADJECTIVES)} {random.choice(NOUNS)} Pro",
                date_released=timezone.now().date(),
                category=random.choice(CATEGORIES)[0],
                price=random.randint(29, 499),
                description=random.choice(DESCRIPTIONS),
                size=random.uniform(100.0, 2000.0),
                download_link="https://store.example.com/plugin"
            )
            pro.save()
            
            # add 1 to 3 random alternatives to this Pro plugin
            random_alts = random.sample(alt_plugins, k=random.randint(1, 8))
            pro.alternatives.set(random_alts)

        self.stdout.write(self.style.SUCCESS("Successfully populated the database!"))