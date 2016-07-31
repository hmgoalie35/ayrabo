import factory
from factory import django

from accounts.tests.factories.UserFactory import UserFactory
from sports.tests.factories.SportFactory import SportFactory
from userprofiles.models import RolesMask


class RolesMaskFactory(django.DjangoModelFactory):
    class Meta:
        model = RolesMask

    user = factory.SubFactory(UserFactory)
    sport = factory.SubFactory(SportFactory)
    # 1 signifies only the player role
    roles_mask = 1
    are_role_objects_created = True
    are_roles_set = True
