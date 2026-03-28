import os
import django
import random
from datetime import date, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from shop.models import Product, Sale
from accounts.models import User

for user in User.objects.filter(subscription_type='shop'):
    products = list(Product.objects.filter(owner=user))
    if not products:
        continue
    
    # Generate June dates. Today is March 25. June 1 is roughly +68 days, June 30 is +97 days.
    for d in range(68, 97):
        sale_date = date.today() + timedelta(days=d)
        
        # Create 2 to 5 sales per day in June
        for _ in range(random.randint(2, 5)):
            p = random.choice(products)
            qty = random.randint(1, 5)
            s_price = float(p.selling_price) * random.uniform(0.9, 1.1)
            Sale.objects.create(
                product=p, 
                quantity=qty, 
                selling_price=s_price, 
                buying_price=p.buying_price, 
                date=sale_date
            )

print("June data successfully injected for all shops!")
