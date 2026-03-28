from django.contrib import admin
from .models import Client, ClientPayment


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ['name', 'owner', 'total_amount', 'paid_amount', 'due_amount', 'created_at']
    search_fields = ['name', 'owner__email']


@admin.register(ClientPayment)
class ClientPaymentAdmin(admin.ModelAdmin):
    list_display = ['client', 'amount', 'date']
