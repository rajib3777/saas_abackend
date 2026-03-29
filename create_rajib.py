import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from accounts.models import User

user, created = User.objects.get_or_create(email='rajib.somadhansoft@gmail.com', defaults={'full_name': 'Rajib', 'password': 'Password123!', 'subscription_type': 'shop'})
if not created:
    user.set_password('Password123!')
    user.subscription_type = 'shop'

user.is_superuser = True
user.is_staff = True
user.is_active_subscriber = True
user.save()

print('User ensured with password Password123!')
