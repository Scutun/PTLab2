from django.contrib import admin

from .models import Product, Purchase


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'quantity', 'initial_quantity',
                    'price_increased')


@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    list_display = ('date', 'person', 'product', 'count', 'price', 'address')
    list_filter = ('product',)
