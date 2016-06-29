import factory
from factory import django, fuzzy

from divisions.tests.factories.DivisionFactory import DivisionFactory
from teams.models import Team


class TeamFactory(django.DjangoModelFactory):
    class Meta:
        model = Team

    name = fuzzy.FuzzyText(length=32)
    website = 'https://www.google.com'
    division = factory.SubFactory(DivisionFactory)
