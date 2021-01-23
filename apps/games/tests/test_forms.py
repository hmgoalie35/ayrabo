import datetime

import pytz
from django.utils import timezone

from ayrabo.utils.testing import BaseTestCase
from common.models import GenericChoice
from common.tests import GenericChoiceFactory
from divisions.tests import DivisionFactory
from games.forms import HockeyGameCreateForm, HockeyGameScoresheetForm, HockeyGameUpdateForm
from games.models import AbstractGame
from games.tests import HockeyGameFactory, HockeyGamePlayerFactory
from leagues.tests import LeagueFactory
from players.tests import HockeyPlayerFactory
from seasons.tests import SeasonFactory
from sports.tests import SportFactory
from teams.tests import TeamFactory


# Tests for the .clean method can be found in test_views
class AbstractGameCreateUpdateFormTests(BaseTestCase):
    """
    Testing the abstract class via `HockeyGameCreateForm`.
    """

    def setUp(self):
        self.form_cls = HockeyGameCreateForm

        self.ice_hockey = SportFactory(name='Ice Hockey')
        self.liahl = LeagueFactory(name='Long Island Amateur Hockey League', sport=self.ice_hockey)
        self.mm_aa = DivisionFactory(name='Midget Minor AA', league=self.liahl)
        self.t1 = TeamFactory(division=self.mm_aa)
        self.t2 = TeamFactory(division=self.mm_aa)
        self.t3 = TeamFactory(division=self.mm_aa)
        self.t4 = TeamFactory(name='Green Machine IceCats', division=self.mm_aa)

        self.squirt = DivisionFactory(name='Squirt', league=self.liahl)
        self.squirt_teams = TeamFactory.create_batch(3, division=self.squirt)

        self.game_type = GenericChoiceFactory(
            id=1,
            short_value='exhibition',
            long_value='Exhibition',
            type=GenericChoice.GAME_TYPE,
            content_object=self.ice_hockey
        )
        self.point_value = GenericChoiceFactory(
            id=2,
            short_value='2',
            long_value='2',
            type=GenericChoice.GAME_POINT_VALUE,
            content_object=self.ice_hockey
        )

    def test_teams_filtered_by_division(self):
        form = self.form_cls(team=self.t4)
        home_team_qs = form.fields['home_team'].queryset
        away_team_qs = form.fields['away_team'].queryset
        expected = [self.t1.id, self.t2.id, self.t3.id, self.t4.id]
        self.assertListEqual(sorted(list(home_team_qs.values_list('id', flat=True))), expected)
        self.assertListEqual(sorted(list(away_team_qs.values_list('id', flat=True))), expected)

    def test_generic_choice_filtered_by_game_type(self):
        form = self.form_cls(team=self.t4)
        game_type_qs = form.fields['type'].queryset
        self.assertListEqual(list(game_type_qs.values_list('id', flat=True)), [1])

    def test_generic_choice_filtered_by_game_point_value(self):
        form = self.form_cls(team=self.t4)
        point_value_qs = form.fields['point_value'].queryset
        self.assertListEqual(list(point_value_qs.values_list('id', flat=True)), [2])

    def test_season_filtered_by_league(self):
        SeasonFactory(id=1, league=self.liahl)
        SeasonFactory(id=2, league=self.liahl, start_date=datetime.date(month=12, day=26, year=2000))
        SeasonFactory(id=3)
        form = self.form_cls(team=self.t4)
        season_qs = form.fields['season'].queryset
        self.assertListEqual(list(season_qs.values_list('id', flat=True)), [1, 2])

    def test_initial_timezone(self):
        timezone.activate(pytz.timezone('US/Eastern'))
        form = self.form_cls(team=self.t4)
        self.assertEqual(form.fields['timezone'].initial, 'US/Eastern')

    def test_save_update_case(self):
        season = SeasonFactory(league=self.liahl)
        instance = HockeyGameFactory(
            home_team=self.t1,
            team=self.t1,
            away_team=self.t2,
            type=self.game_type,
            point_value=self.point_value,
            season=season,
        )
        HockeyGamePlayerFactory(
            game=instance,
            player=HockeyPlayerFactory(sport=self.ice_hockey, team=self.t2),
            team=self.t2
        )
        # We're changing the away team
        form = HockeyGameUpdateForm(
            instance=instance,
            team=self.t1,
            data={
                'home_team': self.t1.id,
                'away_team': self.t3.id,
                'type': self.game_type.pk,
                'point_value': self.point_value.pk,
                'location': instance.location.pk,
                'start': instance.start,
                'end': instance.end,
                'timezone': instance.timezone,
                'season': instance.season.pk,
                'status': instance.status,
            }
        )
        form.is_valid()
        form.save()
        self.assertEqual(instance._get_game_players(self.t2).count(), 0)


class AbstractGameScoresheetFormTests(BaseTestCase):
    """Testing this abstract class via `HockeyGameScoresheetForm`"""

    def setUp(self):
        self.sport = SportFactory()
        self.point_value = GenericChoiceFactory(
            content_object=self.sport,
            short_value='1',
            long_value='1',
            type=GenericChoice.GAME_POINT_VALUE
        )
        self.game_type = GenericChoiceFactory(
            content_object=self.sport,
            short_value='exhibition',
            long_value='Exhibition',
            type=GenericChoice.GAME_TYPE
        )
        self.tz_name = 'US/Eastern'
        self.home_team = TeamFactory(name='New York Islanders')
        self.away_team = TeamFactory(name='New York Rangers', division=self.home_team.division)
        self.game = HockeyGameFactory(
            status=AbstractGame.SCHEDULED,
            type=self.game_type,
            point_value=self.point_value,
            start=pytz.utc.localize(datetime.datetime(year=2017, month=12, day=16, hour=19)),
            timezone=self.tz_name,
            home_team=self.home_team,
            away_team=self.away_team,
            period_duration=20,
        )
        HockeyGamePlayerFactory(
            team=self.home_team,
            game=self.game,
            player__position='G',
            is_starting=True,
        )
        HockeyGamePlayerFactory(
            team=self.away_team,
            game=self.game,
            player__position='G',
            is_starting=True,
        )
        self.form_cls = HockeyGameScoresheetForm

    def test_clean(self):
        form = self.form_cls(
            instance=self.game,
            data={'period_duration': 15},
            is_save_and_start_game_action=False,
        )
        form.is_valid()

        self.assertEqual(form.non_field_errors(), [])

        now = timezone.now()
        start = now + datetime.timedelta(hours=1)
        self.game.start = start
        self.game.end = start + datetime.timedelta(hours=2)
        self.game.save()
        form = self.form_cls(
            instance=self.game,
            data={'period_duration': 15},
            is_save_and_start_game_action=True,
        )
        form.is_valid()

        self.assertEqual(
            form.non_field_errors(),
            ['Games can only be started 30 minutes before the scheduled start time.']
        )
