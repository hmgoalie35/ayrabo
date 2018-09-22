from factory import Faker, LazyAttribute, Sequence, SubFactory, django, post_generation

from divisions.tests import DivisionFactory
from organizations.tests import OrganizationFactory
from teams.models import Team


class TeamFactory(django.DjangoModelFactory):
    name = Sequence(lambda x: 'Team {}'.format(x))
    logo = django.ImageField(filename='logo.jpeg', format='JPEG')
    website = Faker('url')
    division = SubFactory(DivisionFactory)
    organization = LazyAttribute(lambda obj: OrganizationFactory(name=obj.name, sport=obj.division.league.sport))

    class Meta:
        model = Team

    @post_generation
    def full_clean(self, obj, extracted, **kwargs):
        # division is omitted here because it seems like factory boy sets division_id after this post generation
        # method is called
        self.full_clean(exclude=['slug', 'division'])
