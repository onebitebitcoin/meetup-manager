from django.contrib import admin

from . import models

for model in (
    models.Member,
    models.Meetup,
    models.Rsvp,
    models.SeminarRequest,
    models.ChatRoom,
    models.ChatMessage,
    models.MeetupRequest,
    models.RequestVote,
    models.LiteConfig,
):
    admin.site.register(model)
