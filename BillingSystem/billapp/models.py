from django.db import models
from decimal import Decimal

# Create your models here.

class Customer(models.Model):
    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email


class Product(models.Model):
    name = models.CharField(max_length=100)
    available_stocks = models.PositiveIntegerField(default=0)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    tax_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Bill(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        self.balance = round(self.total - self.paid_amount, 2)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Bill {self.id}"


class BillItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=0)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    bill = models.ForeignKey(Bill, on_delete=models.CASCADE, related_name="items")

    # def save(self, *args, **kwargs):
    #     self.total = self.price * self.quantity
    #     super().save(*args, **kwargs)

    def __str__(self):
        return f"Item {self.id}"


class Denomination(models.Model):
    value = models.PositiveIntegerField()
    count = models.PositiveIntegerField()
    bill = models.ForeignKey(
        Bill,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="denominations",
    )
    def __str__(self):
        return f"{self.value} x {self.count}"
