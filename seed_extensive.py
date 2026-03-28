import os
import django
import random
import string
from datetime import date, timedelta
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from accounts.models import User, Subscription
from employees.models import Employee, AttendanceRecord
from office.models import Client, ClientPayment
from shop.models import Product, StockEntry, Sale, Parcel, AdCampaign

# Ensure we have a wide range of mock names and categories
def get_random_string(length=8):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))

first_names = ["Rahim", "Karim", "Abul", "Babul", "Kabul", "Salam", "Rafiq", "Jabbar", "Barkat", "Farid", "Hasan", "Jamal", "Kamal", "Lalon", "Momin", "Nasir", "Omi", "Pavel", "Qazi", "Raju", "Sumon", "Tarik", "Uddin", "Walid", "Zahir", "Sadman", "Nafis", "Sakib", "Mushfiq", "Tamim"]
last_names = ["Hossain", "Islam", "Rahman", "Ahmed", "Chowdhury", "Miah", "Uddin", "Ali", "Khan", "Sikder", "Haque", "Talukder", "Sarder", "Biswas", "Mallick", "Majumder", "Bhuiyan", "Kazi", "Mazumder", "Bapari"]

clients_companies = ["NexTech", "Creative IT", "Softify", "WebSolutions BD", "TechCare", "Pixel Perfect", "Digital Dynamics", "Innovate BD", "Cloud Systems", "Appify", "DataSoft", "BrainStation", "ThemeBite", "CodeCrafters", "BD IT Solutions"]
client_services = ["Web Development", "SEO", "Digital Marketing", "App Development", "Software Maintenance", "UI/UX Design", "Social Media Management", "Cloud Hosting", "IT Consultation", "Graphic Design"]

shop_products = [
    ("Wireless Mouse", 400, 750),
    ("Mechanical Keyboard", 1500, 2800),
    ("Gaming Headset", 1200, 2200),
    ("USB-C Hub", 600, 1100),
    ("Laptop Stand", 450, 900),
    ("Webcam 1080p", 1800, 3200),
    ("Bluetooth Speaker", 800, 1600),
    ("Power Bank 10000mAh", 900, 1400),
    ("Smart Watch", 2000, 3500),
    ("Wireless Earbuds", 1300, 2500),
    ("Gaming Monitor 24\"", 12000, 15500),
    ("RGB Mousepad", 350, 650),
    ("External HDD 1TB", 4000, 5200),
    ("SSD 500GB", 3200, 4100),
    ("RAM 8GB DDR4", 2500, 3300),
]

couriers = ["Pathao", "Steadfast", "RedX", "Paperfly", "E-Courier", "SA Paribahan", "Sundarban"]
parcel_statuses = ['pending', 'delivered', 'returned']

platforms = ["Facebook", "Google Search", "TikTok", "Instagram", "YouTube", "LinkedIn"]

def generate_date_span():
    return date.today() + timedelta(days=random.randint(-200, 60))

# 5 Office Users, 5 Shop Users
users_data = []
for i in range(1, 6):
    users_data.append((f"office{i}@synk.com", 'office', f"Office Owner {i}", f"Synk Office {i}"))
for i in range(1, 6):
    users_data.append((f"shop{i}@synk.com", 'shop', f"Shop Owner {i}", f"Synk Shop {i}"))

print("Starting extensive database seeding...")

for email, sub_type, name, b_name in users_data:
    user = User.objects.filter(email=email).first()
    if not user:
        user = User.objects.create_user(email=email, password='Password123!', full_name=name, business_name=b_name, subscription_type=sub_type)
    
    user.is_active_subscriber = True
    user.save()

    print(f"Seeding items for {email}...")

    # Seed 10-15 Employees per user
    current_employees = Employee.objects.filter(owner=user).count()
    if current_employees < 10:
        for _ in range(15 - current_employees):
            emp_name = f"{random.choice(first_names)} {random.choice(last_names)}"
            pos = random.choice(["Executive", "Manager", "Staff", "Support", "Developer", "Designer", "Sales Executive"])
            sal = random.randint(15000, 45000)
            join_d = generate_date_span() - timedelta(days=random.randint(100, 500))
            Employee.objects.create(owner=user, name=emp_name, position=pos, monthly_salary=sal, phone=f"017{random.randint(10000000, 99999999)}", join_date=join_d)

    if sub_type == 'office':
        # Clients (Office) - 15-20 clients
        current_clients = Client.objects.filter(owner=user).count()
        if current_clients < 15:
            for _ in range(20 - current_clients):
                c_name = random.choice(clients_companies) + " " + get_random_string(3).upper()
                c_service = random.choice(client_services)
                t_amount = random.randint(15000, 150000)
                p_amount = min(t_amount, random.randint(5000, t_amount + 10000))
                if p_amount > t_amount: p_amount = t_amount
                Client.objects.create(owner=user, name=c_name, email=f"contact@{get_random_string(5)}.com", phone=f"018{random.randint(10000000, 99999999)}", service=c_service, total_amount=t_amount, paid_amount=p_amount)

    if sub_type == 'shop':
        # Shop Products -> Create 10-15 products
        current_products = Product.objects.filter(owner=user).count()
        if current_products < 10:
            for p_name, bp, sp in shop_products:
                if not Product.objects.filter(owner=user, name=p_name).exists():
                    Product.objects.create(owner=user, name=p_name, buying_price=bp, selling_price=sp, stock=random.randint(10, 200))

        products = list(Product.objects.filter(owner=user))
        
        # Sales (Massive data: 2-5 sales every day for the last 90 days)
        # Check if sales exist
        if Sale.objects.filter(product__owner=user).count() < 3000:
            for d in range(-60, 200):
                sale_date = date.today() - timedelta(days=d)
                # Create 2 to 6 sales for this day
                for _ in range(random.randint(2, 6)):
                    prod = random.choice(products)
                    qty = random.randint(1, 10)
                    Sale.objects.create(product=prod, quantity=qty, buying_price=prod.buying_price, selling_price=prod.selling_price, date=sale_date)

        # Parcels -> 30-50 parcels
        current_parcels = Parcel.objects.filter(owner=user).count()
        if current_parcels < 30:
            for _ in range(40 - current_parcels):
                c_name = f"{random.choice(first_names)} {random.choice(last_names)}"
                courier = random.choice(couriers)
                c_price = random.randint(300, 2000)
                s_price = int(c_price * random.uniform(1.2, 1.8))
                status = random.choices(parcel_statuses, weights=[0.2, 0.7, 0.1])[0] # 70% delivered, 20% pending, 10% returned
                p_date = generate_date_span()
                Parcel.objects.create(owner=user, courier_name=courier, customer_name=c_name, tracking_number=get_random_string(10).upper(), cost_price=c_price, selling_price=s_price, status=status, date=p_date)

        # Ad Campaigns -> 5-10 campaigns
        current_ads = AdCampaign.objects.filter(owner=user).count()
        if current_ads < 5:
            for _ in range(8 - current_ads):
                ad_name = f"Promo {get_random_string(4).upper()} - {random.choice(['Sale', 'Offer', 'Discount'])}"
                plat = random.choice(platforms)
                s_date = generate_date_span()
                e_date = s_date + timedelta(days=random.randint(5, 30))
                spend = random.randint(1000, 10000)
                rev = int(spend * random.uniform(0.5, 4.0)) # Sometimes profitable, sometimes loss
                AdCampaign.objects.create(owner=user, name=ad_name, platform=plat, start_date=s_date, end_date=e_date, total_spend=spend, revenue=rev)

print("Extensive Seeding Completed successfully!")
