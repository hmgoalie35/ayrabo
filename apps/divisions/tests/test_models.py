from django.db.utils import IntegrityError
from django.test import TestCase

from divisions.models import Division
from escoresheet.testing_utils import is_queryset_in_alphabetical_order
from leagues.tests.factories.LeagueFactory import LeagueFactory
from .factories.DivisionFactory import DivisionFactory


class DivisionModelTests(TestCase):
    def test_default_ordering(self):
        DivisionFactory.create_batch(5)
        self.assertTrue(is_queryset_in_alphabetical_order(Division.objects.all(), 'name'))

    def test_to_string(self):
        metro_division = DivisionFactory.create(name='Metropolitan Division')
        self.assertEqual(str(metro_division), 'Metropolitan Division')

    def test_duplicate_division_name_same_league(self):
        league = LeagueFactory(full_name='Long Island Amateur Hockey League')
        DivisionFactory.create(name='Default', league=league)
        with self.assertRaises(IntegrityError,
                               msg='UNIQUE constraint failed: divisions_division.name, divisions_division.league_id'):
            DivisionFactory.create(name='Default', league=league)

    def test_duplicate_division_name_different_league(self):
        # shouldn't throw an error
        liahl = LeagueFactory(full_name='Long Island Amateur Hockey League')
        nhl = LeagueFactory(full_name='National Hockey League')
        DivisionFactory.create(name='Default', league=liahl)
        DivisionFactory.create(name='Default', league=nhl)
