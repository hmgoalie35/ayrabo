import factory
from factory import django, post_generation, Faker, Sequence

from divisions.tests import DivisionFactory
from teams.models import Team


class TeamFactory(django.DjangoModelFactory):
    name = Sequence(lambda x: 'Team {}'.format(x))
    website = Faker('url')
    division = factory.SubFactory(DivisionFactory)

    class Meta:
        model = Team

    @post_generation
    def full_clean(self, obj, extracted, **kwargs):
        # division is omitted here because it seems like factory boy sets division_id after this post generation
        # method is called
        self.full_clean(exclude=['slug', 'division'])
