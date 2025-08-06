from rest_framework import serializers
from django.contrib.auth.models import User
from .models import MeetupUser, Meetup, Registration

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password']
    
    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        
        meetup_user = MeetupUser.objects.create(
            user=user,
            name=validated_data['username'],  # Use username as name
            email=validated_data['email'],
            phone=''
        )
        
        return user

class MeetupUserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    total_meetups_created = serializers.SerializerMethodField()
    
    class Meta:
        model = MeetupUser
        fields = ['id', 'name', 'email', 'phone', 'is_admin', 'created_at', 'username', 'total_meetups_created']
    
    def get_total_meetups_created(self, obj):
        return obj.created_meetups.count()

class MeetupSerializer(serializers.ModelSerializer):
    is_full = serializers.ReadOnlyField()
    available_spots = serializers.ReadOnlyField()
    creator_name = serializers.CharField(source='creator.name', read_only=True)
    
    class Meta:
        model = Meetup
        fields = ['id', 'name', 'description', 'date_time', 'end_time', 'location', 
                 'max_participants', 'current_participants', 'created_at',
                 'is_full', 'available_spots', 'creator', 'creator_name']

class RegistrationSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.name', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    meetup_name = serializers.CharField(source='meetup.name', read_only=True)
    meetup_date_time = serializers.DateTimeField(source='meetup.date_time', read_only=True)
    
    class Meta:
        model = Registration
        fields = ['id', 'user', 'meetup', 'registered_at', 
                 'user_name', 'user_email', 'meetup_name', 'meetup_date_time']

class RegisterUserSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    meetup_id = serializers.IntegerField()
    
    def validate(self, data):
        try:
            user = MeetupUser.objects.get(id=data['user_id'])
            meetup = Meetup.objects.get(id=data['meetup_id'])
        except MeetupUser.DoesNotExist:
            raise serializers.ValidationError("User not found")
        except Meetup.DoesNotExist:
            raise serializers.ValidationError("Meetup not found")
        
        if Registration.objects.filter(user=user, meetup=meetup).exists():
            raise serializers.ValidationError("User already registered for this meetup")
        
        if meetup.is_full:
            raise serializers.ValidationError("Meetup is full")
        
        data['user'] = user
        data['meetup'] = meetup
        return data