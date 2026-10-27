import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_cosmetics_store.settings')
django.setup()

from store.models import User, Cart

# Delete all users
User.objects.all().delete()
print("Deleted all old users.")

# Create admin user
admin_user = User.objects.create_superuser(
    username='admin',
    email='admin@aeterna.com',
    password='1'
)
admin_user.role = 'ADMIN'
admin_user.save()

# Create a cart for admin just in case
Cart.objects.create(user=admin_user)

print("Created new ADMIN account. Username: admin | Password: 1")
