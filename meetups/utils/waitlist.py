from ..models import Waitlist, Registration, Notification


def promote_from_waitlist(meetup):
    """
    Promotes the first person from the waitlist to the meetup when a spot becomes available.
    Creates a notification for the promoted user.
    """
    # Get the first person in the waitlist
    first_waitlist_entry = Waitlist.objects.filter(meetup=meetup).first()
    
    if first_waitlist_entry and not meetup.is_full:
        user = first_waitlist_entry.user
        
        # Create registration for the waitlisted user
        registration = Registration.objects.create(
            user=user,
            meetup=meetup
        )
        
        # Create notification for the promoted user
        Notification.objects.create(
            user=user,
            title=f"{meetup.name} 모임 참가 확정",
            message=f"대기 중이던 '{meetup.name}' 모임에 자리가 생겨서 참가가 확정되었습니다.\n\n"
                   f"일시: {meetup.date_time.strftime('%Y년 %m월 %d일 %H:%M')}\n"
                   f"장소: {meetup.location}\n"
                   f"설명: {meetup.description}\n\n"
                   f"이제 더 이상 대기하실 필요가 없습니다. 모임에서 뵙겠습니다!",
            notification_type='waitlist_promotion',
            meetup=meetup
        )
        
        # Remove from waitlist
        first_waitlist_entry.delete()
        
        print(f"Promoted {user.name} from waitlist to {meetup.name} and created notification")
        
        return registration
    
    return None