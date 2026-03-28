from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from .models import User, Subscription


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['email', 'full_name', 'subscription_type', 'is_active_subscriber', 'date_joined', 'give_access_btn']
    list_filter = ['subscription_type', 'is_active_subscriber', 'is_staff']
    search_fields = ['email', 'full_name', 'business_name']
    ordering = ['-date_joined']

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('full_name', 'phone', 'business_name')}),
        ('Subscription', {'fields': ('subscription_type', 'is_active_subscriber')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'full_name', 'subscription_type', 'password1', 'password2'),
        }),
    )

    def give_access_btn(self, obj):
        if not obj.is_active_subscriber:
            return format_html(
                '<a class="button" href="/admin/accounts/user/{}/give-access/" '
                'style="background:#7C3AED;color:white;padding:4px 10px;border-radius:4px;text-decoration:none;">'
                '✅ Give Access</a>', obj.pk
            )
        return format_html('<span style="color:green;font-weight:bold;">✔ Active</span>')
    give_access_btn.short_description = 'Access Control'

    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom = [path('<int:pk>/give-access/', self.admin_site.admin_view(self.give_access), name='give-access')]
        return custom + urls

    def give_access(self, request, pk):
        from django.http import HttpResponseRedirect
        from django.contrib import messages
        user = User.objects.get(pk=pk)
        user.is_active_subscriber = True
        user.save()
        messages.success(request, f"✅ Access granted to {user.email}")
        return HttpResponseRedirect('/admin/accounts/user/')


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ['user', 'unique_id', 'payment_amount', 'duration_months', 'transaction_id', 'start_date', 'is_active']
    list_filter = ['is_active']
    search_fields = ['user__email', 'unique_id', 'transaction_id']


# Style the admin site
admin.site.site_header = "🚀 SaaS Platform Admin"
admin.site.site_title = "SaaS Admin"
admin.site.index_title = "Business Management Dashboard"
