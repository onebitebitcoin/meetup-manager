import logging
import mimetypes
import os

from django.http import FileResponse
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from ..models import Task, TaskSubmission
from ..serializers import TaskSerializer, TaskSubmissionSerializer
from .helpers import (
    APIResponse,
    get_object_or_error,
    parse_datetime_iso,
    require_meetup_creator_or_participant,
    require_profile,
)

logger = logging.getLogger(__name__)


@api_view(['GET', 'POST'])
@require_meetup_creator_or_participant('meetup_id')
def meetup_tasks(request, meetup_id):
    """밋업 과제 목록 조회(GET) 또는 생성(POST)"""
    meetup = request.meetup
    meetup_user = request.meetup_user

    if request.method == 'GET':
        tasks = Task.objects.filter(meetup=meetup)
        serializer = TaskSerializer(tasks, many=True, context={'request': request})
        return APIResponse.success({'tasks': serializer.data})

    # POST: 생성자만 과제 생성 가능
    if meetup.creator != meetup_user:
        return APIResponse.forbidden('모임 생성자만 과제를 생성할 수 있습니다')

    title = request.data.get('title')
    description = request.data.get('description', '')
    deadline_str = request.data.get('deadline')

    if not title:
        return APIResponse.error('과제 제목을 입력해주세요')

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
@require_profile
def task_detail(request, task_id):
    """과제 상세 조회/수정/삭제"""
    task, error = get_object_or_error(Task, '과제를 찾을 수 없습니다', id=task_id)
    if error:
        return error

    meetup_user = request.meetup_user
    meetup = task.meetup

    # 생성자 또는 참가자 여부 확인
    from ..models import Registration
    is_creator = meetup.creator == meetup_user
    is_participant = Registration.objects.filter(meetup=meetup, user=meetup_user).exists()

    if request.method == 'GET':
        if not is_creator and not is_participant:
            return APIResponse.forbidden()
        serializer = TaskSerializer(task, context={'request': request})
        return Response(serializer.data)

    # PUT/DELETE: 생성자만 가능
    if not is_creator:
        return APIResponse.forbidden('모임 생성자만 접근할 수 있습니다')

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
        return Response(serializer.data)

    # DELETE
    task.delete()
    return APIResponse.no_content()


@api_view(['POST'])
@require_profile
def submit_task(request, task_id):
    """과제 제출 (참가자만)"""
    task, error = get_object_or_error(Task, '과제를 찾을 수 없습니다', id=task_id)
    if error:
        return error

    meetup_user = request.meetup_user

    # 참가자 확인
    from ..models import Registration
    if not Registration.objects.filter(meetup=task.meetup, user=meetup_user).exists():
        return APIResponse.forbidden('모임 참가자만 접근할 수 있습니다')

    # 이미 제출했는지 확인
    if TaskSubmission.objects.filter(task=task, user=meetup_user).exists():
        return APIResponse.error('이미 제출한 과제입니다')

    # JSON과 form-data 모두 처리
    message = request.data.get('message', '') or request.POST.get('message', '')
    link = request.data.get('link') or request.POST.get('link')
    file = request.FILES.get('file')

    if not message:
        return APIResponse.error('메시지를 입력해주세요')

    if not link and not file:
        return APIResponse.error('링크 또는 파일을 첨부해주세요')

    submission = TaskSubmission.objects.create(
        task=task,
        user=meetup_user,
        message=message,
        link=link if link else None,
        file=file if file else None
    )
    if submission.file:
        logger.info(
            "Task submission file saved: submission_id=%s task_id=%s user_id=%s name=%s path=%s size=%s content_type=%s",
            submission.id,
            task.id,
            meetup_user.id,
            os.path.basename(submission.file.name),
            submission.file.name,
            getattr(submission.file, 'size', None),
            getattr(file, 'content_type', None),
        )
    else:
        logger.info(
            "Task submission created without file: submission_id=%s task_id=%s user_id=%s",
            submission.id,
            task.id,
            meetup_user.id,
        )
    serializer = TaskSubmissionSerializer(submission, context={'request': request})
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@require_profile
def task_submissions(request, task_id):
    """과제 제출물 목록 조회 (생성자만)"""
    task, error = get_object_or_error(Task, '과제를 찾을 수 없습니다', id=task_id)
    if error:
        return error

    meetup_user = request.meetup_user

    if task.meetup.creator != meetup_user:
        return APIResponse.forbidden('모임 생성자만 접근할 수 있습니다')

    submissions = TaskSubmission.objects.filter(task=task).select_related('user')
    serializer = TaskSubmissionSerializer(submissions, many=True, context={'request': request})
    return APIResponse.success({'submissions': serializer.data})


