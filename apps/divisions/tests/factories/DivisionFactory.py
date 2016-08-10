import factory
from factory import django, fuzzy, post_generation

from divisions.models import Division
from leagues.tests import LeagueFactory


class DivisionFactory(django.DjangoModelFactory):
    class Meta:
        model = Division

    name = fuzzy.FuzzyText(length=8, suffix=' Division')
    league = factory.SubFactory(LeagueFactory)

    @post_generation
    def full_clean(self, obj, extracted, **kwargs):
        # league is omitted here because it seems like factory boy sets league_id after this post generation method is
        # called
        self.full_clean(exclude=['slug', 'league'])
