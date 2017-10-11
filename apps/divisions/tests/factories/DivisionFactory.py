import factory
from factory import django, Faker, post_generation

from divisions.models import Division
from leagues.tests import LeagueFactory


class DivisionFactory(django.DjangoModelFactory):
    class Meta:
        model = Division
        django_get_or_create = ('name',)

    name = Faker('text', max_nb_chars=8)
    league = factory.SubFactory(LeagueFactory)

    @post_generation
    def full_clean(self, obj, extracted, **kwargs):
        # league is omitted here because it seems like factory boy sets league_id after this post generation method is
        # called
        self.full_clean(exclude=['slug', 'league'])
