from factory import Sequence, SubFactory, django, post_generation

from organizations.models import Organization
from sports.tests import SportFactory


class OrganizationFactory(django.DjangoModelFactory):
    name = Sequence(lambda x: 'Organization {}'.format(x))
    sport = SubFactory(SportFactory)

    class Meta:
        model = Organization

    @post_generation
    def full_clean(self, obj, extracted, **kwargs):
        self.full_clean(exclude=['slug'])
