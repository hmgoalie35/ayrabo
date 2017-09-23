import datetime

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

        today = datetime.date.today()
        start_date = data.get('start_date', today)
        end_date = data.get('end_date', today + datetime.timedelta(days=365))
        kwargs = {'league': league, 'start_date': start_date, 'end_date': end_date}
        obj_id = data.get('id', None)
        if obj_id:
            kwargs['id'] = obj_id

        season = SeasonFactory(**kwargs)

        teams = data.get('teams').split(',')
        for team in teams:
            season.teams.add(Team.objects.get(name=team))
