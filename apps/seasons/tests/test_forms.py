import datetime

from ayrabo.utils.form_fields import PlayerModelMultipleChoiceField
from ayrabo.utils.testing import BaseTestCase
from divisions.tests import DivisionFactory
from leagues.tests import LeagueFactory
from players.tests import HockeyPlayerFactory
from seasons.forms import HockeySeasonRosterCreateUpdateForm
from seasons.tests import SeasonFactory
from sports.tests import SportFactory
from teams.tests import TeamFactory


class HockeySeasonRosterCreateUpdateFormTests(BaseTestCase):
    form_cls = HockeySeasonRosterCreateUpdateForm

    def get_form(self, **kwargs):
        return self.form_cls(team=self.team, **kwargs)

    def setUp(self):
        self.sport = SportFactory(name='Ice Hockey')
        self.league = LeagueFactory(sport=self.sport, name='Long Island Amateur Hockey League')
        self.division = DivisionFactory(league=self.league, name='Midget Minor AA')
        self.teams = TeamFactory.create_batch(5, division=self.division)
        self.team = self.teams[0]
        self.season1 = SeasonFactory(league=self.league, teams=self.teams)
        self.season2 = SeasonFactory(league=self.league, teams=self.teams,
                                     start_date=datetime.date.today() + datetime.timedelta(weeks=4))

    def test_seasons_filtered_by_league(self):
        # Season for another league
        SeasonFactory()

        form = self.get_form()
        qs = form.fields['season'].queryset
        self.assertListEqual(list(qs), [self.season2, self.season1])

    def test_hockeyplayers_filtered_by_team(self):
        players = HockeyPlayerFactory.create_batch(5, team=self.team, sport=self.sport)
        # Inactive player
        HockeyPlayerFactory(team=self.team, sport=self.sport, is_active=False)
        # Player for a different team
        HockeyPlayerFactory(sport=self.sport)

        form = self.get_form()
        qs = form.fields['players'].queryset
        self.assertListEqual(list(qs), players)

    def test_players_displayed_correctly(self):
        form = self.get_form()
        self.assertIsInstance(form.fields['players'], PlayerModelMultipleChoiceField)

    def test_disabling_fields(self):
        form = self.get_form(disable=['season'])
        self.assertTrue(form.fields['season'].disabled)
