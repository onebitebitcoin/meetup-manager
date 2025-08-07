from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

class MeetupUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='meetup_profile', null=True, blank=True)
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    is_admin = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

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

    def __str__(self):
        return self.name

    @property
    def is_full(self):
        return self.current_participants >= self.max_participants

    @property
    def available_spots(self):
        return self.max_participants - self.current_participants

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
