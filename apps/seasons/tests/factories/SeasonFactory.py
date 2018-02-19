import datetime

import factory
from factory import django, post_generation

from leagues.tests import LeagueFactory
from seasons.models import Season


class SeasonFactory(django.DjangoModelFactory):
    start_date = factory.LazyFunction(datetime.date.today)
    end_date = factory.LazyAttribute(lambda obj: obj.start_date + datetime.timedelta(days=365))
    league = factory.SubFactory(LeagueFactory)

    class Meta:
        model = Season

    @post_generation
    def teams(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            for team in extracted:
                self.teams.add(team)
