from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import generic

from common.views import BaseCreateRelatedObjectsView
from escoresheet.utils.mixins import UserHasRolesMixin
from managers.forms import ManagerForm, ManagerModelFormSet
from managers.formset_helpers import ManagerFormSetHelper
from managers.models import Manager


class ManagerHomeView(LoginRequiredMixin, UserHasRolesMixin, generic.TemplateView):
    template_name = 'managers/manager_home.html'
    roles_to_check = ['Manager']

    def get_context_data(self, **kwargs):
        context = super(ManagerHomeView, self).get_context_data(**kwargs)
        # A user has many manager objects, with each manager object being tied to a team
        manager_objects = Manager.objects.active().filter(user=self.request.user).select_related(
                'team', 'team__division__league__sport')
        context['teams'] = [manager.team for manager in manager_objects]
        return context


class ManagersCreateView(BaseCreateRelatedObjectsView):
    def get_formset_prefix(self):
        return 'managers'

    def get_model_class(self, sport_name):
        return Manager

    def get_form_class(self, sport_name):
        return ManagerForm

    def get_formset_class(self, sport_name):
        return ManagerModelFormSet

    def get_formset_helper_class(self, sport_name):
        return ManagerFormSetHelper

    def get_template_name(self):
        return 'managers/managers_create.html'

    def get_role(self):
        return 'Manager'
