# app/models.py

from django.db import models
from django.contrib.auth.models import User


class Product(models.Model):
    name = models.CharField(max_length=100, unique=True)
    current_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f'{self.name} {self.current_price}'


class PriceHistory(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='history')
    old_price = models.DecimalField(max_digits=10, decimal_places=2)
    updated_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)


    class Meta:
        ordering = ['-updated_at']


    def __str__(self):
        user_display = self.updated_by.username if self.updated_by else "Sentinel"
        return f"{self.product.name} changed to ₹{self.old_price} on {self.updated_at.strftime('%Y-%m-%d %H:%M')} by {user_display}"
