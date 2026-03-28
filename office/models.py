from django.db import models
from accounts.models import User


class Client(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='clients')
    name = models.CharField(max_length=150)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    service = models.CharField(max_length=200, blank=True)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    paid_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def due_amount(self):
        return self.total_amount - self.paid_amount

    def __str__(self):
        return f"{self.name} ({self.owner.email})"


class ClientPayment(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    note = models.TextField(blank=True)
    date = models.DateField(auto_now_add=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.client.paid_amount = sum(p.amount for p in self.client.payments.all())
        self.client.save()

    def __str__(self):
        return f"{self.client.name} - {self.amount}"
