from django.db import models
from django.utils import timezone


class Customer(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)


class Order(models.Model):
    class Status(models.TextChoices):
        PAID = 'paid', 'Paid'
        PENDING = 'pending', 'Pending'
        CANCELED = 'canceled', 'Canceled'

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='orders')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=Status.choices)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        indexes = [models.Index(fields=['status', 'created_at'])]
