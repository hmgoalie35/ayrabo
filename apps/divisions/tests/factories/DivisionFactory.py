import factory
from factory import django, fuzzy

from divisions.models import Division
from leagues.tests.factories.LeagueFactory import LeagueFactory


class DivisionFactory(django.DjangoModelFactory):
    class Meta:
        model = Division

    name = fuzzy.FuzzyText(length=8, suffix=' Division')
    league = factory.SubFactory(LeagueFactory)
