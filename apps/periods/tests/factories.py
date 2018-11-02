import datetime

from factory import SubFactory, django

from games.tests import HockeyGameFactory
from periods import models


class AbstractPlayingPeriodFactory(django.DjangoModelFactory):
    duration = datetime.timedelta(minutes=20)

    class Meta:
        model = models.AbstractPlayingPeriod
        abstract = True


class HockeyPeriodFactory(AbstractPlayingPeriodFactory):
    game = SubFactory(HockeyGameFactory)
    name = models.HockeyPeriod.PERIOD_CHOICES[0][0]

    class Meta:
        model = models.HockeyPeriod
