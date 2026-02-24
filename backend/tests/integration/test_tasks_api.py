"""
Integration tests for tasks API endpoints.
"""
from datetime import timedelta

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from django.utils import timezone

from meetups.models import Task, TaskSubmission


@pytest.mark.django_db
class TestTaskListAPI:
    """Tests for task list endpoint."""

    def test_list_meetup_tasks(self, authenticated_client, create_meetup, create_task, create_registration):
        """Test listing tasks for a meetup."""
        client, user, meetup_user = authenticated_client()
        meetup = create_meetup()
        create_registration(meetup_user, meetup)  # 참가자여야 조회 가능
        create_task(meetup, title='Task 1')
        create_task(meetup, title='Task 2')

        url = reverse('meetup-tasks', kwargs={'meetup_id': meetup.id})
        response = client.get(url)

        assert response.status_code == 200
        assert len(response.data['tasks']) == 2

    def test_list_meetup_tasks_empty(self, authenticated_client, create_meetup, create_registration):
        """Test listing tasks when none exist."""
        client, user, meetup_user = authenticated_client()
        meetup = create_meetup()
        create_registration(meetup_user, meetup)  # 참가자여야 조회 가능

        url = reverse('meetup-tasks', kwargs={'meetup_id': meetup.id})
        response = client.get(url)

        assert response.status_code == 200
        assert len(response.data['tasks']) == 0


@pytest.mark.django_db
class TestTaskCreateAPI:
    """Tests for task creation endpoint."""

    def test_create_task(self, authenticated_client, create_meetup):
        """Test creating a task."""
        client, user, meetup_user = authenticated_client(is_admin=True)
        meetup = create_meetup(creator=meetup_user)

        url = reverse('meetup-tasks', kwargs={'meetup_id': meetup.id})
        data = {
            'title': 'New Task',
            'description': 'Task description',
            'deadline': (timezone.now() + timedelta(days=3)).isoformat()
        }

        response = client.post(url, data, format='json')
        assert response.status_code == 201
        assert Task.objects.filter(title='New Task').exists()


@pytest.mark.django_db
class TestTaskDetailAPI:
    """Tests for task detail endpoint."""

    def test_get_task_detail(self, authenticated_client, create_meetup, create_task, create_registration):
        """Test getting task detail."""
        client, user, meetup_user = authenticated_client()
        meetup = create_meetup()
        create_registration(meetup_user, meetup)  # 참가자여야 조회 가능
        task = create_task(meetup, title='Detail Task', description='Task Description')

        url = reverse('task-detail', kwargs={'task_id': task.id})
        response = client.get(url)

        assert response.status_code == 200
        assert response.data['title'] == 'Detail Task'

    def test_update_task(self, authenticated_client, create_meetup, create_task):
        """Test updating a task."""
        client, user, meetup_user = authenticated_client(is_admin=True)
        meetup = create_meetup(creator=meetup_user)
        task = create_task(meetup, title='Original Title')

        url = reverse('task-detail', kwargs={'task_id': task.id})
        data = {'title': 'Updated Title'}

        response = client.put(url, data, format='json')
        assert response.status_code == 200

        task.refresh_from_db()
        assert task.title == 'Updated Title'

    def test_delete_task(self, authenticated_client, create_meetup, create_task):
        """Test deleting a task."""
        client, user, meetup_user = authenticated_client(is_admin=True)
        meetup = create_meetup(creator=meetup_user)
        task = create_task(meetup, title='To Delete')

        url = reverse('task-detail', kwargs={'task_id': task.id})
        response = client.delete(url)

        assert response.status_code in [200, 204]  # 200 OK or 204 No Content
        assert not Task.objects.filter(id=task.id).exists()


@pytest.mark.django_db
class TestTaskSubmissionAPI:
    """Tests for task submission endpoints."""

    def test_submit_task(self, authenticated_client, create_meetup, create_task, create_registration):
        """Test submitting a task."""
        client, user, meetup_user = authenticated_client()
        meetup = create_meetup()
        create_registration(meetup_user, meetup)  # 참가자여야 제출 가능
        task = create_task(meetup)

        url = reverse('submit-task', kwargs={'task_id': task.id})
        data = {
            'message': 'My submission',
            'link': 'https://github.com/example/repo'
        }

        response = client.post(url, data, format='json')
        assert response.status_code == 201
        assert TaskSubmission.objects.filter(task=task, user=meetup_user).exists()

    def test_submit_task_duplicate(self, authenticated_client, create_meetup, create_task, create_submission, create_registration):
        """Test submitting task twice fails."""
        client, user, meetup_user = authenticated_client()
        meetup = create_meetup()
        create_registration(meetup_user, meetup)  # 참가자여야 제출 가능
        task = create_task(meetup)
        create_submission(task, meetup_user)

        url = reverse('submit-task', kwargs={'task_id': task.id})
        data = {'message': 'Second submission'}

        response = client.post(url, data, format='json')
        assert response.status_code == 400

    def test_list_task_submissions(self, authenticated_client, create_meetup, create_task, create_meetup_user, create_submission):
        """Test listing task submissions."""
        client, user, meetup_user = authenticated_client(is_admin=True)
        meetup = create_meetup(creator=meetup_user)
        task = create_task(meetup)

        user1 = create_meetup_user(name='User1', email='user1@example.com')
        user2 = create_meetup_user(name='User2', email='user2@example.com')
        create_submission(task, user1)
        create_submission(task, user2)

        url = reverse('task-submissions', kwargs={'task_id': task.id})
        response = client.get(url)

        assert response.status_code == 200
        assert len(response.data['submissions']) == 2
        assert 'download_url' in response.data['submissions'][0]


