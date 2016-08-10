from django.db.utils import IntegrityError
from django.test import TestCase
from django.utils.text import slugify

from divisions.tests import DivisionFactory
from escoresheet.testing_utils import is_queryset_in_alphabetical_order
from leagues.tests.factories.LeagueFactory import LeagueFactory
from sports.tests.factories.SportFactory import SportFactory
from teams.models import Team
from .factories.TeamFactory import TeamFactory


class TeamModelTests(TestCase):
    def setUp(self):
        self.ice_hockey = SportFactory.create(name='Ice Hockey')
        self.liahl = LeagueFactory.create(full_name='Long Island Amateur Hockey League', sport=self.ice_hockey)
        self.pee_wee_division = DivisionFactory.create(name='Pee Wee AA', league=self.liahl)

    def test_default_ordering(self):
        TeamFactory.create_batch(5)
        self.assertTrue(is_queryset_in_alphabetical_order(Team.objects.all(), 'name'))

    def test_name_unique_to_division_raises_error(self):
        """
        Same team name, same division -> throws error
        Team name must be unique to a division
        """
        TeamFactory.create(name='Green Machine IceCats', division=self.pee_wee_division)
        with self.assertRaises(IntegrityError, msg='UNIQUE constraint failed: teams_team.name, teams_team.division_id'):
            # Try to create a team with the same name and division
            TeamFactory.create(name='Green Machine IceCats', division=self.pee_wee_division)

    def test_name_unique_to_division_diff_divisions(self):
        """
        Same team name, different divisions -> is ok
        Team name is not unique, but the divisions are different
        """
        team_name = 'Green Machine IceCats'
        midgets = DivisionFactory.create(name='Midget Minor AAA', league=self.liahl)

        # Teams with same name are created but for different divisions, so this is ok
        TeamFactory.create(name=team_name, division=self.pee_wee_division)
        TeamFactory.create(name=team_name, division=midgets)

    def test_to_string(self):
        icecats = TeamFactory.create(name='Green Machine IceCats', division=self.pee_wee_division)
        self.assertEqual(str(icecats), '{division} - {name}'.format(division=icecats.division.name, name=icecats.name))

    def test_slug_generation(self):
        icecats = TeamFactory(name='Green Machine IceCats', division=self.pee_wee_division)
        self.assertEqual(icecats.slug, slugify(icecats.name))

    def test_slug_unique_with_division(self):
        TeamFactory(name='Green Machine IceCats', division=self.pee_wee_division)
        with self.assertRaises(IntegrityError, msg='UNIQUE constraint failed: teams_team.slug, teams_team.division_id'):
            # make sure the team name is not the same as above, or it will fail the uniqueness constraint for name
            TeamFactory(name='green machine iceCats', division=self.pee_wee_division)
