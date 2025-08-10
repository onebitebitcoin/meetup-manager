from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
import os

class MeetupUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='meetup_profile', null=True, blank=True)
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
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
        super().delete(*args, **kwargs)
        self.meetup.current_participants -= 1
        self.meetup.save()
