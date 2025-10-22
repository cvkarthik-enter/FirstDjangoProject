from django.contrib import admin
from .models import Product, PriceHistory

admin.site.register(Product)
admin.site.register(PriceHistory)