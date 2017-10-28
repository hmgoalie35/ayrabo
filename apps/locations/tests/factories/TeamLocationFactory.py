import factory
from factory import django

from locations.models import TeamLocation
from locations.tests import LocationFactory
from teams.tests import TeamFactory


class TeamLocationFactory(django.DjangoModelFactory):
    class Meta:
        model = TeamLocation

    team = factory.SubFactory(TeamFactory)
    location = factory.SubFactory(LocationFactory)
