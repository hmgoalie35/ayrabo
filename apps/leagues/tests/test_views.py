from datetime import date, timedelta

from ayrabo.utils.testing import BaseTestCase
from common.tests import GenericChoiceFactory
from divisions.tests import DivisionFactory
from games.tests import HockeyGameFactory
from leagues.tests import LeagueFactory
from managers.tests import ManagerFactory
from organizations.tests import OrganizationFactory
from seasons.tests import SeasonFactory
from sports.tests import SportFactory
from teams.tests import TeamFactory
from users.tests import UserFactory


class LeagueScheduleViewTests(BaseTestCase):
    url = 'leagues:schedule'

    def _create_game(self, home_team, away_team, season):
        return HockeyGameFactory(home_team=home_team, away_team=away_team, team=home_team, season=season,
                                 type=self.game_type, point_value=self.point_value)

    def setUp(self):
        self.user = UserFactory()
        self.ice_hockey = SportFactory(name='Ice Hockey')
        self.liahl = LeagueFactory(name='Long Island Amateur Hockey League', sport=self.ice_hockey)
        self.nhl = LeagueFactory(name='National Hockey League', sport=self.ice_hockey)
        self.mm_aa = DivisionFactory(league=self.liahl, name='Midget Minor AA')
        self.peewee = DivisionFactory(league=self.liahl, name='Pee Wee')
        self.atlantic = DivisionFactory(league=self.nhl, name='Atlantic')

        self.icecats_organization = OrganizationFactory(name='Green Machine IceCats', sport=self.ice_hockey)
        self.edge_organization = OrganizationFactory(name='Long Island Edge', sport=self.ice_hockey)
        self.rebels_organization = OrganizationFactory(name='Long Island Rebels', sport=self.ice_hockey)
        self.bruins_organization = OrganizationFactory(name='Boston Bruins', sport=self.ice_hockey)
        self.sabres_organization = OrganizationFactory(name='Buffalo Sabres', sport=self.ice_hockey)

        # Teams
        self.icecats_mm_aa = TeamFactory(name='Green Machine IceCats', division=self.mm_aa,
                                         organization=self.icecats_organization)
        self.icecats_peewee = TeamFactory(name='Green Machine IceCats', division=self.peewee,
                                          organization=self.icecats_organization)
        self.managers = [ManagerFactory(user=self.user, team=self.icecats_mm_aa)]
        self.edge_mm_aa = TeamFactory(name='Long Island Edge', division=self.mm_aa,
                                      organization=self.edge_organization)
        self.edge_peewee = TeamFactory(name='Long Island Edge', division=self.peewee,
                                       organization=self.edge_organization)

        self.rebels_mm_aa = TeamFactory(name='Long Island Rebels', division=self.mm_aa,
                                        organization=self.rebels_organization)
        self.rebels_peewee = TeamFactory(name='Long Island Rebels', division=self.peewee,
                                         organization=self.rebels_organization)
        self.bruins = TeamFactory(name='Boston Bruins', division=self.atlantic, organization=self.bruins_organization)
        self.sabres = TeamFactory(name='Buffalo Sabres', division=self.atlantic, organization=self.sabres_organization)

        teams = [self.icecats_mm_aa, self.icecats_peewee, self.edge_mm_aa, self.edge_peewee, self.rebels_mm_aa,
                 self.rebels_peewee]

        self.start_date = date.today()
        self.past_start_date = self.start_date - timedelta(days=365)
        self.future_start_date = self.start_date + timedelta(days=365)
        self.previous_season = SeasonFactory(league=self.liahl, start_date=self.past_start_date,
                                             end_date=self.start_date,
                                             teams=teams)
        self.current_season = SeasonFactory(league=self.liahl, start_date=self.start_date,
                                            end_date=self.future_start_date, teams=teams)
        self.next_season = SeasonFactory(league=self.liahl, start_date=self.future_start_date,
                                         end_date=self.future_start_date + timedelta(days=365), teams=teams)

        self.game_type = GenericChoiceFactory(short_value='exhibition', long_value='Exhibition', type='game_type',
                                              content_object=self.ice_hockey)
        self.point_value = GenericChoiceFactory(short_value='2', long_value='2', type='game_point_value',
                                                content_object=self.ice_hockey)
        self.game1 = self._create_game(self.icecats_mm_aa, self.edge_mm_aa, self.current_season)
        self.game2 = self._create_game(self.icecats_mm_aa, self.rebels_mm_aa, self.current_season)
        self.game3 = self._create_game(self.icecats_peewee, self.edge_peewee, self.current_season)
        self._create_game(self.icecats_peewee, self.rebels_peewee, self.previous_season)
        # Game for another league (should be excluded)
        self._create_game(self.bruins, self.sabres, SeasonFactory(league=self.nhl))
        self.games = [self.game1, self.game2, self.game3]
        self.login(user=self.user)

    def test_login_required(self):
        self.client.logout()
        self.assertLoginRequired(self.format_url(slug=self.liahl.slug))

    def test_sport_not_configured(self):
        sport = SportFactory()
        league = LeagueFactory(sport=sport)
        self.assertSportNotConfigured(self.format_url(slug=league.slug))

    # GET
    def test_get(self):
        response = self.client.get(self.format_url(slug=self.liahl.slug))
        team_ids_managed_by_user = [m.team_id for m in self.managers]
        context = response.context
        self.assert_200(response)
        self.assertTemplateUsed(response, 'leagues/league_detail_schedule.html')
        self.assertEqual(context.get('league'), self.liahl)
        self.assertEqual(context.get('sport'), self.ice_hockey)
        self.assertEqual(context.get('active_tab'), 'schedule')
        self.assertEqual(context.get('season'), self.current_season)
        self.assertListEqual(list(context.get('team_ids_managed_by_user')), team_ids_managed_by_user)
        self.assertListEqual(list(context.get('games')), self.games)
