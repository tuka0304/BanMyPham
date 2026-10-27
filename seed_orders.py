import os
import sys
import django
import random
from datetime import datetime, timedelta

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_cosmetics_store.settings')
django.setup()

from store.models import User, Product, Order, OrderItem

# Get or create customer users
users = []
user_names = ['lan_huong', 'mai_anh', 'thu_ha', 'thanh_truc', 'ngoc_huyen', 'minh_chau', 'phuong_thao', 'khanh_vy', 'hoang_yen', 'quynh_nga']
for uname in user_names:
    u, created = User.objects.get_or_create(
        username=uname,
        defaults={
            'email': f'{uname}@gmail.com',
            'first_name': uname.replace('_', ' ').title(),
            'role': 'CUSTOMER'
        }
    )
    if created:
        u.set_password('123456')
        u.save()
    users.append(u)

# Define realistic basket patterns (Co-occurrence groups)
patterns = [
    # 1. Skincare Essential Combo (CeraVe + Thayers + La Roche-Posay Serum & Cream + Sunplay)
    [5, 4, 7, 6],
    [5, 6, 34],
    [5, 4, 34],
    [7, 6, 8],
    [5, 8, 9],
    [1, 4, 6],
    [5, 7, 6, 34],

    # 2. Eye Routine (Mascara Browit + Mi giả Idol / Butterfly + Kẻ viền mắt/môi)
    [24, 25],
    [24, 26],
    [24, 25, 26],
    [24, 25, 27],

    # 3. Lip Routine (Son chính + Chì kẻ viền môi + Son dưỡng / son bóng)
    [17, 27],
    [17, 20],
    [2, 27, 20],
    [15, 27, 19],
    [18, 28],
    [16, 27],
    [2, 20],
    [17, 27, 35],
    [19, 35],

    # 4. Face Base Makeup (Kem nền Nars / Cushion + Phấn phủ Strawberry Cupid + Má hồng Ballet)
    [3, 22, 29],
    [21, 22, 29],
    [23, 22],
    [3, 23],
    [21, 29],
    [3, 2, 22],

    # 5. Body & Hair Care (Sữa tắm Dove + Tẩy tế bào chết Dove + Dưỡng thể Vaseline + Body Oil Camioré + Kem ủ Dove)
    [37, 12, 10],
    [12, 14],
    [37, 12, 14],
    [11, 13, 32],
    [10, 14],
    [37, 12, 13],
    [11, 13],
    [13, 32],

    # 6. Perfume & Luxury (Aeterna Elixir + Gucci Flora / Lilith / Cindy Bloom)
    [40, 39],
    [31, 38],
    [30, 31],
    [40, 2, 17],
    [39, 17]
]

# Create ~75 orders with realistic variations
created_count = 0
base_date = datetime.now() - timedelta(days=60)

for i in range(75):
    # Select pattern or mix
    pattern = random.choice(patterns)
    # 70% chance to take pattern items, 30% chance to add 1 random item
    selected_prod_ids = list(pattern)
    if random.random() < 0.35:
        # maybe drop one item if > 2
        if len(selected_prod_ids) > 2 and random.random() < 0.5:
            selected_prod_ids.pop(random.randrange(len(selected_prod_ids)))
        # maybe add 1 random item
        rand_id = random.randint(1, 40)
        if rand_id not in selected_prod_ids:
            selected_prod_ids.append(rand_id)

    user = random.choice(users)
    order_date = base_date + timedelta(days=random.uniform(0, 58), hours=random.uniform(0, 23))

    order = Order.objects.create(
        user=user,
        receiver_name=user.first_name or user.username,
        shipping_address=f"{random.randint(12, 989)} Nguyễn Huệ, Quận 1, TP.HCM",
        receiver_phone=f"09{random.randint(10000000, 99999999)}",
        status=random.choice(['DELIVERED', 'DELIVERED', 'DELIVERED', 'SHIPPED', 'PROCESSING']),
        total_amount=0.0
    )
    # update date
    order.order_date = order_date
    
    total = 0.0
    for pid in selected_prod_ids:
        try:
            prod = Product.objects.get(id=pid)
            qty = random.choices([1, 2, 3], weights=[0.8, 0.15, 0.05])[0]
            price = prod.price
            total += price * qty
            OrderItem.objects.create(
                order=order,
                product=prod,
                price_at_order=price,
                quantity=qty
            )
        except Product.DoesNotExist:
            pass
            
    order.total_amount = total
    order.save()
    created_count += 1

print(f"Successfully generated {created_count} realistic historical orders!")
print(f"Total orders in DB: {Order.objects.count()}")
print(f"Total order items in DB: {OrderItem.objects.count()}")
