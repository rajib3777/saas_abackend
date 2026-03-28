from django.contrib import admin
from .models import Product, StockEntry, Sale, Parcel, AdCampaign


from django.utils.html import format_html

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'owner', 'buying_price', 'selling_price', 'stock', 'image_tag']
    search_fields = ['name', 'owner__email']

    def image_tag(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="width: 50px; height:50px; object-fit: cover; border-radius: 5px;" />', obj.image.url)
        return "No Image"
    image_tag.short_description = 'Image'


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ['product', 'quantity', 'selling_price', 'buying_price', 'profit', 'date']


@admin.register(Parcel)
class ParcelAdmin(admin.ModelAdmin):
    list_display = ['customer_name', 'courier_name', 'status', 'profit', 'date']
    list_filter = ['status']


@admin.register(AdCampaign)
class AdCampaignAdmin(admin.ModelAdmin):
    list_display = ['name', 'platform', 'start_date', 'end_date', 'total_spend']

admin.site.register(StockEntry)
