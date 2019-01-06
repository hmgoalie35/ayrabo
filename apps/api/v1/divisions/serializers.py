from rest_framework import serializers

from divisions.models import Division


class DivisionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Division
        fields = ('id', 'name')
