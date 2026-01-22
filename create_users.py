import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'payment.settings')
django.setup()

from emi.models import User

try:
    if not User.objects.filter(email='admin@example.com').exists():
        User.objects.create_superuser(
            email='admin@example.com',
            full_name='Admin User',
            phone_number='1234567890',
            password='adminpassword123',
            role='Admin'
        )
        print("Superuser 'admin@example.com' created successfully.")
    else:
        print("Superuser 'admin@example.com' already exists.")

    if not User.objects.filter(email='student@example.com').exists():
        User.objects.create_user(
            email='student@example.com',
            full_name='Student User',
            phone_number='0987654321',
            password='studentpassword123',
            role='Student'
        )
        print("Student user 'student@example.com' created successfully.")
    else:
        print("Student user 'student@example.com' already exists.")

except Exception as e:
    print(f"Error: {e}")
