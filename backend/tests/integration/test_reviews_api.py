"""
Integration tests for reviews API endpoints.

Note: can_write_review requires meetup.end_time (or date_time) to be in the past.
Meetups are created with past end_time so reviews can be written.
"""
from datetime import timedelta

import pytest
from django.urls import reverse
from django.utils import timezone

from meetups.models import Review


def _past_meetup_kwargs():
    """Return kwargs for a meetup that has already ended."""
    past = timezone.now() - timedelta(hours=2)
    return {
        'date_time': past - timedelta(hours=2),
        'end_time': past,
    }


@pytest.mark.django_db
class TestMeetupReviewWriteAPI:

    def test_create_review_success(self, authenticated_client, create_meetup, create_registration):
        client, user, meetup_user = authenticated_client()
        meetup = create_meetup(**_past_meetup_kwargs())
        create_registration(meetup_user, meetup)

        url = reverse('meetup-review', kwargs={'meetup_id': meetup.id})
        response = client.post(url, {'rating': 5, 'content': '정말 좋은 모임이었습니다!'}, format='json')

        assert response.status_code == 201
        assert Review.objects.filter(meetup=meetup, user=meetup_user).exists()

    def test_create_review_min_rating_1_valid(self, authenticated_client, create_meetup, create_registration):
        client, user, meetup_user = authenticated_client()
        meetup = create_meetup(**_past_meetup_kwargs())
        create_registration(meetup_user, meetup)

        url = reverse('meetup-review', kwargs={'meetup_id': meetup.id})
        response = client.post(url, {'rating': 1, 'content': '아쉬웠어요'}, format='json')
        assert response.status_code == 201

    def test_create_review_rating_zero_invalid(self, authenticated_client, create_meetup, create_registration):
        client, user, meetup_user = authenticated_client()
        meetup = create_meetup(**_past_meetup_kwargs())
        create_registration(meetup_user, meetup)

        url = reverse('meetup-review', kwargs={'meetup_id': meetup.id})
        response = client.post(url, {'rating': 0, 'content': '별점 없음'}, format='json')
        assert response.status_code == 400

    def test_create_review_rating_six_invalid(self, authenticated_client, create_meetup, create_registration):
        client, user, meetup_user = authenticated_client()
        meetup = create_meetup(**_past_meetup_kwargs())
        create_registration(meetup_user, meetup)

        url = reverse('meetup-review', kwargs={'meetup_id': meetup.id})
        response = client.post(url, {'rating': 6, 'content': '6점'}, format='json')
        assert response.status_code == 400

    def test_create_review_content_500_chars_valid(self, authenticated_client, create_meetup, create_registration):
        client, user, meetup_user = authenticated_client()
        meetup = create_meetup(**_past_meetup_kwargs())
        create_registration(meetup_user, meetup)

        url = reverse('meetup-review', kwargs={'meetup_id': meetup.id})
        response = client.post(url, {'rating': 4, 'content': 'a' * 500}, format='json')
        assert response.status_code == 201

    def test_create_review_content_501_chars_invalid(self, authenticated_client, create_meetup, create_registration):
        client, user, meetup_user = authenticated_client()
        meetup = create_meetup(**_past_meetup_kwargs())
        create_registration(meetup_user, meetup)

        url = reverse('meetup-review', kwargs={'meetup_id': meetup.id})
        response = client.post(url, {'rating': 4, 'content': 'a' * 501}, format='json')
        assert response.status_code == 400

    def test_create_review_duplicate_fails(self, authenticated_client, create_meetup, create_registration):
        client, user, meetup_user = authenticated_client()
        meetup = create_meetup(**_past_meetup_kwargs())
        create_registration(meetup_user, meetup)

        url = reverse('meetup-review', kwargs={'meetup_id': meetup.id})
        client.post(url, {'rating': 4, 'content': '첫 번째'}, format='json')
        response = client.post(url, {'rating': 5, 'content': '두 번째'}, format='json')
        assert response.status_code == 400

    def test_create_review_for_future_meetup_fails(self, authenticated_client, create_meetup, create_registration):
        client, user, meetup_user = authenticated_client()
        meetup = create_meetup()  # future meetup (default fixture)
        create_registration(meetup_user, meetup)

        url = reverse('meetup-review', kwargs={'meetup_id': meetup.id})
        response = client.post(url, {'rating': 5, 'content': '아직 안 열렸어요'}, format='json')
        assert response.status_code == 400

    def test_non_participant_cannot_write_review(self, authenticated_client, create_meetup):
        client, user, meetup_user = authenticated_client()
        meetup = create_meetup(**_past_meetup_kwargs())

        url = reverse('meetup-review', kwargs={'meetup_id': meetup.id})
        response = client.post(url, {'rating': 3, 'content': '참가 안 했는데'}, format='json')
        assert response.status_code == 400

    def test_unauthenticated_cannot_write_review(self, api_client, create_meetup):
        meetup = create_meetup(**_past_meetup_kwargs())
        url = reverse('meetup-review', kwargs={'meetup_id': meetup.id})
        response = api_client.post(url, {'rating': 5, 'content': '미인증'}, format='json')
        assert response.status_code == 401


