from escoresheet.utils.testing_utils import BaseTestCase
from leagues.tests import LeagueFactory
from referees.forms import RefereeForm
from sports.tests import SportFactory
from accounts.tests import UserFactory
from referees.tests import RefereeFactory


class RefereeFormTests(BaseTestCase):
    def setUp(self):
        self.sport = SportFactory(name='Ice Hockey')
        self.form_cls = RefereeForm

    def test_leagues_filtered_by_sport(self):
        LeagueFactory(sport=self.sport)
        league_different_sport = LeagueFactory()

        form = self.form_cls(sport=self.sport)
        league_field = form.fields['league']
        self.assertNotIn(league_different_sport, league_field.queryset)

    def test_no_sport_kwarg(self):
        leagues = [LeagueFactory(sport=self.sport)]
        league_different_sport = LeagueFactory()
        leagues.append(league_different_sport)

        form = self.form_cls()
        league_field = form.fields['league']
        self.assertTrue(set(leagues).issubset(set(league_field.queryset)))

    def test_sets_fields_disabled(self):
        form = self.form_cls(read_only_fields=['league'])
        self.assertTrue(form.fields['league'].disabled)

    def test_leagues_already_registered_for(self):
        """
        Leagues already registered for should be excluded
        """
        user = UserFactory()
        leagues = LeagueFactory.create_batch(5)
        RefereeFactory(user=user, league=leagues[0])
        form = self.form_cls(already_registered_for=[leagues[0].id])
        league_field = form.fields['league']
        self.assertNotIn(leagues[0], league_field.queryset)
