from factory import django, Sequence

from common.models import GenericChoice


class GenericChoiceFactory(django.DjangoModelFactory):
    class Meta:
        model = GenericChoice

    short_value = Sequence(lambda x: 'model_choice_{}'.format(x))
    long_value = Sequence(lambda x: 'Model Choice {}'.format(x))
