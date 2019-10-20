from datetime import date, timedelta

from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.urls import reverse
from django.utils import timezone

from ayrabo.utils.testing import BaseTestCase
from divisions.tests import DivisionFactory
from leagues.tests import LeagueFactory
from players.tests import HockeyPlayerFactory
from seasons.models import HockeySeasonRoster, Season
from sports.tests import SportFactory
from teams.tests import TeamFactory
from . import HockeySeasonRosterFactory, SeasonFactory


class SeasonModelTests(BaseTestCase):
    def setUp(self):
        self.league = LeagueFactory()
        self.past_season, self.current_season, self.future_season = self.create_past_current_future_seasons(
            league=self.league
        )

    def test_to_string(self):
        season = SeasonFactory()
        self.assertEqual(str(season), f'{season.start_date.year}-{season.end_date.year} Season')

    def test_end_date_before_start_date(self):
        start_date = date(2016, 8, 15)
        end_date = start_date + timedelta(days=-365)
        with self.assertRaisesMessage(ValidationError, "The season's end date must be after the season's start date."):
            SeasonFactory(start_date=start_date, end_date=end_date).full_clean()

    def test_end_date_equal_to_start_date(self):
        start_date = date(2016, 8, 15)
        end_date = start_date
        with self.assertRaisesMessage(ValidationError, "The season's end date must be after the season's start date."):
            SeasonFactory(start_date=start_date, end_date=end_date).full_clean()

    def test_unique_together_start_date_league(self):
        league = LeagueFactory(name='Long Island Amateur Hockey League')
        start_date = date(2016, 8, 15)
        SeasonFactory(start_date=start_date, end_date=start_date + timedelta(days=365), league=league)
        with self.assertRaises(IntegrityError):
            SeasonFactory(start_date=start_date, end_date=start_date + timedelta(days=360), league=league)

    def test_unique_together_end_date_league(self):
        league = LeagueFactory(name='Long Island Amateur Hockey League')
        end_date = date(2016, 8, 15)
        SeasonFactory(start_date=date(2016, 8, 15), end_date=end_date, league=league)
        with self.assertRaises(IntegrityError):
            SeasonFactory(start_date=date(2016, 9, 23), end_date=end_date, league=league)

    def test_unique_for_year(self):
        start_date = date(2016, 8, 15)
        league = LeagueFactory(name='Long Island Amateur Hockey League')
        SeasonFactory(start_date=start_date, league=league)
        with self.assertRaisesMessage(ValidationError, "{'league': ['League must be unique for Start Date year.']}"):
            SeasonFactory(start_date=start_date + timedelta(days=30), league=league).full_clean()

    def test_default_ordering(self):
        # If end dates are the same, should then sort by start date desc
        s = SeasonFactory(
            start_date=self.future_season.end_date + timedelta(days=30),
            end_date=self.future_season.end_date
        )
        self.assertListEqual(list(Season.objects.all()), [s, self.future_season, self.current_season, self.past_season])

    def test_is_past(self):
        self.assertTrue(self.past_season.is_past)
        self.assertFalse(self.current_season.is_past)
        self.assertFalse(self.future_season.is_past)
        # Test when end date == now
        now = timezone.now().date()
        s = SeasonFactory(league=self.league, start_date=now - timedelta(days=30), end_date=now)
        self.assertFalse(s.is_past)

    def test_is_current(self):
        self.assertFalse(self.past_season.is_current)
        # start_date == now for the current season, which tests <=
        self.assertTrue(self.current_season.is_current)
        self.assertFalse(self.future_season.is_current)
        now = timezone.now().date()
        # Test when now is b/w start and end (not equal to)
        s = SeasonFactory(league=self.league, start_date=now - timedelta(days=60), end_date=now + timedelta(days=60))
        self.assertTrue(s.is_current)
        # Test when end date ==  now
        s = SeasonFactory(league=self.league, start_date=now - timedelta(days=30), end_date=now)
        self.assertTrue(s.is_current)

    def test_is_future(self):
        self.assertFalse(self.past_season.is_future)
        # start_date == now for the current season, which tests <=
        self.assertFalse(self.current_season.is_future)
        self.assertTrue(self.future_season.is_future)

    def test_league_detail_schedule_url(self):
        self.assertEqual(
            self.past_season.league_detail_schedule_url,
            reverse('leagues:seasons:schedule', kwargs={
                'slug': self.league.slug,
                'season_pk': self.past_season.pk,
            })
        )
        self.assertEqual(
            self.current_season.league_detail_schedule_url,
            reverse('leagues:schedule', kwargs={'slug': self.league.slug})
        )
        self.assertEqual(
            self.future_season.league_detail_schedule_url,
            reverse('leagues:seasons:schedule', kwargs={
                'slug': self.league.slug,
                'season_pk': self.future_season.pk,
            })
        )

    def test_league_detail_divisions_url(self):
        self.assertEqual(
            self.past_season.league_detail_divisions_url,
            reverse('leagues:seasons:divisions', kwargs={
                'slug': self.league.slug,
                'season_pk': self.past_season.pk,
            })
        )
        self.assertEqual(
            self.current_season.league_detail_divisions_url,
            reverse('leagues:divisions', kwargs={'slug': self.league.slug})
        )
        self.assertEqual(
            self.future_season.league_detail_divisions_url,
            reverse('leagues:seasons:divisions', kwargs={
                'slug': self.league.slug,
                'season_pk': self.future_season.pk,
            })
        )


