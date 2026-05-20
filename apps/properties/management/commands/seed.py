from django.core.management.base import BaseCommand
from faker import Faker
from decimal import Decimal
import random

from apps.properties.models import Location, Property


class Command(BaseCommand):
    help = 'Seed database with sample locations and properties'

    def add_arguments(self, parser):
        parser.add_argument('--locations', type=int, default=5)
        parser.add_argument('--properties', type=int, default=20)

    def handle(self, *args, **options):
        loc_count = options.get('locations', 5)
        prop_count = options.get('properties', 20)
        faker = Faker()

        self.stdout.write(self.style.NOTICE(f'Creating {loc_count} locations'))
        locations = []
        for _ in range(loc_count):
            loc = Location.objects.create(
                city=faker.city(),
                neighborhood=faker.street_name(),
                address=faker.address(),
            )
            locations.append(loc)

        self.stdout.write(self.style.NOTICE(f'Creating {prop_count} properties'))
        for _ in range(prop_count):
            loc = random.choice(locations)
            title = faker.sentence(nb_words=4)
            description = faker.paragraph(nb_sentences=3)
            price = Decimal(random.randint(50000000, 500000000))
            operation = random.choice(['rent', 'sale'])

            Property.objects.create(
                title=title,
                description=description,
                price=price,
                operation=operation,
                is_active=True,
                location=loc,
            )

        self.stdout.write(self.style.SUCCESS('Seeding completed.'))
