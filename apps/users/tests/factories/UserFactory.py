import factory
from factory import PostGenerationMethodCall, django, Faker

from users.models import User


class UserFactory(django.DjangoModelFactory):
    first_name = Faker('first_name_male')
    last_name = Faker('last_name_male')
    # username and email must be the same
    email = factory.sequence(lambda x: 'user{x}@ayrabo.com'.format(x=x))
    username = factory.LazyAttribute(lambda obj: obj.email)
    password = PostGenerationMethodCall('set_password', 'myweakpassword')
    userprofile = factory.RelatedFactory('userprofiles.tests.UserProfileFactory', 'user')

    class Meta:
        model = User
