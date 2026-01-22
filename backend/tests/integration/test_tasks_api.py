"""
Integration tests for tasks API endpoints.
"""
from datetime import timedelta

import pytest
from django.urls import reverse
from django.utils import timezone

from meetups.models import Task, TaskSubmission


@pytest.mark.django_db
class TestTaskListAPI:
    """Tests for task list endpoint."""

    def test_list_meetup_tasks(self, api_client, create_meetup, create_task):
        """Test listing tasks for a meetup."""
        meetup = create_meetup()
        create_task(meetup, title='Task 1')
        create_task(meetup, title='Task 2')

        url = reverse('meetup-tasks', kwargs={'meetup_id': meetup.id})
        response = api_client.get(url)

        assert response.status_code == 200
        assert len(response.data['tasks']) == 2

    def test_list_meetup_tasks_empty(self, api_client, create_meetup):
        """Test listing tasks when none exist."""
        meetup = create_meetup()

        url = reverse('meetup-tasks', kwargs={'meetup_id': meetup.id})
        response = api_client.get(url)

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

    def test_get_task_detail(self, api_client, create_meetup, create_task):
        """Test getting task detail."""
        meetup = create_meetup()
        task = create_task(meetup, title='Detail Task', description='Task Description')

        url = reverse('task-detail', kwargs={'task_id': task.id})
        response = api_client.get(url)

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

        assert response.status_code == 200
        assert not Task.objects.filter(id=task.id).exists()


@pytest.mark.django_db
class TestTaskSubmissionAPI:
    """Tests for task submission endpoints."""

    def test_submit_task(self, authenticated_client, create_meetup, create_task):
        """Test submitting a task."""
        client, user, meetup_user = authenticated_client()
        meetup = create_meetup()
        task = create_task(meetup)

        url = reverse('submit-task', kwargs={'task_id': task.id})
        data = {
            'message': 'My submission',
            'link': 'https://github.com/example/repo'
        }

        response = client.post(url, data, format='json')
        assert response.status_code == 201
        assert TaskSubmission.objects.filter(task=task, user=meetup_user).exists()

    def test_submit_task_duplicate(self, authenticated_client, create_meetup, create_task, create_submission):
        """Test submitting task twice fails."""
        client, user, meetup_user = authenticated_client()
        meetup = create_meetup()
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
