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

# Admin credentials
username = 'admin'
email = 'admin@meetup.com'
password = 'admin123!'
name = 'Admin User'

try:
    # Create Django User
    if User.objects.filter(username=username).exists():
        print(f"User '{username}' already exists, updating...")
        user = User.objects.get(username=username)
        user.email = email
        user.set_password(password)
        user.is_staff = True
        user.is_superuser = True
        user.save()
    else:
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )
        user.is_staff = True
        user.is_superuser = True
        user.save()
        print(f"Django User '{username}' created successfully!")
    
    # Create or update MeetupUser
    if MeetupUser.objects.filter(email=email).exists():
        print(f"MeetupUser with email '{email}' already exists, updating...")
        meetup_user = MeetupUser.objects.get(email=email)
        meetup_user.user = user
        meetup_user.name = name
        meetup_user.is_admin = True
        meetup_user.save()
    else:
        meetup_user = MeetupUser.objects.create(
            user=user,
            name=name,
            email=email,
            phone='',
            is_admin=True
        )
        print(f"MeetupUser '{name}' created successfully!")
    
    print("\n" + "="*50)
    print("ADMIN ACCOUNT CREATED SUCCESSFULLY!")
    print("="*50)
    print(f"Username: {username}")
    print(f"Email: {email}")
    print(f"Password: {password}")
    print(f"Name: {name}")
    print("Admin privileges: YES")
    print("="*50)
    
except Exception as e:
    print(f"Error creating admin user: {e}")
    import traceback
    traceback.print_exc()