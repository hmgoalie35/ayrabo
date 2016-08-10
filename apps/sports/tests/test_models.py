from django.core.urlresolvers import reverse
from django.db.utils import IntegrityError
from django.test import TestCase
from django.utils.text import slugify

from accounts.tests import UserFactory
from coaches.tests.factories.CoachFactory import CoachFactory
from divisions.tests.factories.DivisionFactory import DivisionFactory
from escoresheet.testing_utils import is_queryset_in_alphabetical_order
from leagues.tests.factories.LeagueFactory import LeagueFactory
from managers.tests.factories.ManagerFactory import ManagerFactory
from players.tests.factories.PlayerFactory import HockeyPlayerFactory
from referees.tests.factories.RefereeFactory import RefereeFactory
from sports.models import Sport, SportRegistration
from teams.tests.factories.TeamFactory import TeamFactory
from .factories.SportFactory import SportFactory
from .factories.SportRegistrationFactory import SportRegistrationFactory


class SportModelTests(TestCase):
    # Slugs are auto generated from the name attribute, so the uniqueness of slugs makes sure names are also unique for case insensitive
    # ice Hockey and Ice Hockey will pass the uniqueness of the name field, but won't pass uniqueness of slug field
    def test_unique_names_case_sensitive(self):
        SportFactory.create(name='Ice Hockey')
        with self.assertRaises(IntegrityError, msg='UNIQUE constraint failed: sports_sport.name'):
            SportFactory.create(name='Ice Hockey')

    def test_unique_slugs_case_insensitive(self):
        # Slug is autogenerated via overridden .clean() method
        SportFactory.create(name='ice Hockey')
        with self.assertRaises(IntegrityError, msg='UNIQUE constraint failed: sports_sport.slug'):
            SportFactory.create(name='ice hockey')

    def test_slug_generation(self):
        ice_hockey = SportFactory.create(name='Ice hockey')
        self.assertEqual(ice_hockey.slug, slugify(ice_hockey.name))

    def test_default_ordering(self):
        SportFactory.create_batch(5)
        self.assertTrue(is_queryset_in_alphabetical_order(Sport.objects.all(), 'name'))

    def test_to_string(self):
        sport = SportFactory.build(name='Ice Hockey')
        self.assertEqual(str(sport), 'Ice Hockey')

    def test_name_converted_to_titlecase(self):
        sport = SportFactory.create(name='ice hockey')
        self.assertEqual(sport.name, 'Ice Hockey')


