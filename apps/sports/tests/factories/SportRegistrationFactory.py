import factory
from factory import django

from accounts.tests import UserFactory
from sports.models import SportRegistration
from sports.tests.factories.SportFactory import SportFactory


class SportRegistrationFactory(django.DjangoModelFactory):
    class Meta:
        model = SportRegistration

    user = factory.SubFactory(UserFactory)
    sport = factory.SubFactory(SportFactory)
    # 1 signifies only the player role
    roles_mask = 1
    is_complete = True