@api_view(['GET'])
@require_profile
def download_submission_file(request, submission_id):
    """제출 파일 다운로드/열기 (생성자 또는 제출자 본인만)"""
    submission, error = get_object_or_error(TaskSubmission, '제출물을 찾을 수 없습니다', id=submission_id)
    if error:
        return error

    meetup_user = request.meetup_user
    is_creator = submission.task.meetup.creator == meetup_user
    is_submitter = submission.user == meetup_user

    if not is_creator and not is_submitter:
        logger.warning(
            "Task submission file access denied: submission_id=%s requester_id=%s task_id=%s owner_id=%s",
            submission.id,
            meetup_user.id,
            submission.task_id,
            submission.user_id,
        )
        return APIResponse.forbidden('모임 생성자 또는 제출자 본인만 파일을 열 수 있습니다')

    if not submission.file:
        logger.warning(
            "Task submission file missing field: submission_id=%s requester_id=%s",
            submission.id,
            meetup_user.id,
        )
        return APIResponse.not_found('첨부 파일이 없습니다')

    if not submission.file.name:
        logger.warning(
            "Task submission file invalid name: submission_id=%s requester_id=%s",
            submission.id,
            meetup_user.id,
        )
        return APIResponse.not_found('첨부 파일 경로가 올바르지 않습니다')

    disposition = (request.GET.get('disposition') or 'inline').lower()
    if disposition not in ['inline', 'attachment']:
        return APIResponse.error('disposition 값은 inline 또는 attachment 여야 합니다')
    as_attachment = disposition == 'attachment'

    try:
        file_handle = submission.file.open('rb')
    except FileNotFoundError:
        logger.error(
            "Task submission file not found on disk: submission_id=%s requester_id=%s storage_name=%s",
            submission.id,
            meetup_user.id,
            submission.file.name,
        )
        return APIResponse.not_found('파일을 찾을 수 없습니다')
    except Exception:
        logger.exception(
            "Task submission file open failed: submission_id=%s requester_id=%s storage_name=%s",
            submission.id,
            meetup_user.id,
            submission.file.name,
        )
        return APIResponse.error('파일을 여는 중 오류가 발생했습니다', status.HTTP_500_INTERNAL_SERVER_ERROR)

    filename = os.path.basename(submission.file.name)
    content_type, _ = mimetypes.guess_type(filename)

    logger.info(
        "Task submission file served: submission_id=%s requester_id=%s task_id=%s owner_id=%s disposition=%s file=%s exists=%s",
        submission.id,
        meetup_user.id,
        submission.task_id,
        submission.user_id,
        disposition,
        submission.file.name,
        True,
    )

    response = FileResponse(
        file_handle,
        as_attachment=as_attachment,
        filename=filename,
        content_type=content_type or 'application/octet-stream',
    )
    response['X-Content-Type-Options'] = 'nosniff'
    return response


@api_view(['PUT'])
@require_profile
def review_submission(request, submission_id):
    """제출물 승인/거절 (생성자만)"""
    submission, error = get_object_or_error(TaskSubmission, '제출물을 찾을 수 없습니다', id=submission_id)
    if error:
        return error

    meetup_user = request.meetup_user

    if submission.task.meetup.creator != meetup_user:
        return APIResponse.forbidden('모임 생성자만 접근할 수 있습니다')

    new_status = request.data.get('status')
    if new_status not in ['approved', 'rejected']:
        return APIResponse.error('유효하지 않은 상태입니다')

    submission.status = new_status
    submission.reviewed_at = timezone.now()
    submission.save()

    serializer = TaskSubmissionSerializer(submission, context={'request': request})
    return Response(serializer.data)
