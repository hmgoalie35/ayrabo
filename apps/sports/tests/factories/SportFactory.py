import factory
import factory.fuzzy
from factory.django import DjangoModelFactory
from sports.models import Sport


class SportFactory(DjangoModelFactory):
    class Meta:
        model = Sport

    name = factory.sequence(lambda x: 'sport_{x}'.format(x=x))
    # slug =
    description = factory.fuzzy.FuzzyText(length=32)