class SeasonTeamM2MSignalTests(BaseTestCase):
    def setUp(self):
        self.liahl = LeagueFactory(name='Long Island Amateur Hockey League')
        self.nhl = LeagueFactory(name='National Hockey League')
        self.mites = DivisionFactory(name='Mites', league=self.liahl)
        self.midget_minor_aa = DivisionFactory(name='Midget Minor AA', league=self.liahl)
        self.pacific = DivisionFactory(name='Pacific Division', league=self.nhl)
        self.liahl_season = SeasonFactory(league=self.liahl)

    def test_add_teams_same_leagues_to_season_obj(self):
        """
        Not reverse, i.e. season_obj.teams.add(team_obj), so pk_set contains pks for team objects
        """
        # self.mites are a part of the same league...
        icecats = TeamFactory(division=self.mites, name='IceCats')
        sharks = TeamFactory(division=self.mites, name='San Jose Sharks')
        self.assertListEqual([], list(self.liahl_season.teams.all()))
        self.liahl_season.teams.add(icecats, sharks)
        self.assertListEqual([icecats, sharks], list(self.liahl_season.teams.all()))

    def test_add_teams_diff_leagues_to_season_obj(self):
        """
        Not reverse, i.e. season_obj.teams.add(team_obj), so pk_set contains pks for team objects
        """
        # Different divisions and leagues will be created by factory boy.
        icecats = TeamFactory(name='IceCats')
        sharks = TeamFactory(name='San Jose Sharks')
        self.assertListEqual([], list(self.liahl_season.teams.all()))
        self.liahl_season.teams.add(icecats, sharks)
        self.assertListEqual([], list(self.liahl_season.teams.all()))

    def test_add_season_diff_league_to_team_obj(self):
        """
        reverse, i.e. team_obj.seasons.add(season_obj), so pk_set contains pks for season objects
        """
        team = TeamFactory(division=self.mites, name='IceCats')
        s1 = SeasonFactory()
        s2 = SeasonFactory(league=self.nhl)
        self.assertListEqual([], list(team.seasons.all()))
        team.seasons.add(s1, s2)
        self.assertListEqual([], list(team.seasons.all()))

    def test_add_season_same_league_to_team_obj(self):
        """
        reverse, i.e. team_obj.seasons.add(season_obj), so pk_set contains pks for season objects
        """
        start_date = date(2016, 8, 15)
        end_date = start_date + timedelta(days=365)
        team = TeamFactory(division=self.mites, name='IceCats')
        s1 = SeasonFactory(league=self.liahl, start_date=start_date, end_date=end_date)
        s2 = SeasonFactory(league=self.liahl, start_date=start_date - timedelta(days=365),
                           end_date=end_date - timedelta(days=365))
        self.assertListEqual([], list(team.seasons.all()))
        team.seasons.add(s1, s2)
        self.assertListEqual([s1, s2], list(team.seasons.all()))

    def test_invalid_pks(self):
        team = TeamFactory()
        self.liahl_season.teams.add(team.id)
        self.assertListEqual([], list(self.liahl_season.teams.all()))


