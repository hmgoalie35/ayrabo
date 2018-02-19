from rest_framework import serializers

from users.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        # I'm excluding email so players, coaches, etc. don't have their email leaked.
        fields = ['id', 'first_name', 'last_name']
