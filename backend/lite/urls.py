from django.urls import path

from . import views

urlpatterns = [
    path('api/lite/members/', views.MemberCreateView.as_view()),
    path('api/lite/me/', views.MeView.as_view()),
    path('api/lite/host/claim/', views.HostClaimView.as_view()),
    path('api/lite/home/', views.HomeView.as_view()),
    path('api/lite/meetups/', views.MeetupCreateView.as_view()),
    path('api/lite/meetups/<int:meetup_id>/', views.MeetupDetailView.as_view()),
    path('api/lite/meetups/<int:meetup_id>/rsvp/', views.RsvpView.as_view()),
    path('api/lite/rooms/<int:room_id>/messages/', views.RoomMessagesView.as_view()),
    path('api/lite/rooms/<int:room_id>/files/', views.RoomFilesView.as_view()),
    path('api/lite/admin/meetups/', views.AdminMeetupListView.as_view()),
    path('api/lite/admin/meetups/<int:meetup_id>/', views.AdminMeetupDetailView.as_view()),
    path('api/lite/admin/meetups/<int:meetup_id>/cancel/', views.AdminMeetupCancelView.as_view()),
    path('api/lite/admin/meetups/<int:meetup_id>/members/<int:member_id>/', views.AdminMemberRemoveView.as_view()),
    path('api/lite/rooms/<int:room_id>/messages/<int:message_id>/', views.AdminMessageDeleteView.as_view()),
    path('api/lite/rooms/<int:room_id>/pin/', views.AdminPinView.as_view()),
    path('api/lite/link-preview/', views.LinkPreviewView.as_view()),
    path('api/lite/seminar/', views.SeminarView.as_view()),
    path('api/lite/seminars/<int:seminar_id>/confirm/', views.SeminarConfirmView.as_view()),
    path('api/lite/requests/', views.RequestListView.as_view()),
    path('api/lite/requests/<int:request_id>/vote/', views.RequestVoteView.as_view()),
]
