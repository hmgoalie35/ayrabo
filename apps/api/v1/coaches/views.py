from api.v1.common.views import BaseDeactivateApiView
from coaches.models import Coach


class DeactivateCoachApiView(BaseDeactivateApiView):
    def get_role(self):
        return 'coach'

    def get_model(self, sport_name):
        return Coach

    def get_url_lookup_kwarg(self):
        return 'coach_pk'
