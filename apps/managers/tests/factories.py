from factory import SubFactory, django

from managers.models import Manager
from teams.tests import TeamFactory
from users.tests import UserFactory


class ManagerFactory(django.DjangoModelFactory):
    user = SubFactory(UserFactory)
    team = SubFactory(TeamFactory)
    is_active = True

    class Meta:
        model = Manager
