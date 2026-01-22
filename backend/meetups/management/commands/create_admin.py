from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from meetups.models import MeetupUser


class Command(BaseCommand):
    help = 'Create an admin user for the meetup system'

    def add_arguments(self, parser):
        parser.add_argument('--username', type=str, help='Admin username', default='admin')
        parser.add_argument('--email', type=str, help='Admin email', default='admin@example.com')
        parser.add_argument('--password', type=str, help='Admin password', default='admin123')
        parser.add_argument('--name', type=str, help='Admin display name', default='Administrator')

    def handle(self, *args, **options):
        username = options['username']
        email = options['email']
        password = options['password']
        name = options['name']

        # Check if user already exists
        if User.objects.filter(username=username).exists():
            self.stdout.write(
                self.style.WARNING(f'User with username "{username}" already exists')
            )
            return

        # Create Django user
        django_user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        # Create MeetupUser with admin privileges
        MeetupUser.objects.create(
            user=django_user,
            name=name,
            email=email,
            is_admin=True
        )

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created admin user: {username}\n'
                f'Email: {email}\n'
                f'Password: {password}\n'
                f'Display Name: {name}'
            )
        )
