from behave import *
from django.db.models import Q

from leagues.models import League
from seasons.tests import SeasonFactory
from teams.models import Team


@step('The following season objects? exists?')
def step_impl(context):
    for row in context.table:
        data = row.as_dict()
        league_name = data.get('league')
        league = League.objects.get(Q(full_name=league_name) | Q(abbreviated_name=league_name))

        kwargs = {'league': league}
        start_date = data.get('start_date')
        end_date = data.get('end_date')

        if start_date:
            kwargs['start_date'] = start_date
        if end_date:
            kwargs['end_date'] = end_date

        season = SeasonFactory(**kwargs)

        teams = data.get('teams').split(',')
        for team in teams:
            season.teams.add(Team.objects.get(name=team))
