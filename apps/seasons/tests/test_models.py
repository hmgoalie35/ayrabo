import datetime

from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.test import TestCase

from divisions.tests import DivisionFactory
from seasons.models import Season
from teams.tests import TeamFactory
from . import SeasonFactory


class SeasonModelTests(TestCase):
    def test_to_string(self):
        season = SeasonFactory()
        self.assertEqual(str(season), '{start_year} - {end_year} Season'.format(start_year=season.start_date.year,
                                                                                end_year=season.end_date.year))

    def test_end_date_before_start_date(self):
        start_date = datetime.date(2016, 8, 15)
        end_date = start_date + datetime.timedelta(days=-365)
        with self.assertRaises(ValidationError, msg="The season's end date must be after the season's start date."):
            SeasonFactory(start_date=start_date, end_date=end_date).full_clean()

    def test_end_date_equal_to_start_date(self):
        start_date = datetime.date(2016, 8, 15)
        end_date = start_date
        with self.assertRaises(ValidationError, msg="The season's end date must be after the season's start date."):
            SeasonFactory(start_date=start_date, end_date=end_date).full_clean()

    def test_unique_together_start_date_division(self):
        division = DivisionFactory(name='Mites')
        start_date = datetime.date(2016, 8, 15)
        SeasonFactory(start_date=start_date, division=division)
        with self.assertRaises(IntegrityError,
                               msg='UNIQUE constraint failed: seasons_season.start_date, seasons_season.division_id'):
            SeasonFactory(start_date=start_date, division=division)

    def test_unique_together_end_date_division(self):
        division = DivisionFactory(name='Mites')
        end_date = datetime.date(2016, 8, 15)
        SeasonFactory(end_date=end_date, division=division)
        with self.assertRaises(IntegrityError,
                               msg='UNIQUE constraint failed: seasons_season.end_date, seasons_season.division_id'):
            SeasonFactory(end_date=end_date, division=division)

    def test_unique_for_year(self):
        start_date = datetime.date(2016, 8, 15)
        division = DivisionFactory(name='Mites')
        SeasonFactory(start_date=start_date, division=division)
        with self.assertRaisesMessage(ValidationError,
                                      "{'division': ['Division must be unique for Start Date year.']}"):
            SeasonFactory(start_date=start_date + datetime.timedelta(days=30), division=division).full_clean()

    def test_default_ordering(self):
        start_date = datetime.date(2014, 8, 15)
        end_date = datetime.date(2015, 8, 15)
        division = DivisionFactory(name='Mites')
        seasons = []
        for i in range(3):
            start = start_date + datetime.timedelta(days=i * 365)
            end = end_date + datetime.timedelta(days=i * 365)
            season = SeasonFactory(start_date=start, end_date=end, division=division)
            seasons.append(season)
        self.assertListEqual(list(reversed(seasons)), list(Season.objects.all()))


class SeasonTeamM2MSignalTests(TestCase):
    def setUp(self):
        self.mites = DivisionFactory(name='Mites')
        self.midget_minor_aa = DivisionFactory(name='Midget Minor AA')
        self.pacific = DivisionFactory(name='Pacific Division')
        self.mites_season = SeasonFactory(division=self.mites)

    def test_add_teams_same_divisions_to_season_obj(self):
        """
        Not reverse, i.e. season_obj.teams.add(team_obj), so pk_set contains pks for team objects
        """
        icecats = TeamFactory(division=self.mites, name='IceCats')
        sharks = TeamFactory(division=self.mites, name='San Jose Sharks')
        self.assertListEqual([], list(self.mites_season.teams.all()))
        self.mites_season.teams.add(icecats, sharks)
        self.assertListEqual([icecats, sharks], list(self.mites_season.teams.all()))

    def test_add_teams_diff_divisions_to_season_obj(self):
        """
        Not reverse, i.e. season_obj.teams.add(team_obj), so pk_set contains pks for team objects
        """
        icecats = TeamFactory(division=self.midget_minor_aa, name='IceCats')
        sharks = TeamFactory(division=self.pacific, name='San Jose Sharks')
        self.assertListEqual([], list(self.mites_season.teams.all()))
        self.mites_season.teams.add(icecats, sharks)
        self.assertListEqual([], list(self.mites_season.teams.all()))

    def test_add_season_diff_division_to_team_obj(self):
        """
        reverse, i.e. team_obj.season_set.add(season_obj), so pk_set contains pks for season objects
        """
        team = TeamFactory(division=self.mites, name='IceCats')
        s1 = SeasonFactory(division=self.midget_minor_aa)
        s2 = SeasonFactory(division=self.pacific)
        self.assertListEqual([], list(team.season_set.all()))
        team.season_set.add(s1, s2)
        self.assertListEqual([], list(team.season_set.all()))

    def test_add_season_same_division_to_team_obj(self):
        """
        reverse, i.e. team_obj.season_set.add(season_obj), so pk_set contains pks for season objects
        """
        start_date = datetime.date(2016, 8, 15)
        end_date = start_date + datetime.timedelta(days=365)
        team = TeamFactory(division=self.mites, name='IceCats')
        s1 = SeasonFactory(division=self.mites, start_date=start_date, end_date=end_date)
        s2 = SeasonFactory(division=self.mites, start_date=start_date - datetime.timedelta(days=365),
                           end_date=end_date - datetime.timedelta(days=365))
        self.assertListEqual([], list(team.season_set.all()))
        team.season_set.add(s1, s2)
        self.assertListEqual([s1, s2], list(team.season_set.all()))

    def test_invalid_pks(self):
        self.mites_season.teams.add(88)
        self.assertListEqual([], list(self.mites_season.teams.all()))
