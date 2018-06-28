from ayrabo.utils.testing import BaseTestCase
from coaches.tests import CoachFactory
from divisions.tests import DivisionFactory
from leagues.tests import LeagueFactory
from sports.tests import SportFactory, SportRegistrationFactory
from teams.tests import TeamFactory
from users.tests import UserFactory


class CoachesUpdateViewTests(BaseTestCase):
    url = 'sportregistrations:coaches:update'

    @classmethod
    def setUpTestData(cls):
        cls.ice_hockey = SportFactory(name='Ice Hockey')
        cls.email = 'user@ayrabo.com'
        cls.password = 'myweakpassword'
        cls.user = UserFactory(email=cls.email, password=cls.password)
        cls.league = LeagueFactory(full_name='Long Island Amateur Hockey League', sport=cls.ice_hockey)
        cls.division = DivisionFactory(name='Midget Minor AA', league=cls.league)
        cls.team = TeamFactory(name='Green Machine IceCats', division=cls.division)

        cls.sr = SportRegistrationFactory(user=cls.user, sport=cls.ice_hockey, is_complete=True)
        cls.sr.set_roles(['Coach'])

    def setUp(self):
        self.post_data = {
            'position': 'head_coach'
        }
        self.coach = CoachFactory(user=self.user, team=self.team, **self.post_data)
        self.coach_url = self.format_url(pk=self.sr.pk, coach_pk=self.coach.pk)

        self.client.login(email=self.email, password=self.password)

    # General
    def test_login_required(self):
        self.client.logout()
        response = self.client.get(self.coach_url)
        self.assertRedirects(response, self.get_login_required_url(self.coach_url))

    # GET
    def test_get(self):
        response = self.client.get(self.coach_url)
        context = response.context

        self.assert_200(response)
        self.assertTemplateUsed(response, 'coaches/coaches_update.html')
        self.assertIsNotNone(context['coach'])
        self.assertIsNotNone(context['sport_registration'])
        self.assertIsNotNone(context['form'])

    def test_get_sport_reg_dne(self):
        response = self.client.get(self.format_url(pk=99, coach_pk=self.coach.pk))
        self.assertEqual(response.status_code, 404)

    def test_get_coach_obj_dne(self):
        response = self.client.get(self.format_url(pk=self.sr.pk, coach_pk=99))
        self.assertEqual(response.status_code, 404)

    def test_get_not_obj_owner(self):
        self.client.logout()
        user = UserFactory(password=self.password)
        SportRegistrationFactory(user=user, sport=self.ice_hockey)
        self.client.login(email=user.email, password=self.password)
        response = self.client.get(self.coach_url)
        self.assertEqual(response.status_code, 404)

    # POST
    def test_post(self):
        self.post_data.update({'position': 'assistant_coach'})
        response = self.client.post(self.coach_url, data=self.post_data, follow=True)
        self.assertHasMessage(response, 'Your coach information has been updated.')
        self.coach.refresh_from_db()
        self.assertEqual(self.coach.position, 'assistant_coach')
        self.assertRedirects(response, self.sr.get_absolute_url())

    def test_post_nothing_changed(self):
        response = self.client.post(self.coach_url, data=self.post_data, follow=True)
        self.assertNoMessage(response, 'Your coach information has been updated.')
        self.coach.refresh_from_db()
        self.assertEqual(self.coach.position, 'head_coach')
        self.assertRedirects(response, self.sr.get_absolute_url())

    def test_post_invalid(self):
        self.post_data.update({'position': ''})
        response = self.client.post(self.coach_url, data=self.post_data, follow=True)
        self.assertFormError(response, 'form', 'position', 'This field is required.')
        self.assertTemplateUsed('coaches/coaches_update.html')
