"""후기 API 뷰"""
import logging

from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from ..models import Meetup, MeetupUser, Registration, Review
from ..serializers import ReviewSerializer

logger = logging.getLogger(__name__)


def is_meetup_ended(meetup):
    """밋업이 종료되었는지 확인"""
    now = timezone.now()
    if meetup.end_time:
        return meetup.end_time < now
    return meetup.date_time < now


def can_write_review(user, meetup):
    """
    사용자가 후기를 작성할 수 있는지 확인
    - 밋업이 종료됨
    - 밋업 생성자이거나 참가자
    """
    if not is_meetup_ended(meetup):
        return False, "모임이 아직 종료되지 않았습니다."

    try:
        meetup_user = user.meetup_profile
    except MeetupUser.DoesNotExist:
        return False, "사용자 프로필을 찾을 수 없습니다."

    # 밋업 생성자인지 확인
    if meetup.creator == meetup_user:
        return True, None

    # 참가자인지 확인
    if Registration.objects.filter(meetup=meetup, user=meetup_user).exists():
        return True, None

    return False, "해당 모임의 참가자만 후기를 작성할 수 있습니다."


@api_view(['GET'])
@permission_classes([AllowAny])
def review_feed(request):
    """
    후기 피드 (모든 사용자 조회 가능)
    페이지네이션 지원
    """
    page = int(request.query_params.get('page', 1))
    page_size = int(request.query_params.get('page_size', 10))

    reviews = Review.objects.select_related('user', 'meetup').all()
    total = reviews.count()

    start = (page - 1) * page_size
    end = start + page_size
    reviews = reviews[start:end]

    serializer = ReviewSerializer(reviews, many=True, context={'request': request})

    return Response({
        'reviews': serializer.data,
        'total': total,
        'page': page,
        'page_size': page_size,
        'has_more': end < total
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def recent_reviews(request):
    """최근 후기 5개 조회 (대시보드용)"""
    reviews = Review.objects.select_related('user', 'meetup').all()[:5]
    serializer = ReviewSerializer(reviews, many=True, context={'request': request})
    return Response({'reviews': serializer.data})


@api_view(['GET', 'POST', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def meetup_review(request, meetup_id):
    """
    밋업별 후기 CRUD
    GET: 내 후기 조회
    POST: 후기 작성
    PUT: 후기 수정
    DELETE: 후기 삭제
    """
    try:
        meetup = Meetup.objects.get(id=meetup_id)
    except Meetup.DoesNotExist:
        return Response({'error': '모임을 찾을 수 없습니다.'}, status=status.HTTP_404_NOT_FOUND)

    try:
        meetup_user = request.user.meetup_profile
    except MeetupUser.DoesNotExist:
        return Response({'error': '사용자 프로필을 찾을 수 없습니다.'}, status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'GET':
        # 내 후기 조회
        try:
            review = Review.objects.get(meetup=meetup, user=meetup_user)
            serializer = ReviewSerializer(review, context={'request': request})
            return Response(serializer.data)
        except Review.DoesNotExist:
            # 후기가 없는 경우, 작성 가능 여부 확인
            can_write, error_msg = can_write_review(request.user, meetup)
            return Response({
                'review': None,
                'can_write': can_write,
                'error': error_msg
            })

    elif request.method == 'POST':
        # 후기 작성
        can_write, error_msg = can_write_review(request.user, meetup)
        if not can_write:
            return Response({'error': error_msg}, status=status.HTTP_400_BAD_REQUEST)

        # 이미 후기가 있는지 확인
        if Review.objects.filter(meetup=meetup, user=meetup_user).exists():
            return Response({'error': '이미 후기를 작성하셨습니다.'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = ReviewSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save(meetup=meetup, user=meetup_user)
            logger.info(f"Review created: user={meetup_user.id}, meetup={meetup_id}")
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'PUT':
        # 후기 수정
        try:
            review = Review.objects.get(meetup=meetup, user=meetup_user)
        except Review.DoesNotExist:
            return Response({'error': '수정할 후기가 없습니다.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = ReviewSerializer(review, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            logger.info(f"Review updated: user={meetup_user.id}, meetup={meetup_id}")
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        # 후기 삭제
        try:
            review = Review.objects.get(meetup=meetup, user=meetup_user)
        except Review.DoesNotExist:
            return Response({'error': '삭제할 후기가 없습니다.'}, status=status.HTTP_404_NOT_FOUND)

        review.delete()
        logger.info(f"Review deleted: user={meetup_user.id}, meetup={meetup_id}")
        return Response({'message': '후기가 삭제되었습니다.'}, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def meetup_reviews_list(request, meetup_id):
    """특정 밋업의 모든 후기 조회"""
    try:
        meetup = Meetup.objects.get(id=meetup_id)
    except Meetup.DoesNotExist:
        return Response({'error': '모임을 찾을 수 없습니다.'}, status=status.HTTP_404_NOT_FOUND)

    reviews = Review.objects.filter(meetup=meetup).select_related('user')
    serializer = ReviewSerializer(reviews, many=True, context={'request': request})

    # 평균 별점 계산
    if reviews.exists():
        avg_rating = sum(r.rating for r in reviews) / reviews.count()
    else:
        avg_rating = 0

    return Response({
        'reviews': serializer.data,
        'total': reviews.count(),
        'average_rating': round(avg_rating, 1)
    })
