from coaches.forms import CoachForm, CoachModelFormSet
from coaches.formset_helpers import CoachFormSetHelper
from coaches.models import Coach
from common.views import BaseCreateRelatedObjectsView


class CreateCoachesView(BaseCreateRelatedObjectsView):
    def get_formset_prefix(self):
        return 'coaches'

    def get_model_class(self, sport_name):
        return Coach

    def get_form_class(self, sport_name):
        return CoachForm

    def get_formset_class(self, sport_name):
        return CoachModelFormSet

    def get_formset_helper_class(self, sport_name):
        return CoachFormSetHelper

    def get_template_name(self):
        return 'coaches/coaches_create.html'

    def get_role(self):
        return 'Coach'
