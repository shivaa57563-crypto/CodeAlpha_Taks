import os

from django.apps import AppConfig


class StoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'store'
    verbose_name = 'E-Commerce Store'

    def ready(self):
        """Create media and media/products folders automatically if they don't exist."""
        from django.conf import settings
        media_root = settings.MEDIA_ROOT
        if not os.path.exists(media_root):
            os.makedirs(media_root)
        media_products = os.path.join(media_root, 'products')
        if not os.path.exists(media_products):
            os.makedirs(media_products)
