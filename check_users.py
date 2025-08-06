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

print("=== DJANGO USERS ===")
for user in User.objects.all():
    print(f"ID: {user.id}, Username: {user.username}, Email: {user.email}, Staff: {user.is_staff}, Superuser: {user.is_superuser}")

print("\n=== MEETUP USERS ===")
for meetup_user in MeetupUser.objects.all():
    django_user_info = f"Django User: {meetup_user.user.username if meetup_user.user else 'None'}"
    print(f"ID: {meetup_user.id}, Name: {meetup_user.name}, Email: {meetup_user.email}, Admin: {meetup_user.is_admin}, {django_user_info}")