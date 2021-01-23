from factory import SubFactory, django

from games.tests import HockeyGameFactory
from periods import models


class AbstractPlayingPeriodFactory(django.DjangoModelFactory):
    duration = 15

    class Meta:
        model = models.AbstractPlayingPeriod
        abstract = True


class HockeyPeriodFactory(AbstractPlayingPeriodFactory):
    game = SubFactory(HockeyGameFactory)
    name = models.HockeyPeriod.ONE

    class Meta:
        model = models.HockeyPeriod
