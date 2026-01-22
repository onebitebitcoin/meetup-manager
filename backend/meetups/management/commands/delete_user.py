from django.core.management.base import BaseCommand
from django.db import transaction
from django.contrib.auth.models import User
from meetups.models import MeetupUser, Registration, Waitlist, Notification


class Command(BaseCommand):
    help = 'Safely delete a user by email or username, handling all foreign key relationships'

    def add_arguments(self, parser):
        parser.add_argument('identifier', type=str, help='Email or username of the user to delete')
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force deletion even if user is admin',
        )

    def handle(self, *args, **options):
        identifier = options['identifier']
        force = options['force']
        
        # Try to find user by email or username
        user = None
        meetup_user = None
        
        try:
            # Try Django User first
            if '@' in identifier:
                user = User.objects.get(email=identifier)
            else:
                user = User.objects.get(username=identifier)
            
            # Get linked MeetupUser
            try:
                meetup_user = user.meetup_profile
            except MeetupUser.DoesNotExist:
                pass
                
        except User.DoesNotExist:
            # Try MeetupUser directly
            try:
                if '@' in identifier:
                    meetup_user = MeetupUser.objects.get(email=identifier)
                else:
                    meetup_user = MeetupUser.objects.get(name=identifier)
            except MeetupUser.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'User not found: {identifier}')
                )
                return

        if not meetup_user and not user:
            self.stdout.write(
                self.style.ERROR(f'User not found: {identifier}')
            )
            return

        # Check if admin user
        is_admin = False
        if meetup_user:
            is_admin = meetup_user.is_admin
        if user:
            is_admin = is_admin or user.is_staff or user.is_superuser

        if is_admin and not force:
            self.stdout.write(
                self.style.ERROR('Cannot delete admin user. Use --force to override.')
            )
            return

        # Show what will be deleted
        self.stdout.write(f'Preparing to delete user: {identifier}')
        
        if meetup_user:
            # Count related objects
            created_meetups = meetup_user.created_meetups.count()
            registrations = Registration.objects.filter(user=meetup_user).count()
            waitlist_entries = Waitlist.objects.filter(user=meetup_user).count()
            notifications = Notification.objects.filter(user=meetup_user).count()
            
            self.stdout.write(f'  - MeetupUser ID: {meetup_user.id}')
            self.stdout.write(f'  - Created meetups: {created_meetups} (will set creator to None)')
            self.stdout.write(f'  - Registrations: {registrations} (will be deleted)')
            self.stdout.write(f'  - Waitlist entries: {waitlist_entries} (will be deleted)')
            self.stdout.write(f'  - Notifications: {notifications} (will be deleted)')
            
        if user:
            self.stdout.write(f'  - Django User ID: {user.id}')

        # Confirm deletion
        confirm = input('Are you sure you want to delete this user? (yes/no): ')
        if confirm.lower() != 'yes':
            self.stdout.write('Deletion cancelled.')
            return

        # Perform deletion with transaction
        try:
            with transaction.atomic():
                if meetup_user:
                    # 1. Handle meetups created by this user - set creator to None
                    created_count = meetup_user.created_meetups.update(creator=None)
                    if created_count > 0:
                        self.stdout.write(f'Updated {created_count} meetups to remove creator reference')
                    
                    # 2. Delete registrations (will auto-update meetup participant counts)
                    registrations = Registration.objects.filter(user=meetup_user)
                    reg_count = 0
                    for registration in registrations:
                        registration.delete()  # This will properly update meetup.current_participants
                        reg_count += 1
                    if reg_count > 0:
                        self.stdout.write(f'Deleted {reg_count} registrations')
                    
                    # 3. Delete waitlist entries (will auto-update positions)
                    waitlist_entries = Waitlist.objects.filter(user=meetup_user)
                    waitlist_count = 0
                    for waitlist_entry in waitlist_entries:
                        waitlist_entry.delete()  # This will properly update positions
                        waitlist_count += 1
                    if waitlist_count > 0:
                        self.stdout.write(f'Deleted {waitlist_count} waitlist entries')
                    
                    # 4. Delete notifications
                    notif_count = Notification.objects.filter(user=meetup_user).count()
                    if notif_count > 0:
                        Notification.objects.filter(user=meetup_user).delete()
                        self.stdout.write(f'Deleted {notif_count} notifications')
                
                # 5. Finally delete the user
                if user and meetup_user:
                    # Delete Django User (this will cascade to MeetupUser)
                    user.delete()
                    self.stdout.write(f'Deleted Django User and linked MeetupUser')
                elif user:
                    # Delete standalone Django User
                    user.delete()
                    self.stdout.write(f'Deleted Django User')
                elif meetup_user:
                    # Delete standalone MeetupUser
                    meetup_user.delete()
                    self.stdout.write(f'Deleted MeetupUser')
                
            self.stdout.write(
                self.style.SUCCESS(f'Successfully deleted user: {identifier}')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error deleting user: {str(e)}')
            )