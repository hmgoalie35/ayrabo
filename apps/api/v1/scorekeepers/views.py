from api.v1.common.views import BaseDeactivateApiView
from scorekeepers.models import Scorekeeper


class DeactivateScorekeeperApiView(BaseDeactivateApiView):
    def get_role(self):
        return 'scorekeeper'

    def get_model(self, sport_name):
        return Scorekeeper

    def get_url_lookup_kwarg(self):
        return 'scorekeeper_pk'
