from django.db.utils import IntegrityError
from django.utils.text import slugify

from divisions.tests import DivisionFactory
from escoresheet.utils.testing import BaseTestCase
from leagues.tests import LeagueFactory
from sports.tests import SportFactory
from teams.models import Team
from .factories.TeamFactory import TeamFactory


class TeamModelTests(BaseTestCase):
    def setUp(self):
        self.ice_hockey = SportFactory.create(name='Ice Hockey')
        self.liahl = LeagueFactory.create(full_name='Long Island Amateur Hockey League', sport=self.ice_hockey)
        self.pee_wee_division = DivisionFactory.create(name='Pee Wee AA', league=self.liahl)

    def test_default_ordering(self):
        green_machine = TeamFactory(name='Green Machine IceCats')
        aviator = TeamFactory(name='Aviator Gulls')
        rebels = TeamFactory(name='Rebels')
        expected = [aviator, green_machine, rebels]
        self.assertListEqual(list(Team.objects.all()), expected)

    def test_name_unique_to_division_raises_error(self):
        """
        Same team name, same division -> throws error
        Team name must be unique to a division
        """
        TeamFactory.create(name='Green Machine IceCats', division=self.pee_wee_division)
        with self.assertRaises(IntegrityError):
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
        self.assertEqual(str(icecats), icecats.name)

    def test_slug_generation(self):
        icecats = TeamFactory(name='Green Machine IceCats', division=self.pee_wee_division)
        self.assertEqual(icecats.slug, slugify(icecats.name))

    def test_slug_unique_with_division(self):
        TeamFactory(name='Green Machine IceCats', division=self.pee_wee_division)
        with self.assertRaises(IntegrityError):
            # make sure the team name is not the same as above, or it will fail the uniqueness constraint for name
            TeamFactory(name='green machine iceCats', division=self.pee_wee_division)
