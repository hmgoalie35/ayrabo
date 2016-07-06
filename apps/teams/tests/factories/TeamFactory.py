import factory
from factory import django, fuzzy, post_generation

from divisions.tests.factories.DivisionFactory import DivisionFactory
from teams.models import Team


class TeamFactory(django.DjangoModelFactory):
    class Meta:
        model = Team

    name = fuzzy.FuzzyText(length=32)
    website = 'https://www.google.com'
    division = factory.SubFactory(DivisionFactory)

    @post_generation
    def full_clean(self, obj, extracted, **kwargs):
        self.full_clean(exclude=['slug'])

