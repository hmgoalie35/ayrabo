import factory
from django.contrib.auth import get_user_model
from factory import PostGenerationMethodCall, django
from faker import Faker

fake = Faker()
User = get_user_model()


class UserFactory(django.DjangoModelFactory):
    class Meta:
        model = User

    first_name = factory.LazyFunction(fake.first_name_male)
    last_name = factory.LazyFunction(fake.last_name_male)
    # username and email must be the same
    email = factory.sequence(lambda x: 'user{x}@example.com'.format(x=x))
    username = factory.LazyAttribute(lambda obj: obj.email)
    password = PostGenerationMethodCall('set_password', 'myweakpassword')
    userprofile = factory.RelatedFactory('userprofiles.tests.factories.UserProfileFactory.UserProfileFactory', 'user')
