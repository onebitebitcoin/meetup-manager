from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .models import ChatMessage, ChatRoom, Meetup, SeminarRequest


@receiver(post_save, sender=Meetup)
def ensure_meetup_room(sender, instance, created, raw=False, **kwargs):
    if created and not raw:
        ChatRoom.objects.get_or_create(meetup=instance, defaults={'kind': ChatRoom.Kind.MEETUP})


@receiver(post_save, sender=SeminarRequest)
def ensure_seminar_room(sender, instance, created, raw=False, **kwargs):
    if created and not raw:
        ChatRoom.objects.get_or_create(seminar=instance, defaults={'kind': ChatRoom.Kind.SEMINAR})


@receiver(post_delete, sender=ChatMessage)
def delete_attachment_file(sender, instance, **kwargs):
    if instance.attachment:
        instance.attachment.delete(save=False)
