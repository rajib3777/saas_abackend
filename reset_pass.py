import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from accounts.models import User

# Reset password for login
u = User.objects.get(email='shop1@synk.com')
u.set_password('shop123')
u.is_active_subscriber = True
u.subscription_type = 'shop'
u.role = 'admin'
u.save()
print(f"Password reset for {u.email}")
print(f"role: {u.role}, type: {u.subscription_type}, active: {u.is_active_subscriber}")
