"""
Admin panel configuration - manage products and orders from Django admin.
"""

from django.contrib import admin
from django.utils.html import format_html
from .models import Product, Cart, CartItem, Order, OrderItem


# Inline: show order items when viewing an order
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['product', 'quantity', 'price', 'get_subtotal']

    def get_subtotal(self, obj):
        return obj.get_subtotal()
    get_subtotal.short_description = 'Subtotal'


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """Admin view for products - list, filter, search, image upload."""
    list_display = ['name', 'price', 'stock', 'image_preview', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'description']
    fields = ['name', 'description', 'price', 'stock', 'image']

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" style="object-fit:cover;border-radius:4px;" />', obj.image.url)
        return format_html('<span style="color:#999;">No image</span>')
    image_preview.short_description = 'Image'


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'total', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['user__username', 'id']
    inlines = [OrderItemInline]


# Optional: register Cart and CartItem for debugging
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(OrderItem)
