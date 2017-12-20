from django.contrib.auth.models import User, Group
from .models import Submission
from rest_framework import serializers
from django.contrib.auth import get_user_model # If used custom user model

UserModel = get_user_model()

class UserSerializer(serializers.HyperlinkedModelSerializer):
    password = serializers.CharField(write_only=True)

    def create(self, validated_data):

        user = UserModel.objects.create(
            username=validated_data['email']
        )
        user.set_password(validated_data['password'])
        user.save()

        return user

    class Meta:
        model = UserModel
        fields = ('email','password',)


class SubmissionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Submission
        read_only_fields = ('create_date', 'processed_date','user')
        # read_only_fields = ('created', 'datafile', 'owner')
        fields = ('id', 'video','processed_video', 'status', 'analysis') 
