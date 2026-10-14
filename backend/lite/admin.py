from django.contrib import admin

from . import models


@admin.register(models.ChatRoom)
class ChatRoomAdmin(admin.ModelAdmin):
    """채팅방은 Meetup·SeminarRequest 생성 시 자동으로 만들어지므로 admin에서는 추가·수정하지 않는다.
    삭제 권한은 막지 않는다. 막으면 Meetup 삭제 시 연쇄 삭제 권한 검사에 걸려 Meetup도 지울 수 없다."""

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


for model in (
    models.Member,
    models.Meetup,
    models.Rsvp,
    models.SeminarRequest,
    models.ChatMessage,
    models.MeetupRequest,
    models.RequestVote,
    models.LiteConfig,
):
    admin.site.register(model)
