from api.v1.common.views import BaseDeactivateApiView
from referees.models import Referee


class DeactivateRefereeApiView(BaseDeactivateApiView):
    def get_role(self):
        return 'referee'

    def get_model(self, sport_name):
        return Referee

    def get_url_lookup_kwarg(self):
        return 'referee_pk'
