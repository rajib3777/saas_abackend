import os
import django
import random
import string
from datetime import date, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from accounts.models import User, Subscription
from employees.models import Employee, AttendanceRecord
from office.models import Client, ClientPayment
from shop.models import Product, StockEntry, Sale, Parcel, AdCampaign

def get_random_string(length=8):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))

# 5 Office Users, 5 Shop Users
users_data = []
for i in range(1, 6):
    users_data.append((f"office{i}@synk.com", 'office', f"Office Owner {i}", f"Synk Office {i}"))
for i in range(1, 6):
    users_data.append((f"shop{i}@synk.com", 'shop', f"Shop Owner {i}", f"Synk Shop {i}"))

for email, sub_type, name, b_name in users_data:
    user = User.objects.filter(email=email).first()
    if not user:
        user = User.objects.create_user(email=email, password='Password123!', full_name=name, business_name=b_name, subscription_type=sub_type)
    
    user.is_active_subscriber = True
    user.save()

    # Employees (All)
    if not Employee.objects.filter(owner=user).exists():
        for j in range(1, 4):
            Employee.objects.create(owner=user, name=f"Staff {j}", position="Executive", monthly_salary=random.randint(15000, 25000))

    if sub_type == 'office':
        if not Client.objects.filter(owner=user).exists():
            Client.objects.create(owner=user, name="Creative Agency", service="Marketing", total_amount=50000, paid_amount=30000)
            Client.objects.create(owner=user, name="Tech Solutions", service="IT Support", total_amount=20000, paid_amount=20000)
    else:
        # Products
        if not Product.objects.filter(owner=user).exists():
            p1 = Product.objects.create(owner=user, name="Wireless Mouse", buying_price=400, selling_price=750, stock=50)
            p2 = Product.objects.create(owner=user, name="Mechanical Keyboard", buying_price=1500, selling_price=2800, stock=20)
            
            # Sales (Last 7 days)
            for d in range(7):
                Sale.objects.create(product=p1, quantity=random.randint(1, 5), buying_price=400, selling_price=750, date=date.today()-timedelta(days=d))
                Sale.objects.create(product=p2, quantity=random.randint(0, 2), buying_price=1500, selling_price=2800, date=date.today()-timedelta(days=d))

        # Parcels
        if not Parcel.objects.filter(owner=user).exists():
            Parcel.objects.create(owner=user, courier_name="Pathao", customer_name="Rahim", cost_price=500, selling_price=800, status='delivered')
            Parcel.objects.create(owner=user, courier_name="Steadfast", customer_name="Karim", cost_price=1200, selling_price=1600, status='pending')
            Parcel.objects.create(owner=user, courier_name="Redx", customer_name="Abul", cost_price=300, selling_price=500, status='returned')

        # Ad Campaigns
        if not AdCampaign.objects.filter(owner=user).exists():
            AdCampaign.objects.create(
                owner=user, name="Eid Dhamaka", platform="Facebook", 
                start_date=date.today()-timedelta(days=30), end_date=date.today(), 
                total_spend=5000, revenue=15000
            )
            AdCampaign.objects.create(
                owner=user, name="Summer Sale", platform="TikTok", 
                start_date=date.today()-timedelta(days=15), end_date=date.today()+timedelta(days=15), 
                total_spend=2000, revenue=4500
            )

print("Comprehensive Seeding Completed!")