class AbstractSeasonRosterModelTests(BaseTestCase):
    """
    We can't create an instance of AbstractSeasonRosterFactory so just default to the hockey factory
    """

    def test_to_string(self):
        ice_hockey = SportFactory(name='Ice Hockey')
        liahl = LeagueFactory(sport=ice_hockey, name='Long Island Amateur Hockey League')
        mm_aa = DivisionFactory(league=liahl, name='Midget Minor AA')
        icecats = TeamFactory(name='Green Machine IceCats', division=mm_aa)
        season = SeasonFactory(league=liahl, teams=[icecats])
        season_roster = HockeySeasonRosterFactory(team=icecats)
        self.assertEqual(str(season_roster), '{}-{}: {}'.format('Green Machine IceCats', 'Midget Minor AA', season))

    def test_roster_default_false(self):
        season_roster = HockeySeasonRosterFactory()
        self.assertFalse(season_roster.default)

    def test_default_ordering(self):
        rosters = []
        start_time = timezone.now()
        for i in range(5):
            rosters.append(HockeySeasonRosterFactory(created=start_time + timedelta(hours=i * 10)))

        self.assertListEqual(rosters, list(HockeySeasonRoster.objects.all()))

    def test_get_latest(self):
        rosters = []
        start_time = timezone.now()
        for i in range(5):
            rosters.append(HockeySeasonRosterFactory(created=start_time + timedelta(hours=i * 10)))

        latest_obj = rosters[len(rosters) - 1]
        self.assertEqual(latest_obj.pk, HockeySeasonRoster.objects.latest().pk)

    def test_get_absolute_url(self):
        season_roster = HockeySeasonRosterFactory()
        self.assertEqual(season_roster.get_absolute_url(), reverse('teams:season_rosters:update',
                                                                   kwargs={'team_pk': season_roster.team.pk,
                                                                           'pk': season_roster.pk}))

    def test_unique_name_season_and_team(self):
        division = DivisionFactory()
        team = TeamFactory(division=division)
        season = SeasonFactory(league=division.league, teams=[team])
        HockeySeasonRosterFactory(season=season, team=team, name='Main Squad')
        msg = "{'name': ['Name must be unique for this team and season.']}"
        with self.assertRaisesMessage(ValidationError, msg):
            HockeySeasonRosterFactory(season=season, team=team, name='Main Squad')

    def test_can_update(self):
        league = LeagueFactory()
        past_season, current_season, _ = self.create_past_current_future_seasons(league=league)
        past_season_roster = HockeySeasonRosterFactory(season=past_season)
        current_season_roster = HockeySeasonRosterFactory(season=current_season)

        self.assertFalse(past_season_roster.can_update())
        self.assertTrue(current_season_roster.can_update())


class HockeySeasonRosterModelTests(BaseTestCase):
    def setUp(self):
        self.division = DivisionFactory()
        self.team = TeamFactory(division=self.division)
        self.season = SeasonFactory(league=self.division.league, teams=[self.team])
        self.season_roster = HockeySeasonRosterFactory(season=self.season, team=self.team, default=True)

    def test_clean_default(self):
        with self.assertRaisesMessage(ValidationError, "{'default': ['A default season roster for this team and "
                                                       "season already exists.']}"):
            HockeySeasonRosterFactory(season=self.season, team=self.team, default=True).full_clean()

    def test_excludes_current_obj_from_clean_default(self):
        # There was a bug where a default season roster couldn't be updated because it wasn't excluded from the
        # clean_default query
        self.season_roster.players.add(HockeyPlayerFactory(team=self.team, sport=self.team.division.league.sport))
        self.season_roster.full_clean()

    def test_get_players(self):
        sport = self.team.division.league.sport
        player1 = HockeyPlayerFactory(team=self.team, sport=sport, jersey_number=1)
        player2 = HockeyPlayerFactory(team=self.team, sport=sport, jersey_number=2)
        player3 = HockeyPlayerFactory(team=self.team, sport=sport, jersey_number=3)
        player4 = HockeyPlayerFactory(team=self.team, sport=sport, jersey_number=4)
        player4.is_active = False
        player4.save()
        self.season_roster.players.add(player1, player2, player3, player4)
        self.assertListEqual(list(self.season_roster.get_players()), [player1, player2, player3])
