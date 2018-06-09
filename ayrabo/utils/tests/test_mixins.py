from django.test import RequestFactory
from django.views import generic

from ayrabo.utils.mixins import PreSelectedTabMixin
from ayrabo.utils.testing import BaseTestCase


class DummyView(PreSelectedTabMixin, generic.TemplateView):
    template_name = ''


class PreSelectedTabMixinTests(BaseTestCase):

    def _run_view(self, view, request):
        return view.as_view()(request)

    def setUp(self):
        self.factory = RequestFactory()

    def test_valid_tabs_is_list(self):
        request = self.factory.get('/')
        view = DummyView
        view.valid_tabs = 'string'
        with self.assertRaisesMessage(AssertionError, 'valid_tabs must be a non-empty list'):
            self._run_view(view, request)

    def test_valid_tabs_non_empty_list(self):
        request = self.factory.get('/')
        view = DummyView
        view.valid_tabs = []
        with self.assertRaisesMessage(AssertionError, 'valid_tabs must be a non-empty list'):
            self._run_view(view, request)

    def test_default_tab_is_string(self):
        request = self.factory.get('/')
        view = DummyView
        view.valid_tabs = ['tab-1', 'tab-2']
        view.default_tab = []
        with self.assertRaisesMessage(AssertionError, 'default_tab must be a non-empty string'):
            self._run_view(view, request)

    def test_default_tab_non_empty_string(self):
        request = self.factory.get('/')
        view = DummyView
        view.valid_tabs = ['tab-1', 'tab-2']
        view.default_tab = ''
        with self.assertRaisesMessage(AssertionError, 'default_tab must be a non-empty string'):
            self._run_view(view, request)

    def test_default_tab_in_valid_tabs(self):
        request = self.factory.get('/')
        view = DummyView
        view.valid_tabs = ['tab-1', 'tab-2']
        view.default_tab = 'tab-3'
        with self.assertRaisesMessage(AssertionError, 'tab-3 is not a valid choice, choose from tab-1, tab-2'):
            self._run_view(view, request)

    def test_tab_from_query_param_selected(self):
        request = self.factory.get('/', {'tab': 'tab-3'})
        view = DummyView
        view.valid_tabs = ['tab-1', 'tab-2', 'tab-3']
        view.default_tab = 'tab-1'
        response = self._run_view(view, request)
        self.assertEqual(response.context_data.get('active_tab'), 'tab-3')

    def test_default_tab_selected(self):
        request = self.factory.get('/', {'tab': 'tab-invalid'})
        view = DummyView
        view.valid_tabs = ['tab-1', 'tab-2', 'tab-3']
        view.default_tab = 'tab-1'
        response = self._run_view(view, request)
        self.assertEqual(response.context_data.get('active_tab'), 'tab-1')
