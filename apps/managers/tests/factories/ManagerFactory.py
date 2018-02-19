import factory
from factory import django

from users.tests import UserFactory
from managers.models import Manager
from teams.tests import TeamFactory


class ManagerFactory(django.DjangoModelFactory):
    class Meta:
        model = Manager

    user = factory.SubFactory(UserFactory)
    team = factory.SubFactory(TeamFactory)
    is_active = True
