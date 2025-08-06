#!/usr/bin/env python
import os
import sys
import django

# Add the project directory to Python path
sys.path.append('/Users/nsw/Desktop/dev/training')

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'meetup_backend.settings')

# Setup Django
django.setup()

from django.contrib.auth.models import User
from meetups.models import MeetupUser

# Update the existing admin user (ID: 15)
try:
    # Get the Django user
    django_user = User.objects.get(id=15, username='admin')
    
    # Update password and make sure it's staff/superuser
    django_user.set_password('admin123')
    django_user.is_staff = True
    django_user.is_superuser = True
    django_user.save()
    
    # Get the corresponding MeetupUser (ID: 23)
    meetup_user = MeetupUser.objects.get(id=23, email='admin@example.com')
    meetup_user.is_admin = True
    meetup_user.save()
    
    print("="*50)
    print("ADMIN ACCOUNT READY!")
    print("="*50)
    print(f"Username: {django_user.username}")
    print(f"Email: {django_user.email}")
    print(f"Password: admin123")
    print(f"Display Name: {meetup_user.name}")
    print("Admin privileges: YES")
    print("Django Staff: YES")
    print("Django Superuser: YES")
    print("="*50)
    print("You can now login using:")
    print("- Username: admin")
    print("- Password: admin123")
    print("OR")
    print(f"- Email: {django_user.email}")
    print("- Password: admin123")
    print("="*50)
    
except Exception as e:
    print(f"Error updating admin user: {e}")
    import traceback
    traceback.print_exc()