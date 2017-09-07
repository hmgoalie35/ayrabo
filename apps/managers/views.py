from common.views import BaseCreateRelatedObjectsView
from managers.forms import ManagerForm, ManagerModelFormSet
from managers.formset_helpers import ManagerFormSetHelper
from managers.models import Manager


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
