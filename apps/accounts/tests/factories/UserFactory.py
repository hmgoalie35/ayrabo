import factory
from django.contrib.auth import get_user_model
from factory import PostGenerationMethodCall, django, Faker

User = get_user_model()


class UserFactory(django.DjangoModelFactory):
    class Meta:
        model = User

    first_name = Faker('first_name_male')
    last_name = Faker('last_name_male')
    # username and email must be the same
    email = factory.sequence(lambda x: 'user{x}@example.com'.format(x=x))
    username = factory.LazyAttribute(lambda obj: obj.email)
    password = PostGenerationMethodCall('set_password', 'myweakpassword')
    userprofile = factory.RelatedFactory('userprofiles.tests.factories.UserProfileFactory.UserProfileFactory', 'user')
