"""
Management command to create sample products in the database.
Run with: python manage.py create_sample_products
"""

from django.core.management.base import BaseCommand
from store.models import Product


class Command(BaseCommand):
    help = 'Creates sample products for the e-commerce store'

    def handle(self, *args, **options):
        sample_products = [
            {
                'name': 'Wireless Headphones',
                'description': 'High-quality wireless headphones with noise cancellation and 20-hour battery life.',
                'price': 79.99,
            },
            {
                'name': 'Smart Watch',
                'description': 'Fitness tracking, heart rate monitor, and smartphone notifications. Water resistant.',
                'price': 149.99,
            },
            {
                'name': 'Portable Charger',
                'description': '10000mAh power bank with fast charging. Compact and lightweight for travel.',
                'price': 29.99,
            },
            {
                'name': 'USB-C Hub',
                'description': '7-in-1 hub with HDMI, USB 3.0, and SD card reader. Perfect for laptops.',
                'price': 49.99,
            },
            {
                'name': 'Mechanical Keyboard',
                'description': 'RGB backlit mechanical keyboard with Cherry MX switches. Ideal for gaming and typing.',
                'price': 89.99,
            },
            {
                'name': 'Wireless Mouse',
                'description': 'Ergonomic wireless mouse with 6 programmable buttons and long battery life.',
                'price': 39.99,
            },
        ]

        created = 0
        for data in sample_products:
            product, was_created = Product.objects.get_or_create(
                name=data['name'],
                defaults={
                    'description': data['description'],
                    'price': data['price'],
                }
            )
            if was_created:
                created += 1

        self.stdout.write(self.style.SUCCESS(f'Created {created} new sample products. Total products: {Product.objects.count()}'))
