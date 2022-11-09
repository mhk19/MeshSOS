from rest_framework import serializers
from . models import request_logs, UserProfile

class rlogSerializer(serializers.ModelSerializer):
    class Meta:
        model = request_logs
        fields = '__all__'
        
class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ('name', 'id', 'email', 'phone', 'service', 'location')
