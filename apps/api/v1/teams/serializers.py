from rest_framework import serializers

from api.utils.serializer_fields import EasyThumbnailField
from api.v1.divisions.serializers import DivisionSerializer
from teams.models import Team


class TeamSerializer(serializers.ModelSerializer):
    logo = EasyThumbnailField(alias='sm')
    division = DivisionSerializer()

    # logo = serializers.SerializerMethodField()
    #
    # def get_logo(self, obj):
    #     # XSS?
    #     return '<img src="{}" />'.format(obj.logo.url)

    class Meta:
        model = Team
        fields = ('id', 'name', 'logo', 'division')
