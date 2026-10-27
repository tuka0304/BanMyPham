import os
import json
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "django_cosmetics_store.settings")
django.setup()

from store.models import Product, Category

STATIC_IMG_DIR = os.path.join(os.path.dirname(__file__), 'static', 'images')
if not os.path.exists(STATIC_IMG_DIR):
    os.makedirs(STATIC_IMG_DIR)

with open('products.json', 'r', encoding='utf-8') as f:
    products = json.load(f)

for p_data in products:
    # Create or get category
    category, created = Category.objects.get_or_create(name=p_data['category_name'])
    
    # Copy image from seed_images to static
    src_img = os.path.join(os.path.dirname(__file__), 'seed_images', p_data['image_file'])
    dest_img = os.path.join(STATIC_IMG_DIR, p_data['image_file'])
    import shutil
    if os.path.exists(src_img):
        shutil.copy(src_img, dest_img)
    
    # Create or update product
    product, created = Product.objects.get_or_create(name=p_data['name'], defaults={
        'description': p_data['description'],
        'price': p_data['price'],
        'stock_quantity': p_data['stock_quantity'],
        'category': category,
        'image_url': f'/static/images/{p_data["image_file"]}'
    })
    
    if not created:
        product.description = p_data['description']
        product.price = p_data['price']
        product.stock_quantity = p_data['stock_quantity']
        product.category = category
        product.image_url = f'/static/images/{p_data["image_file"]}'
        product.save()

print("Products loaded successfully!")
