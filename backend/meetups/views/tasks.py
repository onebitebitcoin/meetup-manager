from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from ..models import Registration, Task, TaskSubmission
from ..serializers import TaskSerializer, TaskSubmissionSerializer
from .helpers import (
    ensure_authenticated,
    ensure_meetup_creator,
    get_meetup_or_response,
    get_meetup_user_or_response,
    parse_datetime_iso,
)


def get_task_or_response(task_id, message='과제를 찾을 수 없습니다'):
    """Retrieve a Task instance by ID."""
    try:
        return Task.objects.get(id=task_id), None
    except Task.DoesNotExist:
        return None, Response({'error': message}, status=status.HTTP_404_NOT_FOUND)


def ensure_meetup_participant(meetup, meetup_user, message='모임 참가자만 접근할 수 있습니다'):
    """Verify the user is a registered participant of the meetup."""
    if Registration.objects.filter(meetup=meetup, user=meetup_user).exists():
        return None
    return Response({'error': message}, status=status.HTTP_403_FORBIDDEN)


@api_view(['GET', 'POST'])
def meetup_tasks(request, meetup_id):
    """List tasks for meetup (GET) or create new task (POST)"""
    meetup, error = get_meetup_or_response(meetup_id)
    if error:
        return error

    auth_error = ensure_authenticated(request)
    if auth_error:
        return auth_error

    meetup_user, profile_error = get_meetup_user_or_response(request)
    if profile_error:
        return profile_error

    if request.method == 'GET':
        # Participants and creator can view tasks
        is_creator = meetup.creator == meetup_user
        is_participant = Registration.objects.filter(meetup=meetup, user=meetup_user).exists()

        if not is_creator and not is_participant:
            return Response(
                {'error': '모임 참가자 또는 생성자만 접근할 수 있습니다'},
                status=status.HTTP_403_FORBIDDEN
            )

        tasks = Task.objects.filter(meetup=meetup)
        serializer = TaskSerializer(tasks, many=True, context={'request': request})
        return Response({'tasks': serializer.data}, status=status.HTTP_200_OK)

    # POST - Create task (creator only)
    creator_error = ensure_meetup_creator(meetup, meetup_user)
    if creator_error:
        return creator_error

    title = request.data.get('title')
    description = request.data.get('description', '')
    deadline_str = request.data.get('deadline')

    if not title:
        return Response({'error': '과제 제목을 입력해주세요'}, status=status.HTTP_400_BAD_REQUEST)

    deadline, error = parse_datetime_iso(deadline_str)
    if error:
        return error

    task = Task.objects.create(
        meetup=meetup,
        title=title,
        description=description,
        deadline=deadline
    )
    serializer = TaskSerializer(task, context={'request': request})
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['GET', 'PUT', 'DELETE'])
def task_detail(request, task_id):
    """Get, update, or delete a specific task"""
    task, error = get_task_or_response(task_id)
    if error:
        return error

    auth_error = ensure_authenticated(request)
    if auth_error:
        return auth_error

    meetup_user, profile_error = get_meetup_user_or_response(request)
    if profile_error:
        return profile_error

    if request.method == 'GET':
        # Participants and creator can view
        is_creator = task.meetup.creator == meetup_user
        is_participant = Registration.objects.filter(meetup=task.meetup, user=meetup_user).exists()

        if not is_creator and not is_participant:
            return Response({'error': '권한이 없습니다'}, status=status.HTTP_403_FORBIDDEN)

        serializer = TaskSerializer(task, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    # PUT/DELETE - creator only
    creator_error = ensure_meetup_creator(task.meetup, meetup_user)
    if creator_error:
        return creator_error

    if request.method == 'PUT':
        task.title = request.data.get('title', task.title)
        task.description = request.data.get('description', task.description)
        if 'deadline' in request.data:
            deadline, error = parse_datetime_iso(request.data.get('deadline'))
            if error:
                return error
            task.deadline = deadline
        task.save()
        serializer = TaskSerializer(task, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    # DELETE
    task.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['POST'])
def submit_task(request, task_id):
    """Submit task completion (participant only)"""
    task, error = get_task_or_response(task_id)
    if error:
        return error

    auth_error = ensure_authenticated(request)
    if auth_error:
        return auth_error

    meetup_user, profile_error = get_meetup_user_or_response(request)
    if profile_error:
        return profile_error

    participant_error = ensure_meetup_participant(task.meetup, meetup_user)
    if participant_error:
        return participant_error

    # Check if already submitted
    if TaskSubmission.objects.filter(task=task, user=meetup_user).exists():
        return Response({'error': '이미 제출한 과제입니다'}, status=status.HTTP_400_BAD_REQUEST)

    # Handle both JSON and form-data
    message = request.data.get('message', '') or request.POST.get('message', '')
    link = request.data.get('link') or request.POST.get('link')
    file = request.FILES.get('file')

    if not message:
        return Response({'error': '메시지를 입력해주세요'}, status=status.HTTP_400_BAD_REQUEST)

    if not link and not file:
        return Response({'error': '링크 또는 파일을 첨부해주세요'}, status=status.HTTP_400_BAD_REQUEST)

    submission = TaskSubmission.objects.create(
        task=task,
        user=meetup_user,
        message=message,
        link=link if link else None,
        file=file if file else None
    )
    serializer = TaskSubmissionSerializer(submission, context={'request': request})
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['GET'])
def task_submissions(request, task_id):
    """List all submissions for a task (creator only)"""
    task, error = get_task_or_response(task_id)
    if error:
        return error

    auth_error = ensure_authenticated(request)
    if auth_error:
        return auth_error

    meetup_user, profile_error = get_meetup_user_or_response(request)
    if profile_error:
        return profile_error

    creator_error = ensure_meetup_creator(task.meetup, meetup_user)
    if creator_error:
        return creator_error

    submissions = TaskSubmission.objects.filter(task=task).select_related('user')
    serializer = TaskSubmissionSerializer(submissions, many=True, context={'request': request})
    return Response({'submissions': serializer.data}, status=status.HTTP_200_OK)


@api_view(['PUT'])
def review_submission(request, submission_id):
    """Approve or reject a submission (creator only)"""
    try:
        submission = TaskSubmission.objects.get(id=submission_id)
    except TaskSubmission.DoesNotExist:
        return Response({'error': '제출물을 찾을 수 없습니다'}, status=status.HTTP_404_NOT_FOUND)

    auth_error = ensure_authenticated(request)
    if auth_error:
        return auth_error

    meetup_user, profile_error = get_meetup_user_or_response(request)
    if profile_error:
        return profile_error

    creator_error = ensure_meetup_creator(submission.task.meetup, meetup_user)
    if creator_error:
        return creator_error

    new_status = request.data.get('status')
    if new_status not in ['approved', 'rejected']:
        return Response({'error': '유효하지 않은 상태입니다'}, status=status.HTTP_400_BAD_REQUEST)

    submission.status = new_status
    submission.reviewed_at = timezone.now()
    submission.save()

    serializer = TaskSubmissionSerializer(submission, context={'request': request})
    return Response(serializer.data, status=status.HTTP_200_OK)
