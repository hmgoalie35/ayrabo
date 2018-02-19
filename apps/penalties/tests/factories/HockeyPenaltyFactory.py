import datetime

from factory import django, SubFactory, LazyAttribute

from games.tests import HockeyGameFactory
from penalties import models
from periods.tests import HockeyPeriodFactory
from players.tests import HockeyPlayerFactory


class HockeyPenaltyFactory(django.DjangoModelFactory):
    game = SubFactory(HockeyGameFactory)
    period = SubFactory(HockeyPeriodFactory)
    duration = datetime.timedelta(minutes=2)
    player = SubFactory(HockeyPlayerFactory)
    time_in = datetime.timedelta(minutes=3, seconds=23)
    time_out = LazyAttribute(lambda obj: obj.time_in + obj.duration)

    class Meta:
        model = models.HockeyPenalty
