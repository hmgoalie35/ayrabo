from django.contrib.auth import get_user_model
from factory import PostGenerationMethodCall
from factory.django import DjangoModelFactory

User = get_user_model()


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User

    first_name = 'John'
    last_name = 'Doe'
    # username and email must be the same
    email = 'user@example.com'
    username = email
    password = PostGenerationMethodCall('set_password', 'myweakpassword')
