from django.core.management.base import BaseCommand
from django.core.management.base import CommandError
from decimal import Decimal
import random

from apps.properties.models import Location, Property, PropertyImage


CITY_NEIGHBORHOODS = [
    ("Bogota", ["Chapinero", "Usaquen", "Cedritos", "Santa Barbara", "Salitre"]),
    ("Medellin", ["El Poblado", "Laureles", "Belen", "Envigado", "Sabaneta"]),
    ("Cali", ["Ciudad Jardin", "Granada", "San Fernando", "Pance", "El Ingenio"]),
    ("Barranquilla", ["Alto Prado", "Villa Santos", "Riomar", "El Golf", "Buenavista"]),
    ("Cartagena", ["Bocagrande", "Manga", "Crespo", "Castillogrande", "Serena del Mar"]),
    ("La Ceja", ["El Yarumo", "Centro", "San Cayetano", "Payuco", "Villas de La Ceja"]),
]

PROPERTY_TYPES = [
    "Apartamento",
    "Casa",
    "Loft",
    "Apartaestudio",
    "Penthouse",
    "Casa campestre",
]

FEATURES = [
    "cocina integral",
    "balcon con buena vista",
    "parqueadero cubierto",
    "zona de ropas independiente",
    "seguridad 24 horas",
    "excelente iluminacion natural",
    "ascensor",
    "deposito privado",
    "zonas comunes",
    "facil acceso a transporte",
]

AUDIENCES = [
    "familias que quieren vivir cerca de servicios",
    "profesionales que buscan buena movilidad",
    "personas que valoran tranquilidad y seguridad",
    "inversionistas que buscan alta valorizacion",
    "parejas que necesitan espacios funcionales",
]

IMAGE_URLS = [
    "https://images.unsplash.com/photo-1512917774080-9991f1c4c750?auto=format&fit=crop&w=1200&q=80",
    "https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?auto=format&fit=crop&w=1200&q=80",
    "https://images.unsplash.com/photo-1564013799919-ab600027ffc6?auto=format&fit=crop&w=1200&q=80",
    "https://images.unsplash.com/photo-1600047509807-ba8f99d2cdde?auto=format&fit=crop&w=1200&q=80",
    "https://images.unsplash.com/photo-1600566753190-17f0baa2a6c3?auto=format&fit=crop&w=1200&q=80",
    "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?auto=format&fit=crop&w=1200&q=80",
    "https://images.unsplash.com/photo-1600607687939-ce8a6c25118c?auto=format&fit=crop&w=1200&q=80",
    "https://images.unsplash.com/photo-1605276374104-dee2a0ed3cd6?auto=format&fit=crop&w=1200&q=80",
    "https://images.unsplash.com/photo-1605146769289-440113cc3d00?auto=format&fit=crop&w=1200&q=80",
    "https://images.unsplash.com/photo-1613977257363-707ba9348227?auto=format&fit=crop&w=1200&q=80",
    "https://images.unsplash.com/photo-1613977257592-4871e5fcd7c4?auto=format&fit=crop&w=1200&q=80",
    "https://images.unsplash.com/photo-1631049307264-da0ec9d70304?auto=format&fit=crop&w=1200&q=80",
]


def build_address(rng):
    road = rng.choice(["Calle", "Carrera", "Transversal", "Diagonal"])
    return f"{road} {rng.randint(1, 150)} # {rng.randint(1, 99)}-{rng.randint(1, 99)}"


def build_feature_sentence(items):
    if len(items) == 1:
        return items[0]
    return f"{', '.join(items[:-1])} y {items[-1]}"


def build_price(operation, rng):
    if operation == Property.OP_RENT:
        return Decimal(rng.randrange(1_500_000, 8_500_001, 50_000))
    return Decimal(rng.randrange(180_000_000, 1_400_000_001, 1_000_000))


