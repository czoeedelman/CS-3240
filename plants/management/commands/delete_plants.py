from django.core.management.base import BaseCommand
from plants.models import Plant

class Command(BaseCommand):
    help = "Delete all plants from the database."

    def handle(self, *args, **options):
        plant_count = Plant.objects.count()
        
        if plant_count > 0:
            Plant.objects.all().delete()
            self.stdout.write(self.style.SUCCESS(f"Successfully deleted {plant_count} plants."))
        else:
            self.stdout.write(self.style.WARNING("No plants to delete."))
