from common.views import BaseCreateRelatedObjectsView

from .forms import CoachForm, CoachModelFormSet
from .formset_helpers import CoachFormSetHelper
from .models import Coach


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

    def get_form_kwargs(self, **kwargs):
        sport_registration = kwargs.get('sport_registration')
        return {
            'sport': sport_registration.sport
        }

    def get_role(self):
        return 'Coach'
