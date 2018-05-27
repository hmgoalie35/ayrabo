from factory import SubFactory, django

from users.models import Permission


class PermissionFactory(django.DjangoModelFactory):
    user = SubFactory('users.UserFactory')

    class Meta:
        model = Permission
