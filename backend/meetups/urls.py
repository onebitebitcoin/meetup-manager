from django.urls import path

from . import views

urlpatterns = [
    path('api/csrf/', views.get_csrf_token, name='csrf-token'),
    path('api/auth/register/', views.register_new_user, name='auth-register'),
    path('api/auth/check-username/', views.check_username_availability, name='check-username'),
    path('api/auth/login/', views.login_user, name='auth-login'),
    path('api/auth/logout/', views.logout_user, name='auth-logout'),
    path('api/auth/change-password/', views.change_password, name='auth-change-password'),
    path('api/users/', views.MeetupUserListCreateView.as_view(), name='user-list-create'),
    path('api/meetups/', views.MeetupListCreateView.as_view(), name='meetup-list-create'),
    path('api/meetups/<int:pk>/', views.meetup_detail, name='meetup-detail'),
    path('api/meetups/<int:meetup_id>/registrations/', views.meetup_registrations, name='meetup-registrations'),
    path('api/meetups/<int:meetup_id>/register/', views.register_for_meetup, name='register-for-meetup'),
    path('api/meetups/<int:meetup_id>/unregister/', views.unregister_from_meetup, name='unregister-from-meetup'),
    path('api/meetups/<int:meetup_id>/status/', views.check_registration_status, name='check-registration-status'),
    path('api/my-meetups/', views.user_meetups, name='user-meetups'),
    path('api/my-attended-meetups/', views.user_attended_meetups, name='user-attended-meetups'),
    path('api/registrations/', views.RegistrationListView.as_view(), name='registration-list'),
    path('api/register/', views.register_user, name='register-user'),
    path('api/health/', views.health_check, name='health-check'),

    # Admin endpoints
    path('api/admin/users/', views.admin_users_list, name='admin-users-list'),
    path('api/admin/meetups/', views.admin_meetups_list, name='admin-meetups-list'),
    path('api/admin/users/<int:user_id>/delete/', views.admin_delete_user, name='admin-delete-user'),
    path('api/admin/meetups/<int:meetup_id>/delete/', views.admin_delete_meetup, name='admin-delete-meetup'),
    path('api/admin/users/<int:user_id>/toggle-admin/', views.admin_toggle_user_admin, name='admin-toggle-user-admin'),
    path('api/admin/statistics/', views.admin_statistics, name='admin-statistics'),
    path('api/admin/users/<int:user_id>/reset-password/', views.admin_reset_user_password, name='admin-reset-password'),

    # Manual participant management
    path('api/meetups/<int:meetup_id>/add-participant/', views.add_participant_by_email, name='add-participant-by-email'),
    path('api/meetups/<int:meetup_id>/remove-participant/<int:registration_id>/', views.remove_participant, name='remove-participant'),

    # Waitlist endpoints
    path('api/meetups/<int:meetup_id>/waitlist/', views.add_to_waitlist, name='add-to-waitlist'),
    path('api/meetups/<int:meetup_id>/waitlist/remove/', views.remove_from_waitlist, name='remove-from-waitlist'),
    path('api/meetups/<int:meetup_id>/waitlist/status/', views.check_waitlist_status, name='check-waitlist-status'),
    path('api/meetups/<int:meetup_id>/waitlist/list/', views.meetup_waitlist, name='meetup-waitlist'),
    path('api/my-waitlists/', views.user_waitlists, name='user-waitlists'),

    # Notification endpoints
    path('api/notifications/', views.user_notifications, name='user-notifications'),
    path('api/notifications/<int:notification_id>/read/', views.mark_notification_read, name='mark-notification-read'),
    path('api/notifications/mark-all-read/', views.mark_all_notifications_read, name='mark-all-notifications-read'),
    path('api/notifications/<int:notification_id>/delete/', views.delete_notification, name='delete-notification'),
    path('api/meetups/<int:meetup_id>/send-notification/', views.send_notification_to_participants, name='send-notification-to-participants'),

    # Task endpoints
    path('api/meetups/<int:meetup_id>/tasks/', views.meetup_tasks, name='meetup-tasks'),
    path('api/tasks/<int:task_id>/', views.task_detail, name='task-detail'),
    path('api/tasks/<int:task_id>/submissions/', views.task_submissions, name='task-submissions'),
    path('api/tasks/<int:task_id>/submit/', views.submit_task, name='submit-task'),
    path('api/submissions/<int:submission_id>/review/', views.review_submission, name='review-submission'),
    path('api/submissions/<int:submission_id>/file/', views.download_submission_file, name='submission-file-download'),

    # Review endpoints
    path('api/reviews/', views.review_feed, name='review-feed'),
    path('api/reviews/recent/', views.recent_reviews, name='recent-reviews'),
    path('api/meetups/<int:meetup_id>/review/', views.meetup_review, name='meetup-review'),
    path('api/meetups/<int:meetup_id>/reviews/', views.meetup_reviews_list, name='meetup-reviews-list'),
]
