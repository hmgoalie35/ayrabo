from django.urls import reverse

from ayrabo.utils.testing import BaseTestCase
from ayrabo.utils.urls import url_with_query_string
from coaches.models import Coach
from coaches.tests import CoachFactory
from common.tests import WaffleSwitchFactory
from divisions.tests import DivisionFactory
from leagues.tests import LeagueFactory
from sports.models import SportRegistration
from sports.tests import SportFactory, SportRegistrationFactory
from teams.tests import TeamFactory
from users.tests import UserFactory


class CoachesUpdateViewTests(BaseTestCase):
    url = 'sports:coaches:update'

    def setUp(self):
        self.coach_update_switch = WaffleSwitchFactory(name='coach_update', active=True)
        self.ice_hockey = SportFactory(name='Ice Hockey')
        self.email = 'user@ayrabo.com'
        self.password = 'myweakpassword'
        self.user = UserFactory(email=self.email, password=self.password)
        self.league = LeagueFactory(name='Long Island Amateur Hockey League', sport=self.ice_hockey)
        self.division = DivisionFactory(name='Midget Minor AA', league=self.league)
        self.team = TeamFactory(name='Green Machine IceCats', division=self.division)
        SportRegistrationFactory(user=self.user, sport=self.ice_hockey, role=SportRegistration.COACH)

        self.post_data = {
            'position': Coach.HEAD_COACH
        }
        self.coach = CoachFactory(user=self.user, team=self.team, **self.post_data)
        self.coach_url = self.format_url(slug='ice-hockey', coach_pk=self.coach.pk)

        self.login(user=self.user)

    # General
    def test_login_required(self):
        self.client.logout()
        self.assertLoginRequired(self.coach_url)

    def test_sport_dne(self):
        response = self.client.get(self.format_url(slug='non-existent', coach_pk=self.coach.pk))
        self.assert_404(response)

    def test_coach_dne(self):
        response = self.client.get(self.format_url(slug='ice-hockey', coach_pk=99))
        self.assert_404(response)

    def test_has_permission_false(self):
        self.client.logout()
        user = UserFactory(password=self.password)
        self.login(user=user)
        response = self.client.get(self.coach_url)
        self.assert_404(response)

    def test_switch_inactive(self):
        self.coach_update_switch.active = False
        self.coach_update_switch.save()
        response = self.client.get(self.coach_url)
        self.assert_404(response)

    # GET
    def test_get(self):
        response = self.client.get(self.coach_url)
        context = response.context

        self.assert_200(response)
        self.assertTemplateUsed(response, 'coaches/coaches_update.html')
        self.assertEqual(context['coach'].pk, self.coach.pk)

    # POST
    def test_post(self):
        self.post_data.update({'position': Coach.ASSISTANT_COACH})
        response = self.client.post(self.coach_url, data=self.post_data, follow=True)
        self.assertHasMessage(response, 'Your coach information has been updated.')
        self.coach.refresh_from_db()
        self.assertEqual(self.coach.position, Coach.ASSISTANT_COACH)
        url = url_with_query_string(reverse('sports:dashboard', kwargs={'slug': self.ice_hockey.slug}), tab='coach')
        self.assertRedirects(response, url)

    def test_post_nothing_changed(self):
        response = self.client.post(self.coach_url, data=self.post_data, follow=True)
        self.assertNoMessage(response, 'Your coach information has been updated.')
        self.coach.refresh_from_db()
        self.assertEqual(self.coach.position, Coach.HEAD_COACH)
        url = url_with_query_string(reverse('sports:dashboard', kwargs={'slug': self.ice_hockey.slug}), tab='coach')
        self.assertRedirects(response, url)

    def test_post_invalid(self):
        self.post_data.update({'position': ''})
        response = self.client.post(self.coach_url, data=self.post_data, follow=True)
        self.assertFormError(response, 'form', 'position', 'This field is required.')
        self.assertTemplateUsed('coaches/coaches_update.html')
