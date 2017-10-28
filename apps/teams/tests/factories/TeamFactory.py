import factory
from factory import django, post_generation, Faker

from divisions.tests import DivisionFactory
from teams.models import Team


class TeamFactory(django.DjangoModelFactory):
    class Meta:
        model = Team

    name = Faker('text', max_nb_chars=32)
    website = Faker('url')
    division = factory.SubFactory(DivisionFactory)

    @post_generation
    def full_clean(self, obj, extracted, **kwargs):
        # division is omitted here because it seems like factory boy sets division_id after this post generation
        # method is called
        self.full_clean(exclude=['slug', 'division'])
