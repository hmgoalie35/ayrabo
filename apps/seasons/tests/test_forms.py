import datetime

from divisions.tests import DivisionFactory
from escoresheet.utils.testing_utils import BaseTestCase
from leagues.tests import LeagueFactory
from players.tests import HockeyPlayerFactory
from seasons.forms import CreateHockeySeasonRosterForm, UpdateHockeySeasonRosterForm
from seasons.tests import SeasonFactory
from sports.tests import SportFactory
from teams.tests import TeamFactory


class CreateHockeySeasonRosterFormTests(BaseTestCase):
    def setUp(self):
        self.sport = SportFactory(name='Ice Hockey')
        self.league = LeagueFactory(sport=self.sport, full_name='Long Island Amateur Hockey League')
        self.division = DivisionFactory(league=self.league, name='Midget Minor AA')
        self.teams = TeamFactory.create_batch(5, division=self.division)
        self.season1 = SeasonFactory(league=self.league, teams=self.teams)
        self.season2 = SeasonFactory(league=self.league, teams=self.teams,
                                     start_date=datetime.date.today() + datetime.timedelta(weeks=4))
        self.form_cls = CreateHockeySeasonRosterForm

    def test_sets_fields_disabled(self):
        form = self.form_cls(read_only_fields=['team'])
        self.assertTrue(form.fields['team'].disabled)

    def test_seasons_filtered_by_league(self):
        season_other_league = SeasonFactory()

        form = self.form_cls(league=self.league)
        season_field = form.fields['season']
        self.assertNotIn(season_other_league, season_field.queryset)

    def test_no_past_seasons(self):
        today = datetime.date.today()
        today_last_year = today - datetime.timedelta(days=365)
        today_2_years_ago = today - datetime.timedelta(days=365 * 2)
        season_ending_today = SeasonFactory(league=self.league, start_date=today_last_year, end_date=today)
        season_ended_2_yrs_ago = SeasonFactory(league=self.league, start_date=today_2_years_ago)

        form = self.form_cls(league=self.league)
        season_field = form.fields['season']
        self.assertNotIn(season_ended_2_yrs_ago, season_field.queryset)
        # Test edge case where season ends today
        self.assertIn(season_ending_today, season_field.queryset)

    def test_teams_filtered_by_league(self):
        team_different_league = TeamFactory()

        form = self.form_cls(league=self.league)
        team_field = form.fields['team']
        self.assertNotIn(team_different_league, team_field.queryset)

    def test_hockeyplayers_filtered_by_team(self):
        HockeyPlayerFactory.create_batch(5, team=self.teams[0], sport=self.sport)
        hockeyplayer_different_team = HockeyPlayerFactory(sport=self.sport)

        form = self.form_cls(team=self.teams[0])
        players_field = form.fields['players']
        self.assertNotIn(hockeyplayer_different_team, players_field.queryset)


class UpdateHockeySeasonRosterFormTests(BaseTestCase):
    def setUp(self):
        self.sport = SportFactory(name='Ice Hockey')
        self.league = LeagueFactory(sport=self.sport, full_name='Long Island Amateur Hockey League')
        self.division = DivisionFactory(league=self.league, name='Midget Minor AA')
        self.team = TeamFactory(division=self.division)
        self.form_cls = UpdateHockeySeasonRosterForm

    def test_hockeyplayers_filtered_by_team(self):
        HockeyPlayerFactory.create_batch(5, team=self.team, sport=self.sport)
        hockeyplayer_different_team = HockeyPlayerFactory(sport=self.sport)

        form = self.form_cls(team=self.team)
        players_field = form.fields['players']
        self.assertNotIn(hockeyplayer_different_team, players_field.queryset)
