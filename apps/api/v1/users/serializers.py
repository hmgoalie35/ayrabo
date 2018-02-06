from django.contrib.auth.models import User
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        # I'm excluding email so players, coaches, etc. don't have their email leaked.
        fields = ['id', 'first_name', 'last_name']
