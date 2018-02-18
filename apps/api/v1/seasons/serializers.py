from rest_framework import serializers

from api.v1.players.serializers import HockeyPlayerSerializer
from seasons.models import HockeySeasonRoster


class AbstractSeasonRosterSerializer(serializers.ModelSerializer):
    class Meta:
        model = None
        fields = ['id', 'name', 'default', 'season', 'players']


class HockeySeasonRosterSerializer(AbstractSeasonRosterSerializer):
    players = HockeyPlayerSerializer(many=True, read_only=True)

    class Meta(AbstractSeasonRosterSerializer.Meta):
        model = HockeySeasonRoster
