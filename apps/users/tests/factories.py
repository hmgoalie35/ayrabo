from factory import Faker, LazyAttribute, PostGenerationMethodCall, RelatedFactory, SubFactory, django, sequence

from users.models import Permission
from users.models import User


class UserFactory(django.DjangoModelFactory):
    first_name = Faker('first_name_male')
    last_name = Faker('last_name_male')
    # username and email must be the same
    email = sequence(lambda x: 'user{x}@ayrabo.com'.format(x=x))
    username = LazyAttribute(lambda obj: obj.email)
    password = PostGenerationMethodCall('set_password', 'myweakpassword')
    userprofile = RelatedFactory('userprofiles.tests.UserProfileFactory', 'user')

    class Meta:
        model = User


class PermissionFactory(django.DjangoModelFactory):
    user = SubFactory('users.tests.UserFactory')

    class Meta:
        model = Permission
