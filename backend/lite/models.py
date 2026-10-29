import secrets

from django.db import models


def generate_token():
    return secrets.token_urlsafe(32)


# 도착 코드는 없앴지만 0001_initial 마이그레이션이 이 함수를 참조한다
def generate_checkin_code():
    return f'{secrets.randbelow(10000):04d}'


class Member(models.Model):
    name = models.CharField(max_length=20, unique=True)
    token = models.CharField(max_length=64, unique=True, default=generate_token)
    is_host = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class MeetupRequest(models.Model):
    class Period(models.TextChoices):
        THIS_MONTH = 'this_month', '이번 달'
        NEXT_MONTH = 'next_month', '다음 달'
        ANY = 'any', '상관없음'

    class Status(models.TextChoices):
        OPEN = 'open', '진행 중'
        DONE = 'done', '완료'

    title = models.CharField(max_length=60)
    preferred_period = models.CharField(max_length=20, choices=Period.choices, default=Period.ANY)
    created_by = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='requests')
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.OPEN)
    meetup = models.ForeignKey(
        'Meetup', on_delete=models.SET_NULL, null=True, blank=True, related_name='fulfilled_requests'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Meetup(models.Model):
    title = models.CharField(max_length=80)
    description = models.TextField(blank=True)
    # 어떤 분께 맞는 모임인지 한 줄로 적는다 (예: 비트코인을 처음 접하는 분)
    audience = models.CharField(max_length=100, blank=True, default='')
    starts_at = models.DateTimeField()
    location = models.CharField(max_length=100)
    capacity = models.PositiveIntegerField()
    # 썸네일 원본 주소. 기존 앱 모임은 업로드 파일의 /media/ 경로 또는 외부 URL을 그대로 담는다.
    image_url = models.CharField(max_length=500, blank=True, default='')
    # image_url을 줄여 만든 WebP 썸네일의 /media/ 주소. 화면에는 원본 대신 이것만 보낸다.
    thumb_url = models.CharField(max_length=200, blank=True, default='')
    from_request = models.ForeignKey(
        MeetupRequest, on_delete=models.SET_NULL, null=True, blank=True, related_name='opened_meetups'
    )
    legacy_meetup_id = models.IntegerField(unique=True, null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Rsvp(models.Model):
    class Status(models.TextChoices):
        GOING = 'going', '참석'
        MAYBE = 'maybe', '미정'
        NO = 'no', '불참'

    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='rsvps')
    meetup = models.ForeignKey(Meetup, on_delete=models.CASCADE, related_name='rsvps')
    status = models.CharField(max_length=10, choices=Status.choices)
    removed_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=['member', 'meetup'], name='lite_rsvp_unique_member_meetup')]


class SeminarRequest(models.Model):
    class Mode(models.TextChoices):
        ONLINE = 'online', '온라인'
        OFFLINE = 'offline', '오프라인'

    class Status(models.TextChoices):
        GUIDE = 'guide', '안내 중'
        RECEIVED = 'received', '접수'
        CONFIRMED = 'confirmed', '확정'

    member = models.OneToOneField(Member, on_delete=models.CASCADE, related_name='seminar')
    mode = models.CharField(max_length=10, choices=Mode.choices, null=True, blank=True)
    topic = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.GUIDE)
    created_at = models.DateTimeField(auto_now_add=True)


class ChatRoom(models.Model):
    class Kind(models.TextChoices):
        MEETUP = 'meetup', '모임'
        SEMINAR = 'seminar', '세미나'

    kind = models.CharField(max_length=10, choices=Kind.choices)
    meetup = models.OneToOneField(Meetup, on_delete=models.CASCADE, null=True, blank=True, related_name='room')
    seminar = models.OneToOneField(
        SeminarRequest, on_delete=models.CASCADE, null=True, blank=True, related_name='room'
    )
    pinned_message = models.ForeignKey(
        'ChatMessage', on_delete=models.SET_NULL, null=True, blank=True, related_name='+'
    )


class ChatMessage(models.Model):
    class Kind(models.TextChoices):
        USER = 'user', '사용자'
        SYSTEM = 'system', '시스템'
        GUIDE = 'guide', '안내'

    class AttachmentKind(models.TextChoices):
        IMAGE = 'image', '이미지'
        FILE = 'file', '파일'

    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    member = models.ForeignKey(Member, on_delete=models.SET_NULL, null=True, blank=True, related_name='messages')
    kind = models.CharField(max_length=10, choices=Kind.choices, default=Kind.USER)
    body = models.TextField(max_length=1000, blank=True)
    attachment = models.FileField(upload_to='lite/chat/%Y/%m/', blank=True)
    attachment_name = models.CharField(max_length=120, blank=True)
    attachment_size = models.PositiveIntegerField(null=True, blank=True)
    attachment_kind = models.CharField(max_length=5, choices=AttachmentKind.choices, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['id']
        indexes = [models.Index(fields=['room', 'id'])]


class RoomRead(models.Model):
    """회원이 채팅방에서 어디까지 읽었는지(마지막으로 받은 메시지 id). 안 읽은 대화 수 배지에 쓴다."""

    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='room_reads')
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='reads')
    last_read_id = models.PositiveBigIntegerField(default=0)

    class Meta:
        constraints = [models.UniqueConstraint(fields=['member', 'room'], name='lite_roomread_unique_member_room')]


class RequestVote(models.Model):
    request = models.ForeignKey(MeetupRequest, on_delete=models.CASCADE, related_name='votes')
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='votes')

    class Meta:
        constraints = [models.UniqueConstraint(fields=['request', 'member'], name='lite_vote_unique_request_member')]


SEMINAR_GUIDE_1 = '운영자와 1:1로 진행하는 세미나예요.\n온라인·오프라인 모두 가능해요.'
SEMINAR_GUIDE_2 = '제안 주제\n· 비트코인 셀프 커스터디\n· 비트코인 공부\n· AI 공부\n다른 주제도 괜찮아요.'
SEMINAR_GUIDE_3 = '원하는 주제와 희망 날짜·시간을 적어 주세요. 온라인·오프라인 중 편한 쪽도 함께 알려 주세요.'


class LiteConfig(models.Model):
    """싱글턴 설정(pk=1). Django admin에서 수정한다."""

    vote_threshold = models.PositiveIntegerField(default=5)
    # 꺼져 있으면 운영자가 아닌 방문자는 목록만 보고 참석·채팅·세미나·요청을 쓸 수 없다(오픈 전 잠금)
    is_open = models.BooleanField(default=False)
    seminar_guide_1 = models.TextField(default=SEMINAR_GUIDE_1)
    seminar_guide_2 = models.TextField(default=SEMINAR_GUIDE_2)
    seminar_guide_3 = models.TextField(default=SEMINAR_GUIDE_3)
    seminar_guide_4 = models.TextField(default='접수됐어요. 여기서 일정을 안내해 드릴게요.')
    join_guide = models.TextField(default='신청 완료! 공지는 여기서 안내해요.')

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def get(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    def __str__(self):
        return 'LITE 설정'
