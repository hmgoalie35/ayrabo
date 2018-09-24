from factory import Faker, SubFactory, django

from sports.models import SportRegistration
from sports.tests import SportFactory
from users.tests import UserFactory


class SportRegistrationFactory(django.DjangoModelFactory):
    user = SubFactory(UserFactory)
    sport = SubFactory(SportFactory)
    role = Faker('random_element', elements=[role[0] for role in SportRegistration.ROLE_CHOICES])
    is_complete = True

    class Meta:
        model = SportRegistration
