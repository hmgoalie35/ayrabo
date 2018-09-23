from factory import Faker, Sequence
from factory.django import DjangoModelFactory
from waffle.models import Switch

from common.models import GenericChoice


class GenericChoiceFactory(DjangoModelFactory):
    short_value = Sequence(lambda x: 'model_choice_{}'.format(x))
    long_value = Sequence(lambda x: 'Model Choice {}'.format(x))

    class Meta:
        model = GenericChoice


class WaffleSwitchFactory(DjangoModelFactory):
    name = Faker('text', max_nb_chars=32)
    active = False
    note = Faker('text', max_nb_chars=32)

    class Meta:
        model = Switch