def build_property_payload(location, rng):
    operation = rng.choice([Property.OP_RENT, Property.OP_SALE])
    property_type = rng.choice(PROPERTY_TYPES)
    bedrooms = rng.randint(1, 5)
    bathrooms = rng.randint(1, min(4, bedrooms + 1))
    area_m2 = Decimal(rng.randint(35, 260))
    features = rng.sample(FEATURES, 3)
    operation_text = "en arriendo" if operation == Property.OP_RENT else "en venta"
    located_text = "ubicada" if property_type in {"Casa", "Casa campestre"} else "ubicado"
    bedroom_label = "habitacion" if bedrooms == 1 else "habitaciones"
    bathroom_label = "bano" if bathrooms == 1 else "banos"

    title = f"{property_type} {operation_text} en {location.neighborhood}"
    description = (
        f"{property_type} {operation_text} {located_text} en {location.neighborhood}, {location.city}. "
        f"Cuenta con {bedrooms} {bedroom_label}, {bathrooms} {bathroom_label}, {area_m2} m2, "
        f"{build_feature_sentence(features)}. "
        f"Ideal para {rng.choice(AUDIENCES)}."
    )

    return {
        "title": title,
        "description": description,
        "price": build_price(operation, rng),
        "operation": operation,
        "bedrooms": bedrooms,
        "bathrooms": bathrooms,
        "area_m2": area_m2,
    }


def get_or_create_location(city, neighborhood, address, idempotent):
    if not idempotent:
        return Location.objects.create(
            city=city,
            neighborhood=neighborhood,
            address=address,
        )

    location, _ = Location.objects.get_or_create(
        city=city,
        neighborhood=neighborhood,
        address=address,
    )
    return location


def get_or_create_property(location, payload, idempotent):
    if not idempotent:
        return Property.objects.create(
            **payload,
            is_active=True,
            location=location,
        ), True

    lookup = {
        **payload,
        "location": location,
    }
    prop = Property.objects.filter(**lookup).first()
    if prop:
        return prop, False

    return Property.objects.create(
        **payload,
        is_active=True,
        location=location,
    ), True


def create_property_images(property_obj, rng, image_count, idempotent=False):
    selected_urls = rng.sample(IMAGE_URLS, k=min(image_count, len(IMAGE_URLS)))
    while len(selected_urls) < image_count:
        selected_urls.append(rng.choice(IMAGE_URLS))

    for index, image_url in enumerate(selected_urls):
        if idempotent:
            existing_image = property_obj.images.filter(image_url=image_url).first()
            if existing_image:
                if index == 0 and not property_obj.images.filter(is_cover=True).exists():
                    existing_image.is_cover = True
                    existing_image.save(update_fields=["is_cover"])
                continue

        PropertyImage.objects.create(
            property=property_obj,
            image_url=image_url,
            is_cover=(index == 0),
        )


class Command(BaseCommand):
    help = 'Seed database with real-estate sample locations and properties'

    def add_arguments(self, parser):
        parser.add_argument('--locations', type=int, default=5)
        parser.add_argument('--properties', type=int, default=20)
        parser.add_argument('--images', type=int, default=3, help='Image URLs to create per seeded property')
        parser.add_argument('--seed', type=int, default=None, help='Optional random seed for reproducible sample data')
        parser.add_argument('--idempotent', action='store_true', help='Reuse existing generated sample records instead of duplicating them')

    def handle(self, *args, **options):
        loc_count = options.get('locations', 5)
        prop_count = options.get('properties', 20)
        image_count = options.get('images', 3)
        idempotent = options.get('idempotent', False)
        rng = random.Random(options.get('seed'))

        if loc_count < 1:
            raise CommandError('--locations must be at least 1')
        if prop_count < 0:
            raise CommandError('--properties cannot be negative')
        if image_count < 0:
            raise CommandError('--images cannot be negative')

        verb = "Ensuring" if idempotent else "Creating"
        self.stdout.write(self.style.NOTICE(f'{verb} {loc_count} locations'))
        locations = []
        for _ in range(loc_count):
            city, neighborhoods = rng.choice(CITY_NEIGHBORHOODS)
            loc = get_or_create_location(
                city=city,
                neighborhood=rng.choice(neighborhoods),
                address=build_address(rng),
                idempotent=idempotent,
            )
            locations.append(loc)

        self.stdout.write(self.style.NOTICE(f'{verb} {prop_count} properties'))
        created_properties = 0
        for _ in range(prop_count):
            loc = rng.choice(locations)
            payload = build_property_payload(loc, rng)

            prop, created = get_or_create_property(loc, payload, idempotent)
            if created:
                created_properties += 1
            create_property_images(prop, rng, image_count, idempotent=idempotent)

        self.stdout.write(self.style.SUCCESS(f'Seeding completed. Created {created_properties} new properties.'))
