import os
import uuid

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator, MaxValueValidator, MinValueValidator
from django.db import models


class MeetupUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='meetup_profile', null=True, blank=True)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True, null=True)
    lightning_address = models.CharField(max_length=255, blank=True, null=True)
    is_admin = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

def validate_image_file_size(file):
    """Validate that the uploaded file is not too large"""
    limit = 5 * 1024 * 1024  # 5MB
    if file.size > limit:
        raise ValidationError(f'파일 크기가 너무 큽니다. 최대 {limit // (1024*1024)}MB까지 업로드 가능합니다.')

def meetup_image_path(instance, filename):
    """Generate upload path for meetup images"""
    # Get file extension
    ext = filename.split('.')[-1].lower()
    # Generate filename based on meetup name and timestamp
    import time
    timestamp = str(int(time.time()))
    safe_name = "".join(c for c in instance.name if c.isalnum() or c in (' ', '-', '_')).rstrip()
    safe_name = safe_name.replace(' ', '_')[:50]  # Limit length
    new_filename = f"{safe_name}_{timestamp}.{ext}"
    return os.path.join('meetups', new_filename)

class Meetup(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    date_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True)
    location = models.CharField(max_length=200)
    max_participants = models.IntegerField()
    current_participants = models.IntegerField(default=0)
    creator = models.ForeignKey(MeetupUser, on_delete=models.CASCADE, related_name='created_meetups', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # Image fields
    image = models.ImageField(
        upload_to=meetup_image_path,
        blank=True,
        null=True,
        help_text="Upload an image for the meetup",
        validators=[
            validate_image_file_size,
            FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'gif', 'webp'])
        ]
    )
    image_url = models.URLField(blank=True, null=True, help_text="Or provide an image URL")

    # Hashtags field - stored as comma-separated string
    hashtags = models.TextField(blank=True, null=True, help_text="Comma-separated hashtags (e.g., #개발,#네트워킹,#스타트업)")

    def __str__(self):
        return self.name

    @property
    def is_full(self):
        return self.current_participants >= self.max_participants

    @property
    def available_spots(self):
        return self.max_participants - self.current_participants

    @property
    def image_display_url(self):
        """Return the image URL - either from uploaded file or external URL"""
        if self.image:
            return self.image.url
        elif self.image_url:
            return self.image_url
        return ''

    @property
    def hashtags_list(self):
        """Return hashtags as a list"""
        if self.hashtags:
            return [tag.strip() for tag in self.hashtags.split(',') if tag.strip()]
        return []

    def add_hashtag(self, hashtag):
        """Add a hashtag to the meetup"""
        hashtag = hashtag.strip()
        if not hashtag.startswith('#'):
            hashtag = '#' + hashtag

        current_hashtags = self.hashtags_list
        if hashtag not in current_hashtags:
            current_hashtags.append(hashtag)
            self.hashtags = ','.join(current_hashtags)

    def remove_hashtag(self, hashtag):
        """Remove a hashtag from the meetup"""
        hashtag = hashtag.strip()
        if not hashtag.startswith('#'):
            hashtag = '#' + hashtag

        current_hashtags = self.hashtags_list
        if hashtag in current_hashtags:
            current_hashtags.remove(hashtag)
            self.hashtags = ','.join(current_hashtags) if current_hashtags else None

class Registration(models.Model):
    user = models.ForeignKey(MeetupUser, on_delete=models.CASCADE)
    meetup = models.ForeignKey(Meetup, on_delete=models.CASCADE)
    registered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'meetup')

    def __str__(self):
        return f"{self.user.name} - {self.meetup.name}"

    def clean(self):
        if self.meetup.is_full:
            raise ValidationError("이 모임의 정원이 가득 찼습니다.")

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        if is_new and self.meetup.is_full:
            raise ValidationError("이 모임의 정원이 가득 찼습니다.")

        super().save(*args, **kwargs)

        if is_new:
            self.meetup.current_participants += 1
            self.meetup.save()

    def delete(self, *args, **kwargs):
        meetup = self.meetup
        super().delete(*args, **kwargs)
        meetup.current_participants -= 1
        meetup.save()

        # Check for waitlist and promote the first person
        if not meetup.is_full:
            from .utils import promote_from_waitlist
            promote_from_waitlist(meetup)


