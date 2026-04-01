from django.db import models, transaction
from django.db.models import F
from django.utils import timezone
from accounts.models import User


class Product(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=200)
    image = models.ImageField(upload_to='products/', null=True, blank=True)
    buying_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    stock = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.owner.email})"


class StockEntry(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='stock_entries')
    quantity = models.IntegerField()
    date = models.DateField(default=timezone.now)
    note = models.CharField(max_length=200, blank=True)

    def save(self, *args, **kwargs):
        with transaction.atomic():
            super().save(*args, **kwargs)
            # Direct QuerySet update is the most robust and atomic way in serverless
            Product.objects.filter(pk=self.product_id).update(stock=F('stock') + self.quantity)


class Sale(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='sales')
    quantity = models.PositiveIntegerField()
    selling_price = models.DecimalField(max_digits=10, decimal_places=2)
    buying_price = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField(default=timezone.now)

    @property
    def profit(self):
        return (self.selling_price - self.buying_price) * self.quantity

    def __str__(self):
        return f"{self.product.name} x{self.quantity} on {self.date}"


class Parcel(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_transit', 'In Transit'),
        ('out_for_delivery', 'Out for Delivery'),
        ('delivered', 'Delivered'),
        ('returned', 'Returned'),
        ('cancelled', 'Cancelled'),
    ]
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='parcels')
    courier_name = models.CharField(max_length=100)
    tracking_number = models.CharField(max_length=100, blank=True)
    customer_name = models.CharField(max_length=150)
    cost_price = models.DecimalField(max_digits=10, decimal_places=2)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    added_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='processed_parcels')
    date = models.DateField(default=timezone.now)
    
    # Auto-tracking fields
    is_auto_tracking = models.BooleanField(default=False)
    next_check = models.DateTimeField(null=True, blank=True)
    last_sync_time = models.DateTimeField(null=True, blank=True)
    last_sync_status = models.CharField(max_length=255, null=True, blank=True)


    @property
    def profit(self):
        return self.selling_price - self.cost_price

    def __str__(self):
        return f"{self.customer_name} - {self.courier_name} ({self.status})"


class AdCampaign(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ad_campaigns')
    name = models.CharField(max_length=200)
    platform = models.CharField(max_length=100, default='Facebook')
    start_date = models.DateField()
    end_date = models.DateField()
    total_spend = models.DecimalField(max_digits=12, decimal_places=2)
    revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.platform})"

class CourierWithdrawal(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='courier_withdrawals')
    courier_name = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.courier_name} - {self.amount} on {self.date}"
