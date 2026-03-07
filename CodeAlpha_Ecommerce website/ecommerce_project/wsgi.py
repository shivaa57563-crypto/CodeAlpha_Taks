"""
WSGI config for e-commerce project.
Used for deployment with production servers.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce_project.settings')

application = get_wsgi_application()