class SportRegistrationModelTests(TestCase):
    def test_default_ordering(self):
        SportRegistrationFactory(sport__name='Ice Hockey')
        SportRegistrationFactory(sport__name='Soccer')
        SportRegistrationFactory(sport__name='Tennis')
        self.assertTrue(is_queryset_in_alphabetical_order(SportRegistration.objects.all(), 'sport', fk='name'))
        self.assertTrue(is_queryset_in_alphabetical_order(SportRegistration.objects.all(), 'user', fk='email'))

    def test_to_string(self):
        sr = SportRegistrationFactory()
        self.assertEqual(str(sr), '{email} - {sport}'.format(email=sr.user.email, sport=sr.sport.name))

    def test_absolute_url(self):
        ice_hockey = SportRegistrationFactory(sport__name='Ice Hockey')
        self.assertEqual(ice_hockey.get_absolute_url(),
                         reverse('sport:update_sport_registration', kwargs={'pk': ice_hockey.pk}))

    def test_current_available_roles(self):
        self.assertListEqual(SportRegistration.ROLES, ['Player', 'Coach', 'Referee', 'Manager'])

    def test_set_roles_param_not_a_list(self):
        sr = SportRegistrationFactory()
        with self.assertRaises(AssertionError):
            sr.set_roles(('Player', 'Manager'))

    def test_set_roles_no_append(self):
        sr = SportRegistrationFactory()
        sr.set_roles(['Player', 'Manager'])
        self.assertEqual(sr.roles_mask, 9)

    def test_set_roles_append(self):
        sr = SportRegistrationFactory()
        sr.set_roles(['Player', 'Manager'])
        sr.set_roles(['Coach'], append=True)
        self.assertEqual(sr.roles_mask, 11)

    def test_set_roles_invalid_role(self):
        sr = SportRegistrationFactory()
        sr.set_roles(['Referee', 'Invalid'])
        self.assertEqual(sr.roles, ['Referee'])

    def test_set_roles_empty_list(self):
        sr = SportRegistrationFactory()
        sr.set_roles([])
        self.assertEqual(sr.roles_mask, 0)

    def test_roles_property(self):
        roles = ['Player', 'Manager']
        sr = SportRegistrationFactory()
        sr.set_roles(roles)
        self.assertEqual(sr.roles, roles)

    def test_has_role_true(self):
        roles = ['Player', 'Manager']
        sr = SportRegistrationFactory()
        sr.set_roles(roles)
        self.assertTrue(sr.has_role('Player'))
        self.assertTrue(sr.has_role('manager'))

    def test_has_role_false(self):
        roles = ['Coach', 'Manager']
        sr = SportRegistrationFactory()
        sr.set_roles(roles)
        self.assertFalse(sr.has_role('Player'))
        self.assertFalse(sr.has_role('InvalidRole'))

    def test_user_unique_with_sport(self):
        user = UserFactory(email='testing@example.com')
        sport = SportFactory(name='Ice Hockey')
        SportRegistrationFactory(user=user, sport=sport)
        with self.assertRaises(IntegrityError,
                               msg='UNIQUE constraint failed: userprofiles_rolesmask.user_id, userprofiles_rolesmask.sport_id'):
            SportRegistrationFactory(user=user, sport=sport)

    def test_get_related_role_objects_all_roles(self):
        user = UserFactory(email='testing@example.com')
        sport = SportFactory(name='Ice Hockey')
        league = LeagueFactory(full_name='Long Island Amateur Hockey League', sport=sport)
        division = DivisionFactory(name='Midget Minor AA', league=league)
        team = TeamFactory(name='Green Machine Icecats', division=division)
        sr = SportRegistrationFactory(user=user, sport=sport)
        sr.set_roles(SportRegistration.ROLES)
        manager = ManagerFactory(user=user, team=team)
        player = HockeyPlayerFactory(user=user, team=team, sport=sport)
        coach = CoachFactory(user=user, team=team)
        referee = RefereeFactory(user=user, league=league)
        result = sr.get_related_role_objects()
        self.assertDictEqual({'Player': player, 'Coach': coach, 'Manager': manager, 'Referee': referee}, result)

    def test_get_related_role_objects_3_roles(self):
        user = UserFactory(email='testing@example.com')
        sport = SportFactory(name='Ice Hockey')
        league = LeagueFactory(full_name='Long Island Amateur Hockey League', sport=sport)
        division = DivisionFactory(name='Midget Minor AA', league=league)
        team = TeamFactory(name='Green Machine Icecats', division=division)
        sr = SportRegistrationFactory(user=user, sport=sport)
        sr.set_roles(['Player', 'Coach', 'Referee'])
        player = HockeyPlayerFactory(user=user, team=team, sport=sport)
        coach = CoachFactory(user=user, team=team)
        referee = RefereeFactory(user=user, league=league)
        result = sr.get_related_role_objects()
        self.assertDictEqual({'Player': player, 'Coach': coach, 'Referee': referee}, result)

    def test_get_related_role_objects_2_roles(self):
        user = UserFactory(email='testing@example.com')
        sport = SportFactory(name='Ice Hockey')
        league = LeagueFactory(full_name='Long Island Amateur Hockey League', sport=sport)
        division = DivisionFactory(name='Midget Minor AA', league=league)
        team = TeamFactory(name='Green Machine Icecats', division=division)
        sr = SportRegistrationFactory(user=user, sport=sport)
        sr.set_roles(['Player', 'Coach'])
        player = HockeyPlayerFactory(user=user, team=team, sport=sport)
        coach = CoachFactory(user=user, team=team)
        result = sr.get_related_role_objects()
        self.assertDictEqual({'Player': player, 'Coach': coach}, result)

    def test_get_related_role_objects_1_role(self):
        user = UserFactory(email='testing@example.com')
        sport = SportFactory(name='Ice Hockey')
        league = LeagueFactory(full_name='Long Island Amateur Hockey League', sport=sport)
        division = DivisionFactory(name='Midget Minor AA', league=league)
        team = TeamFactory(name='Green Machine Icecats', division=division)
        sr = SportRegistrationFactory(user=user, sport=sport)
        sr.set_roles(['Manager'])
        manager = ManagerFactory(user=user, team=team)
        result = sr.get_related_role_objects()
        self.assertDictEqual({'Manager': manager}, result)

    def test_get_related_role_objects_no_roles(self):
        user = UserFactory(email='testing@example.com')
        sport = SportFactory(name='Ice Hockey')
        sr = SportRegistrationFactory(user=user, sport=sport)
        sr.set_roles([])
        result = sr.get_related_role_objects()
        self.assertDictEqual({}, result)