@pytest.mark.django_db
class TestMeetupReviewReadAPI:

    def test_get_own_review(self, authenticated_client, create_meetup, create_registration):
        client, user, meetup_user = authenticated_client()
        meetup = create_meetup(**_past_meetup_kwargs())
        create_registration(meetup_user, meetup)

        url = reverse('meetup-review', kwargs={'meetup_id': meetup.id})
        client.post(url, {'rating': 5, 'content': '최고!'}, format='json')
        response = client.get(url)

        assert response.status_code == 200
        assert response.data['rating'] == 5
        assert response.data['content'] == '최고!'

    def test_update_review(self, authenticated_client, create_meetup, create_registration):
        client, user, meetup_user = authenticated_client()
        meetup = create_meetup(**_past_meetup_kwargs())
        create_registration(meetup_user, meetup)

        url = reverse('meetup-review', kwargs={'meetup_id': meetup.id})
        client.post(url, {'rating': 3, 'content': '처음 후기'}, format='json')
        response = client.put(url, {'rating': 5, 'content': '수정된 후기'}, format='json')

        assert response.status_code == 200
        review = Review.objects.get(meetup=meetup, user=meetup_user)
        assert review.rating == 5
        assert review.content == '수정된 후기'

    def test_meetup_reviews_list_public(self, api_client, create_meetup, create_meetup_user, create_registration):
        meetup = create_meetup(**_past_meetup_kwargs())
        r1 = create_meetup_user(name='이영희', email='lee_rv@example.com')
        r2 = create_meetup_user(name='박지민', email='park_rv@example.com')
        create_registration(r1, meetup)
        create_registration(r2, meetup)
        Review.objects.create(meetup=meetup, user=r1, rating=5, content='훌륭해요')
        Review.objects.create(meetup=meetup, user=r2, rating=4, content='좋아요')

        url = reverse('meetup-reviews-list', kwargs={'meetup_id': meetup.id})
        response = api_client.get(url)
        assert response.status_code == 200
        assert len(response.data['reviews']) == 2
        assert 'average_rating' in response.data
        assert 'total' in response.data


@pytest.mark.django_db
class TestReviewFeedAPI:

    def test_review_feed_public_no_auth(self, api_client, create_meetup, create_meetup_user, create_registration):
        meetup = create_meetup(**_past_meetup_kwargs())
        reviewer = create_meetup_user(name='홍길동', email='hong_rv@example.com')
        create_registration(reviewer, meetup)
        Review.objects.create(meetup=meetup, user=reviewer, rating=4, content='좋았어요')

        url = reverse('review-feed')
        response = api_client.get(url)
        assert response.status_code == 200
        assert len(response.data['reviews']) >= 1

    def test_recent_reviews_public(self, api_client, create_meetup, create_meetup_user, create_registration):
        meetup = create_meetup(**_past_meetup_kwargs())
        reviewer = create_meetup_user(name='김민수', email='kim_rv@example.com')
        create_registration(reviewer, meetup)
        Review.objects.create(meetup=meetup, user=reviewer, rating=3, content='보통')

        url = reverse('recent-reviews')
        response = api_client.get(url)
        assert response.status_code == 200
        assert 'reviews' in response.data

    def test_review_feed_masks_middle_chars(self, api_client, create_meetup, create_meetup_user, create_registration):
        meetup = create_meetup(**_past_meetup_kwargs())
        reviewer = create_meetup_user(name='김철수', email='mask_rv@example.com')
        create_registration(reviewer, meetup)
        Review.objects.create(meetup=meetup, user=reviewer, rating=5, content='마스킹 테스트')

        url = reverse('review-feed')
        response = api_client.get(url)
        reviews = response.data['reviews']
        assert len(reviews) >= 1
        masked = reviews[0]['user_name_masked']
        assert masked == '김*수'
        assert '철' not in masked


@pytest.mark.django_db
class TestReviewNameMasking:
    """Name masking logic via ReviewSerializer directly."""

    def _make_review(self, create_meetup, create_meetup_user, create_registration, name, email):
        from datetime import timedelta
        from django.utils import timezone
        past = timezone.now() - timedelta(hours=2)
        meetup = create_meetup(
            date_time=past - timedelta(hours=2),
            end_time=past,
        )
        user = create_meetup_user(name=name, email=email)
        create_registration(user, meetup)
        return Review.objects.create(meetup=meetup, user=user, rating=5, content='테스트')

    def test_three_char_name(self, create_meetup, create_meetup_user, create_registration):
        from meetups.serializers import ReviewSerializer
        review = self._make_review(create_meetup, create_meetup_user, create_registration, '김철수', 'mask3@example.com')
        assert ReviewSerializer(review).data['user_name_masked'] == '김*수'

    def test_two_char_name(self, create_meetup, create_meetup_user, create_registration):
        from meetups.serializers import ReviewSerializer
        review = self._make_review(create_meetup, create_meetup_user, create_registration, '김철', 'mask2@example.com')
        assert ReviewSerializer(review).data['user_name_masked'] == '김*'

    def test_one_char_name_unchanged(self, create_meetup, create_meetup_user, create_registration):
        from meetups.serializers import ReviewSerializer
        review = self._make_review(create_meetup, create_meetup_user, create_registration, '김', 'mask1@example.com')
        assert ReviewSerializer(review).data['user_name_masked'] == '김'

    def test_four_char_name(self, create_meetup, create_meetup_user, create_registration):
        from meetups.serializers import ReviewSerializer
        review = self._make_review(create_meetup, create_meetup_user, create_registration, '홍길동이', 'mask4@example.com')
        assert ReviewSerializer(review).data['user_name_masked'] == '홍**이'
