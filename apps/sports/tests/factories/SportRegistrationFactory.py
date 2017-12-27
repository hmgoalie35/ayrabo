from factory import django, SubFactory

from accounts.tests import UserFactory
from sports.models import SportRegistration
from sports.tests import SportFactory


class SportRegistrationFactory(django.DjangoModelFactory):
    user = SubFactory(UserFactory)
    sport = SubFactory(SportFactory)
    # 1 signifies only the player role
    roles_mask = 1
    is_complete = True

    class Meta:
        model = SportRegistration
