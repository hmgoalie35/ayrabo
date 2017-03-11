from django.core import mail
from django.urls import reverse

from accounts.tests import UserFactory
from divisions.tests import DivisionFactory
from escoresheet.utils.testing_utils import BaseTestCase
from leagues.tests import LeagueFactory
from players.forms import HockeyPlayerForm
from players.formset_helpers import HockeyPlayerFormSetHelper
from players.models import HockeyPlayer
from sports.tests import SportFactory, SportRegistrationFactory
from teams.tests import TeamFactory


class CreatePlayersViewTests(BaseTestCase):
    def _format_url(self, role, **kwargs):
        return reverse(self.url.format(role=role), kwargs=kwargs)

    @classmethod
    def setUpClass(cls):
        super(CreatePlayersViewTests, cls).setUpClass()
        cls.ice_hockey = SportFactory(name='Ice Hockey')
        cls.baseball = SportFactory(name='Baseball')
        cls.basketball = SportFactory(name='Basketball')

    def setUp(self):
        self.url = 'sportregistrations:{role}:create'
        self.email = 'user@example.com'
        self.password = 'myweakpassword'
        self.post_data = {
            'players-TOTAL_FORMS': 1,
            'players-INITIAL_FORMS': 0,
            'players-MIN_NUM_FORMS': 1,
            'players-MAX_NUM_FORMS': 10
        }

        self.user = UserFactory(email=self.email, password=self.password)

        self.league = LeagueFactory(full_name='Long Island Amateur Hockey League', sport=self.ice_hockey)
        self.division = DivisionFactory(name='Midget Minor AA', league=self.league)
        self.team = TeamFactory(name='Green Machine IceCats', division=self.division)

        self.sr = SportRegistrationFactory(user=self.user, sport=self.ice_hockey, is_complete=False)
        self.sr_2 = SportRegistrationFactory(user=self.user, sport=self.baseball, is_complete=False)
        self.sr.set_roles(['Player', 'Coach'])
        self.client.login(email=self.email, password=self.password)

    def test_get_template_name(self):
        response = self.client.get(self._format_url('players', pk=self.sr.id))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'players/players_create.html')

    def test_get_form_class(self):
        response = self.client.get(self._format_url('players', pk=self.sr.id))
        form_cls = response.context['formset'].forms[0]
        self.assertIsInstance(form_cls, HockeyPlayerForm)

    def test_get_formset_prefix(self):
        response = self.client.get(self._format_url('players', pk=self.sr.id))
        formset = response.context['formset']
        self.assertEqual(formset.prefix, 'players')

    def test_get_model_class(self):
        response = self.client.get(self._format_url('players', pk=self.sr.id))
        self.assertIs(response.context['formset'].model, HockeyPlayer)

    def test_get_formset_helper_class(self):
        response = self.client.get(self._format_url('players', pk=self.sr.id))
        self.assertIs(response.context['helper'], HockeyPlayerFormSetHelper)

    def test_get_role(self):
        response = self.client.get(self._format_url('players', pk=self.sr.id))
        self.assertEqual(response.context['role'], 'Player')

    # GET
    def test_get_sport_not_configured(self):
        self.sr.is_complete = True
        self.sr.save()
        self.sr_2.is_complete = True
        self.sr_2.save()
        sr = SportRegistrationFactory(user=self.user, is_complete=False)
        sr.set_roles(['Player'])
        response = self.client.get(self._format_url('players', pk=sr.id), follow=True)
        self.assertTemplateUsed(response, 'sport_not_configured_msg.html')
        msg = "{sport} hasn't been configured correctly in our system. " \
              "If you believe this is an error please contact us.".format(sport=sr.sport.name)
        self.assertEqual(response.context['message'], msg)
        self.assertEqual(len(mail.outbox), 1)