@pytest.mark.django_db
class TestSubmissionReviewAPI:
    """Tests for submission review endpoint."""

    def test_review_submission_approve(self, authenticated_client, create_meetup, create_task, create_meetup_user, create_submission):
        """Test approving a submission."""
        client, user, meetup_user = authenticated_client(is_admin=True)
        meetup = create_meetup(creator=meetup_user)
        task = create_task(meetup)
        submitter = create_meetup_user(name='Submitter', email='submitter@example.com')
        submission = create_submission(task, submitter)

        url = reverse('review-submission', kwargs={'submission_id': submission.id})
        data = {'status': 'approved'}

        response = client.put(url, data, format='json')
        assert response.status_code == 200

        submission.refresh_from_db()
        assert submission.status == 'approved'

    def test_review_submission_reject(self, authenticated_client, create_meetup, create_task, create_meetup_user, create_submission):
        """Test rejecting a submission."""
        client, user, meetup_user = authenticated_client(is_admin=True)
        meetup = create_meetup(creator=meetup_user)
        task = create_task(meetup)
        submitter = create_meetup_user(name='Submitter', email='submitter@example.com')
        submission = create_submission(task, submitter)

        url = reverse('review-submission', kwargs={'submission_id': submission.id})
        data = {'status': 'rejected'}

        response = client.put(url, data, format='json')
        assert response.status_code == 200

        submission.refresh_from_db()
        assert submission.status == 'rejected'


@pytest.mark.django_db
class TestSubmissionFileDownloadAPI:
    """Tests for submission file download endpoint."""

    def test_creator_can_open_submission_file(
        self, authenticated_client, create_meetup, create_task, create_meetup_user, settings, tmp_path
    ):
        settings.MEDIA_ROOT = str(tmp_path)
        client, user, meetup_user = authenticated_client(is_admin=True)
        meetup = create_meetup(creator=meetup_user)
        task = create_task(meetup)
        submitter = create_meetup_user(name='Submitter A', email='submitter-a@example.com')
        submission = TaskSubmission.objects.create(
            task=task,
            user=submitter,
            message='파일 제출',
            file=SimpleUploadedFile('report.pdf', b'%PDF-1.4 test', content_type='application/pdf'),
        )

        url = reverse('submission-file-download', kwargs={'submission_id': submission.id})
        response = client.get(url, {'disposition': 'inline'})

        assert response.status_code == 200
        assert 'inline' in response['Content-Disposition']
        assert b''.join(response.streaming_content).startswith(b'%PDF-1.4')

    def test_submitter_can_download_own_file(
        self, authenticated_client, create_meetup, create_task, create_meetup_user, settings, tmp_path
    ):
        settings.MEDIA_ROOT = str(tmp_path)
        client, user, meetup_user = authenticated_client()
        creator = create_meetup_user(name='Creator', email='creator-file@example.com')
        meetup = create_meetup(creator=creator)
        task = create_task(meetup)
        submission = TaskSubmission.objects.create(
            task=task,
            user=meetup_user,
            message='내 파일',
            file=SimpleUploadedFile('image.png', b'png-data', content_type='image/png'),
        )

        url = reverse('submission-file-download', kwargs={'submission_id': submission.id})
        response = client.get(url, {'disposition': 'attachment'})

        assert response.status_code == 200
        assert 'attachment' in response['Content-Disposition']
        assert b''.join(response.streaming_content) == b'png-data'

    def test_third_party_cannot_access_submission_file(
        self, authenticated_client, create_meetup, create_task, create_meetup_user, create_submission
    ):
        client, user, outsider = authenticated_client()
        creator = create_meetup_user(name='Creator B', email='creator-b@example.com')
        submitter = create_meetup_user(name='Submitter B', email='submitter-b@example.com')
        meetup = create_meetup(creator=creator)
        task = create_task(meetup)
        submission = create_submission(task, submitter)

        url = reverse('submission-file-download', kwargs={'submission_id': submission.id})
        response = client.get(url)

        assert response.status_code == 403
        assert '모임 생성자 또는 제출자 본인' in response.data['error']

    def test_missing_file_on_disk_returns_404(
        self, authenticated_client, create_meetup, create_task, create_meetup_user, create_submission, settings, tmp_path
    ):
        settings.MEDIA_ROOT = str(tmp_path)
        client, user, meetup_user = authenticated_client(is_admin=True)
        meetup = create_meetup(creator=meetup_user)
        task = create_task(meetup)
        submitter = create_meetup_user(name='Submitter C', email='submitter-c@example.com')
        submission = create_submission(task, submitter)
        submission.file.name = 'task_submissions/missing-file.pdf'
        submission.save(update_fields=['file'])

        url = reverse('submission-file-download', kwargs={'submission_id': submission.id})
        response = client.get(url)

        assert response.status_code == 404
        assert response.data['error'] == '파일을 찾을 수 없습니다'
