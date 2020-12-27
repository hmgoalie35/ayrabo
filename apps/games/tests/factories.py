import datetime

from django.utils import timezone
from factory import LazyAttribute, LazyFunction, SubFactory, django, post_generation

from games import models
from locations.tests import LocationFactory
from players.tests import HockeyPlayerFactory
from seasons.tests import SeasonFactory
from teams.tests import TeamFactory
from users.tests import UserFactory


# NOTE: fields such as type, point_value, etc. should be explicitly set in tests so bad data isn't used.
class AbstractGameFactory(django.DjangoModelFactory):
    home_team = SubFactory(TeamFactory)
    away_team = LazyAttribute(lambda obj: TeamFactory(division=obj.home_team.division))
    status = models.AbstractGame.SCHEDULED
    location = SubFactory(LocationFactory)
    # `timezone.now` is defaulting to UTC because the user/userprofile factories default the timzone to UTC
    start = LazyFunction(timezone.now)
    end = LazyAttribute(lambda obj: obj.start + datetime.timedelta(hours=2))
    # This should match the timezone of `start`.
    timezone = 'UTC'
    season = SubFactory(SeasonFactory)
    team = LazyAttribute(lambda obj: obj.home_team)
    created_by = SubFactory(UserFactory)
    period_duration = 15

    class Meta:
        model = models.AbstractGame
        abstract = True


class HockeyGameFactory(AbstractGameFactory):
    class Meta:
        model = models.HockeyGame


class AbstractGamePlayerFactory(django.DjangoModelFactory):
    team = SubFactory(TeamFactory)

    class Meta:
        abstract = True


class HockeyGamePlayerFactory(AbstractGamePlayerFactory):
    game = SubFactory(HockeyGameFactory)
    player = SubFactory(HockeyPlayerFactory)

    class Meta:
        model = models.HockeyGamePlayer


class HockeyGoalFactory(django.DjangoModelFactory):
    game = SubFactory(HockeyGameFactory)
    period = SubFactory('periods.tests.HockeyPeriodFactory')
    time = datetime.timedelta(minutes=5, seconds=23)
    player = SubFactory(HockeyPlayerFactory)
    type = models.HockeyGoal.EVEN_STRENGTH

    class Meta:
        model = models.HockeyGoal

    @post_generation
    def full_clean(self, *args, **kwargs):
        self.full_clean()


class HockeyAssistFactory(django.DjangoModelFactory):
    player = SubFactory(HockeyPlayerFactory)
    goal = SubFactory(HockeyGoalFactory)

    class Meta:
        model = models.HockeyAssist
