from behave import *
from django.db.models import Q

from ayrabo.utils.testing import comma_separated_string_to_list, handle_date
from leagues.models import League
from seasons.tests import SeasonFactory
from teams.models import Team


@step('The following season objects? exists?')
def step_impl(context):
    for row in context.table:
        data = row.as_dict()
        league_name = data.get('league')
        league = League.objects.get(Q(name=league_name) | Q(abbreviated_name=league_name))

        start_date = data.get('start_date')
        # If start_date or end_date aren't specified, default to today.
        if start_date is None:
            start_date = handle_date('today')
        else:
            start_date = handle_date(start_date)

        end_date = data.get('end_date')
        if end_date is None:
            end_date = handle_date('1y')
        else:
            end_date = handle_date(end_date)

        kwargs = {'league': league, 'start_date': start_date, 'end_date': end_date}
        obj_id = data.get('id', None)
        if obj_id:
            kwargs['id'] = obj_id

        season = SeasonFactory(**kwargs)

        teams = comma_separated_string_to_list(data.get('teams'))
        if all(teams):
            for team in teams:
                season.teams.add(Team.objects.get(name=team))
