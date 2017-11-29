from factory import django, Sequence

from common.models import GenericModelChoice


class GenericModelChoiceFactory(django.DjangoModelFactory):
    class Meta:
        model = GenericModelChoice

    short_name = Sequence(lambda x: 'model_choice_{}'.format(x))
    long_name = Sequence(lambda x: 'Model Choice {}'.format(x))