class Waitlist(models.Model):
    user = models.ForeignKey(MeetupUser, on_delete=models.CASCADE)
    meetup = models.ForeignKey(Meetup, on_delete=models.CASCADE)
    waitlisted_at = models.DateTimeField(auto_now_add=True)
    position = models.IntegerField()

    class Meta:
        unique_together = ('user', 'meetup')
        ordering = ['position']

    def __str__(self):
        return f"{self.user.name} - {self.meetup.name} (Position: {self.position})"

    def save(self, *args, **kwargs):
        if not self.position:
            # Auto-assign position based on waitlist length
            max_position = Waitlist.objects.filter(meetup=self.meetup).aggregate(
                max_pos=models.Max('position')
            )['max_pos']
            self.position = (max_position or 0) + 1
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        meetup = self.meetup
        position = self.position
        super().delete(*args, **kwargs)

        # Adjust positions of remaining waitlist entries
        Waitlist.objects.filter(
            meetup=meetup,
            position__gt=position
        ).update(position=models.F('position') - 1)


class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('waitlist_promotion', '대기열 승격'),
        ('meetup_reminder', '모임 알림'),
        ('general', '일반 알림'),
    ]

    user = models.ForeignKey(MeetupUser, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES, default='general')
    meetup = models.ForeignKey(Meetup, on_delete=models.CASCADE, null=True, blank=True, related_name='notifications')
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.name} - {self.title}"


def task_submission_path(instance, filename):
    """Generate upload path for task submission files"""
    import time
    ext = filename.split('.')[-1].lower()
    timestamp = str(int(time.time()))
    new_filename = f"task_{instance.task.id}_{instance.user.id}_{timestamp}.{ext}"
    return os.path.join('task_submissions', new_filename)


class Task(models.Model):
    meetup = models.ForeignKey(Meetup, on_delete=models.CASCADE, related_name='tasks')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    deadline = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.meetup.name}"

    @property
    def is_deadline_soon(self):
        """Check if deadline is within 3 days"""
        from datetime import timedelta

        from django.utils import timezone
        if not self.deadline:
            return False
        now = timezone.now()
        return now < self.deadline <= now + timedelta(days=3)

    @property
    def is_past_deadline(self):
        """Check if deadline has passed"""
        from django.utils import timezone
        return self.deadline < timezone.now()


class TaskSubmission(models.Model):
    SUBMISSION_STATUS = [
        ('pending', '검토 대기'),
        ('approved', '승인'),
        ('rejected', '반려'),
    ]

    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='submissions')
    user = models.ForeignKey(MeetupUser, on_delete=models.CASCADE, related_name='task_submissions')
    message = models.TextField()
    link = models.URLField(blank=True, null=True)
    file = models.FileField(
        upload_to=task_submission_path,
        blank=True,
        null=True,
        validators=[
            validate_image_file_size,
            FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'gif', 'pdf', 'doc', 'docx'])
        ]
    )
    status = models.CharField(max_length=20, choices=SUBMISSION_STATUS, default='pending')
    submitted_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('task', 'user')
        ordering = ['-submitted_at']

    def __str__(self):
        return f"{self.user.name} - {self.task.title}"


class Review(models.Model):
    """밋업 후기 모델"""
    meetup = models.ForeignKey(Meetup, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(MeetupUser, on_delete=models.CASCADE, related_name='reviews')
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    content = models.TextField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('meetup', 'user')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.name} - {self.meetup.name} ({self.rating}점)"


class MeetupPaymentLink(models.Model):
    """모임 결제 링크 - BOLT11 인보이스를 공개 URL로 공유"""
    token = models.UUIDField(default=uuid.uuid4, unique=True, db_index=True)
    meetup = models.ForeignKey(Meetup, on_delete=models.CASCADE, related_name='payment_links')
    bolt11 = models.TextField()
    amount_sats = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def __str__(self):
        return f"{self.meetup.name} - {self.token}"

    @property
    def is_expired(self):
        from django.utils import timezone
        return timezone.now() >= self.expires_at
