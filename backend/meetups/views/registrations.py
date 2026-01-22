from rest_framework import generics, status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from ..models import Registration
from ..serializers import RegisterUserSerializer, RegistrationSerializer


class RegistrationListView(generics.ListAPIView):
    queryset = Registration.objects.all().order_by('-registered_at')
    serializer_class = RegistrationSerializer


@api_view(['POST'])
def register_user(request):
    serializer = RegisterUserSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    user = serializer.validated_data['user']
    meetup = serializer.validated_data['meetup']
    registration = Registration.objects.create(user=user, meetup=meetup)
    response_serializer = RegistrationSerializer(registration)

    return Response({
        'message': '신청이 완료되었습니다',
        'registration': response_serializer.data
    }, status=status.HTTP_201_CREATED)
