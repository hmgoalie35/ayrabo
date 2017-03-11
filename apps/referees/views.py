from common.views import BaseCreateRelatedObjectsView
from referees.forms import RefereeForm, RefereeModelFormSet
from referees.formset_helpers import RefereeFormSetHelper
from referees.models import Referee


class CreateRefereesView(BaseCreateRelatedObjectsView):
    def get_formset_prefix(self):
        return 'referees'

    def get_model_class(self, sport_name):
        return Referee

    def get_form_class(self, sport_name):
        return RefereeForm

    def get_formset_class(self, sport_name):
        return RefereeModelFormSet

    def get_formset_helper_class(self, sport_name):
        return RefereeFormSetHelper

    def get_template_name(self):
        return 'referees/referees_create.html'

    def get_role(self):
        return 'Referee'
