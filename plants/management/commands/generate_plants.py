import random
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from plants.models import Plant

PLANT_NAMES = ["Fern", "Cactus", "Bamboo", "Aloe Vera", "Ivy", "Orchid", "Daisy", "Tulip", "Rose", "Lily"]
DESCRIPTIONS = [
    "A hardy plant that thrives in shade.",
    "Needs little water and lots of sun.",
    "Fast-growing and great for decoration.",
    "Has medicinal properties and is easy to care for.",
    "Climbing plant that grows quickly.",
    "Beautiful flowers that require careful maintenance.",
    "Bright and cheerful, perfect for gardens.",
    "A classic flower with a variety of colors.",
    "Aromatic and often used in perfumes.",
    "Elegant and widely recognized."
]
SUNLIGHT_OPTIONS = [
        ('Low/Artificial', 'Low/Artificial'),
        ('Partial/Bright Indirect', 'Partial/Bright Indirect'),
        ('Direct Sunlight', 'Direct Sunlight'),
    ]
WATER_OPTIONS = [
        ('Dry', 'Dry'),
        ('Moist', 'Moist'),
        ('Frequent', 'Frequent'),
    ]
TEMP_RANGES = ["60–75°F", "70–85°F", "50–65°F"]
HUMIDITY_OPTIONS = [
        ('Low', 'Low'),
        ('Medium', 'Medium'),
        ('High', 'High'),
    ]
SOIL_TYPES = ["Loamy", "Sandy", "Clay", "Well-draining", None]

SIZE_CHOICES = [
        ('XS (5-12 inches)', 'XS (5-12 inches)'),
        ('SM (7-18 inches)', 'SM (7-18 inches)'),
        ('MD (1-2 FT)', 'MD (1-2 FT)'),
        ('LG (1.5-2.5 FT)', 'LG (1.5-2.5 FT)'),
        ('XL (2-3 FT)', 'XL (2-3 FT)'),
        ('XXL (3-5 FT)', 'XXL (3-5 FT)'),
    ]

DIFFICULTY_CHOICES = [
        ('No-fuss', 'No-fuss'),
        ('Easy', 'Easy'),
        ('Moderate', 'Moderate'),
    ]

class Command(BaseCommand):
    help = "Generate random plants and add them to the database."

    def add_arguments(self, parser):
        parser.add_argument('--count', type=int, default=10, help='Number of plants to generate')

    def handle(self, *args, **options):
        count = options['count']
        plants = []

        for _ in range(count):
            name = random.choice(PLANT_NAMES)
            description = random.choice(DESCRIPTIONS)
            sunlight = random.choice(SUNLIGHT_OPTIONS)
            water = random.choice(WATER_OPTIONS)
            temperature = random.choice(TEMP_RANGES)
            humidity = random.choice(HUMIDITY_OPTIONS)
            soil = random.choice(SOIL_TYPES)
            size = random.choice(SIZE_CHOICES)
            difficulty = random.choice(DIFFICULTY_CHOICES)
            price = random.uniform(0, 200)

            plant = Plant(
                name=name,
                description=description,
                sunlight_reqs=sunlight,
                water_reqs=water,
                temperature_range=temperature,
                humidity_reqs=humidity,
                soil=soil,
                is_available=True,
                rating=round(random.uniform(1, 5), 2),
                size=size,
                difficulty=difficulty,
                price_range=price,
                location="Charlottesville, VA",
            )
            plants.append(plant)

        Plant.objects.bulk_create(plants)
        self.stdout.write(self.style.SUCCESS(f"Successfully added {count} plants!"))