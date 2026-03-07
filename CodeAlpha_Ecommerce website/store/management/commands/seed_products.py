"""
Management command to generate 60 sample products in the database.
Run with: python manage.py seed_products
"""

import random
from decimal import Decimal
from urllib.request import urlopen
from io import BytesIO

from django.core.management.base import BaseCommand
from django.core.files.images import ImageFile

from store.models import Product


# Word pools for generating realistic product names
ADJECTIVES = [
    'Wireless', 'Smart', 'Portable', 'Premium', 'Classic', 'Modern',
    'Pro', 'Ultra', 'Mini', 'Ergonomic', 'Gaming', 'Bluetooth',
    'USB-C', 'High-Speed', 'Compact', 'Lightweight', 'Stainless',
]

PRODUCT_TYPES = [
    'Headphones', 'Mouse', 'Keyboard', 'Watch', 'Charger', 'Hub',
    'Speaker', 'Monitor', 'Camera', 'Adapter', 'Cable', 'Stand',
    'Case', 'Backpack', 'Lamp', 'Desk Mat', 'Webcam', 'Microphone',
    'Tablet', 'Earbuds', 'Power Bank', 'Dock', 'Controller',
]


DESCRIPTIONS = [
    'High-quality build with premium materials. Perfect for daily use.',
    'Features cutting-edge technology for the best performance.',
    'Compact and lightweight design. Ideal for on-the-go.',
    'Designed for comfort and durability. Built to last.',
    'Includes all essential features at an affordable price.',
    'Professional grade quality. Trusted by experts worldwide.',
    'Sleek modern design that fits any workspace.',
    'Ergonomic design reduces fatigue during extended use.',
    'Fast and reliable. Get more done in less time.',
    'Premium sound/performance. Experience the difference.',
]


class Command(BaseCommand):
    help = 'Generates 60 random sample products (deletes existing products)'

    def _generate_name(self):
        """Generate a random product name from word pools."""
        adj = random.choice(ADJECTIVES)
        product_type = random.choice(PRODUCT_TYPES)
        return f'{adj} {product_type}'

    def _fetch_placeholder_bytes(self, url='https://via.placeholder.com/300'):
        """Download placeholder image. Returns bytes or None if failed."""
        try:
            response = urlopen(url, timeout=10)
            return response.read()
        except Exception:
            return None

    def _create_image_file(self, content, filename):
        """Create ImageFile from bytes (each save needs fresh BytesIO)."""
        return ImageFile(BytesIO(content), name=filename)

    def handle(self, *args, **options):
        # Delete existing products
        count_before = Product.objects.count()
        Product.objects.all().delete()
        if count_before > 0:
            self.stdout.write(f'Deleted {count_before} existing products.')

        # Fetch placeholder once (reuse bytes for each product)
        placeholder_bytes = self._fetch_placeholder_bytes()

        # Generate 60 products
        used_names = set()

        for i in range(60):
            # Ensure unique name
            name = self._generate_name()
            while name in used_names:
                name = self._generate_name()
            used_names.add(name)

            # Indian Rupee prices: ₹499 to ₹4999
            price = Decimal(str(round(random.uniform(499, 4999), 2)))
            stock = random.randint(5, 100)
            description = random.choice(DESCRIPTIONS)

            product = Product(
                name=name,
                description=description,
                price=price,
                stock=stock,
            )
            if placeholder_bytes:
                try:
                    img = self._create_image_file(placeholder_bytes, f'product_{i + 1}.png')
                    product.image.save(f'product_{i + 1}.png', img, save=False)
                except Exception:
                    pass  # Skip image if invalid
            product.save()

        self.stdout.write(self.style.SUCCESS('Successfully created 60 products.'))
