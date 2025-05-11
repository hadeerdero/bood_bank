# blood_stock/management/commands/seed_egypt_cities.py
from django.core.management.base import BaseCommand
from apps.city.models import City

EGYPT_CITIES = [
    {"name": "Cairo", "latitude": 30.0444, "longitude": 31.2357},
    {"name": "Alexandria", "latitude": 31.2001, "longitude": 29.9187},
    {"name": "Giza", "latitude": 29.9870, "longitude": 31.2118},
    {"name": "Luxor", "latitude": 25.6872, "longitude": 32.6396},
    {"name": "Aswan", "latitude": 24.0889, "longitude": 32.8998},
    {"name": "Port Said", "latitude": 31.2565, "longitude": 32.2841},
    {"name": "Suez", "latitude": 29.9668, "longitude": 32.5498},
    {"name": "Ismailia", "latitude": 30.6043, "longitude": 32.2723},
    {"name": "Damietta", "latitude": 31.4167, "longitude": 31.8214},
    {"name": "Mansoura", "latitude": 31.0409, "longitude": 31.3785},
    {"name": "Tanta", "latitude": 30.7825, "longitude": 31.0000},
    {"name": "Asyut", "latitude": 27.1820, "longitude": 31.1829},
    {"name": "Minya", "latitude": 28.1099, "longitude": 30.7503},
    {"name": "Beni Suef", "latitude": 29.0667, "longitude": 31.0833},
    {"name": "Faiyum", "latitude": 29.3084, "longitude": 30.8441},
]

class Command(BaseCommand):
    help = 'Seeds Egyptian cities with coordinates for blood bank system'

    def handle(self, *args, **options):
        created_count = 0
        for city_data in EGYPT_CITIES:
            city, created = City.objects.get_or_create(
                name=city_data["name"],
                defaults={
                    'latitude': city_data["latitude"],
                    'longitude': city_data["longitude"]
                }
            )
            if created:
                created_count += 1
                self.stdout.write(f'Created {city.name}')

        self.stdout.write(
            self.style.SUCCESS(f'\nSuccessfully seeded {created_count} Egyptian cities')
        )