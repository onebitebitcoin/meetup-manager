from datetime import datetime

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.utils import timezone

from meetups.models import Meetup, MeetupUser, Registration


class Command(BaseCommand):
    help = 'Seed the database with sample data for August 2025'

    def handle(self, *args, **options):
        self.stdout.write('Clearing existing data...')
        Registration.objects.all().delete()
        Meetup.objects.all().delete()
        MeetupUser.objects.all().delete()
        User.objects.filter(is_superuser=False).delete()

        self.stdout.write('Creating users...')
        users_data = [
            {'username': 'john_smith', 'name': 'John Smith', 'email': 'john.smith@email.com', 'phone': '+1-555-0101', 'password': 'meetup123'},
            {'username': 'sarah_johnson', 'name': 'Sarah Johnson', 'email': 'sarah.johnson@email.com', 'phone': '+1-555-0102', 'password': 'meetup123'},
            {'username': 'mike_chen', 'name': 'Mike Chen', 'email': 'mike.chen@email.com', 'phone': '+1-555-0103', 'password': 'meetup123'},
            {'username': 'emily_davis', 'name': 'Emily Davis', 'email': 'emily.davis@email.com', 'phone': '+1-555-0104', 'password': 'meetup123'},
            {'username': 'alex_rodriguez', 'name': 'Alex Rodriguez', 'email': 'alex.rodriguez@email.com', 'phone': '+1-555-0105', 'password': 'meetup123'},
            {'username': 'lisa_wilson', 'name': 'Lisa Wilson', 'email': 'lisa.wilson@email.com', 'phone': '+1-555-0106', 'password': 'meetup123'},
            {'username': 'david_brown', 'name': 'David Brown', 'email': 'david.brown@email.com', 'phone': '+1-555-0107', 'password': 'meetup123'},
            {'username': 'jessica_miller', 'name': 'Jessica Miller', 'email': 'jessica.miller@email.com', 'phone': '+1-555-0108', 'password': 'meetup123'},
            {'username': 'admin_user', 'name': 'Admin User', 'email': 'admin@meetup.com', 'phone': '+1-555-0100', 'password': 'admin123', 'is_admin': True}
        ]

        users = []
        meetup_users = []
        for user_data in users_data:
            is_admin = user_data.pop('is_admin', False)
            password = user_data.pop('password')
            name = user_data.pop('name')
            phone = user_data.pop('phone')

            # Create Django User
            django_user = User.objects.create_user(
                username=user_data['username'],
                email=user_data['email'],
                password=password
            )
            users.append(django_user)

            # Create MeetupUser
            meetup_user = MeetupUser.objects.create(
                user=django_user,
                name=name,
                email=user_data['email'],
                phone=phone,
                is_admin=is_admin
            )
            meetup_users.append(meetup_user)

        self.stdout.write('Creating meetups for August 2025...')
        meetups_data = [
            {
                'name': 'Tech Talk: AI in Web Development',
                'description': 'Join us for an exciting discussion about integrating AI into modern web applications',
                'date_time': timezone.make_aware(datetime(2025, 8, 5, 18, 0)),
                'location': 'Tech Hub Downtown, Room 301',
                'max_participants': 25
            },
            {
                'name': 'JavaScript Workshop: Advanced React Patterns',
                'description': 'Deep dive into advanced React patterns and best practices for scalable applications',
                'date_time': timezone.make_aware(datetime(2025, 8, 8, 19, 0)),
                'location': 'Code Academy, Main Hall',
                'max_participants': 20
            },
            {
                'name': 'Startup Networking Event',
                'description': 'Connect with fellow entrepreneurs and discuss the latest trends in tech startups',
                'date_time': timezone.make_aware(datetime(2025, 8, 12, 17, 30)),
                'location': 'Innovation Center, Conference Room A',
                'max_participants': 40
            },
            {
                'name': 'Python Data Science Bootcamp',
                'description': 'Learn data analysis and visualization techniques using Python and popular libraries',
                'date_time': timezone.make_aware(datetime(2025, 8, 15, 14, 0)),
                'location': 'Data Science Institute, Lab 2',
                'max_participants': 15
            },
            {
                'name': 'Mobile App Development Meetup',
                'description': 'Showcase your mobile apps and get feedback from the community',
                'date_time': timezone.make_aware(datetime(2025, 8, 19, 18, 30)),
                'location': 'Mobile Dev Space, Presentation Room',
                'max_participants': 30
            },
            {
                'name': 'DevOps Best Practices Workshop',
                'description': 'Learn about CI/CD, containerization, and cloud deployment strategies',
                'date_time': timezone.make_aware(datetime(2025, 8, 22, 16, 0)),
                'location': 'Cloud Computing Center, Workshop Room',
                'max_participants': 18
            },
            {
                'name': 'UX/UI Design Critique Session',
                'description': 'Bring your designs for constructive feedback from experienced designers',
                'date_time': timezone.make_aware(datetime(2025, 8, 26, 19, 0)),
                'location': 'Design Studio, Creative Space',
                'max_participants': 22
            },
            {
                'name': 'Blockchain Technology Discussion',
                'description': 'Explore the latest developments in blockchain and cryptocurrency',
                'date_time': timezone.make_aware(datetime(2025, 8, 29, 17, 0)),
                'location': 'Fintech Hub, Main Auditorium',
                'max_participants': 35
            }
        ]

        meetups = []
        for i, meetup_data in enumerate(meetups_data):
            # Assign creators to meetups (first few users as creators)
            creator_idx = i % min(4, len(meetup_users) - 1)  # Don't assign admin as creator initially
            meetup_data['creator'] = meetup_users[creator_idx]
            meetup = Meetup.objects.create(**meetup_data)
            meetups.append(meetup)

        self.stdout.write('Creating registrations...')
        registrations_data = [
            (0, 0), (1, 0), (2, 0), (3, 0), (4, 0),  # Tech Talk: 5 registrations
            (0, 1), (5, 1), (6, 1),  # JavaScript Workshop: 3 registrations
            (1, 2), (2, 2), (3, 2), (4, 2), (5, 2), (6, 2), (7, 2),  # Startup Networking: 7 registrations
            (0, 3), (1, 3), (7, 3),  # Python Bootcamp: 3 registrations
            (2, 4), (3, 4), (4, 4), (5, 4), (6, 4),  # Mobile App: 5 registrations
            (0, 5), (7, 5),  # DevOps Workshop: 2 registrations
            (1, 6), (3, 6), (5, 6), (7, 6),  # UX/UI Design: 4 registrations
            (0, 7), (2, 7), (4, 7), (6, 7)  # Blockchain: 4 registrations
        ]

        registration_count = 0
        for user_idx, meetup_idx in registrations_data:
            Registration.objects.create(
                user=meetup_users[user_idx],
                meetup=meetups[meetup_idx]
            )
            registration_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully seeded database with:\n'
                f'- {len(meetup_users)} users (including 1 admin)\n'
                f'- {len(meetups)} meetups for August 2025\n'
                f'- {registration_count} registrations\n\n'
                f'Test accounts:\n'
                f'- Regular users: john_smith, sarah_johnson, etc. (password: meetup123)\n'
                f'- Admin user: admin_user (password: admin123)'
            )
        )
