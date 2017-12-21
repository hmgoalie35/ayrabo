from factory import django, Faker

from penalties.models import GenericPenaltyChoice


class GenericPenaltyChoiceFactory(django.DjangoModelFactory):
    name = 'Interference'
    description = Faker('sentences', nb=5)

    class Meta:
        model = GenericPenaltyChoice
