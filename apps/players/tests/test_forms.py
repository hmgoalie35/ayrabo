from divisions.tests import DivisionFactory
from escoresheet.utils import BaseTestCase
from leagues.tests import LeagueFactory
from players.forms import HockeyPlayerForm
from sports.tests import SportFactory
from teams.tests import TeamFactory


class PlayerFormTests(BaseTestCase):
    """
    Even though this is testing `PlayerForm`, we use `HockeyPlayerForm` because the form needs
    a model attribute in `Meta`
    """

    def setUp(self):
        self.sport = SportFactory(name='Ice Hockey')
        self.league = LeagueFactory(sport=self.sport, full_name='Long Island Amateur Hockey League')
        self.division = DivisionFactory(league=self.league, name='Midget Minor AA')
        self.form_cls = HockeyPlayerForm

    def test_teams_filtered_by_sport(self):
        TeamFactory.create_batch(5, division=self.division)
        team_different_sport = TeamFactory()
        form = self.form_cls(sport=self.sport)

        team_field = form.fields['team']

        self.assertNotIn(team_different_sport, team_field.queryset)

    def test_no_sport_kwarg(self):
        teams = TeamFactory.create_batch(2, division=self.division)
        team_different_sport = TeamFactory()
        form = self.form_cls()
        team_field = form.fields['team']

        teams.append(team_different_sport)

        self.assertTrue(set(teams).issubset(set(team_field.queryset)))

    def test_fields_set_to_disabled(self):
        form = self.form_cls(read_only_fields=['team'])
        self.assertTrue(form.fields['team'].disabled)

    def test_no_read_only_fields_kwarg(self):
        form = self.form_cls()
        self.assertFalse(form.fields['team'].disabled)


# As of now no need to add in tests for the different forms, they aren't doing anything special
