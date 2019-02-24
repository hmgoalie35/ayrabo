from unittest.mock import Mock

from django.test import RequestFactory
from django.urls import reverse

from ayrabo.utils.testing import BaseTestCase
from users.tests import UserFactory
from users.utils import get_user_detail_view_context


class UtilsTests(BaseTestCase):
    def setUp(self):
        self.user = UserFactory()
        self.factory = RequestFactory()
        self.change_password_url = reverse('account_change_password')

    def test_get_user_detail_view_context_dynamic_tabs(self):
        request = self.factory.get(reverse('users:detail', kwargs={'pk': self.user.pk}))
        request.user = self.user
        request.resolver_match = Mock()
        request.resolver_match.view_name = 'users:detail'

        context = get_user_detail_view_context(request, request.user, include_user_obj=False)
        self.assertDictEqual(context, {
            'info_tab_key': 'information',
            'sports_tab_key': 'sports',
            'change_password_tab_key': 'change-password',
            'info_tab_link': 'information',
            'sports_tab_link': 'sports',
            'change_password_link': self.change_password_url,
            'dynamic': True
        })

    def test_get_user_detail_view_context_static_tabs(self):
        request = self.factory.get(self.change_password_url)
        request.user = self.user
        request.resolver_match = Mock()
        request.resolver_match.view_name = 'account_change_password'
        user_detail_url = reverse('users:detail', kwargs={'pk': self.user.pk})

        context = get_user_detail_view_context(request, request.user, include_user_obj=True)
        self.assertDictEqual(context, {
            'info_tab_key': 'information',
            'sports_tab_key': 'sports',
            'change_password_tab_key': 'change-password',
            'info_tab_link': f'{user_detail_url}?tab=information',
            'sports_tab_link': f'{user_detail_url}?tab=sports',
            'change_password_link': self.change_password_url,
            'dynamic': False,
            'user_obj': self.user
        })
