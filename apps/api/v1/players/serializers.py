from rest_framework import serializers

from api.v1.users.serializers import UserSerializer
from players.models import HockeyPlayer


class AbstractPlayerSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = None
        fields = ['id', 'user', 'sport', 'team', 'jersey_number', 'is_active']


class HockeyPlayerSerializer(AbstractPlayerSerializer):
    class Meta:
        model = HockeyPlayer
        fields = AbstractPlayerSerializer.Meta.fields + ['position', 'handedness']
