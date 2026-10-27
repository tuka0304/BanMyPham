import os
import sys
import django
import json

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_cosmetics_store.settings')
django.setup()

from store.models import Category, Product

with open('products.json', 'r', encoding='utf-8') as f:
    products_data = json.load(f)

for p_data in products_data:
    cat, created = Category.objects.get_or_create(name=p_data['category_name'])
    
    product, p_created = Product.objects.update_or_create(
        name=p_data['name'],
        defaults={
            'slug': p_data.get('slug'),
            'brand': p_data.get('brand'),
            'skin_type': p_data.get('skin_type'),
            'description': p_data.get('description'),
            'detailed_description': p_data.get('detailed_description'),
            'ingredients': p_data.get('ingredients'),
            'usage_instructions': p_data.get('usage_instructions'),
            'allergy_warning': p_data.get('allergy_warning'),
            'meta_title': p_data.get('meta_title'),
            'meta_description': p_data.get('meta_description'),
            'keywords': p_data.get('keywords'),
            'price': p_data['price'],
            'stock_quantity': p_data['stock_quantity'],
            'image_url': f"/static/images/{p_data['image_file']}",
            'category': cat
        }
    )
    print(f"Loaded {product.name}")

print("Data loaded successfully!")
