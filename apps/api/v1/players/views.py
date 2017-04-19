from api.v1.common.views import BaseDeactivateApiView
from escoresheet.utils.mappings import SPORT_PLAYER_MODEL_MAPPINGS


class DeactivatePlayerApiView(BaseDeactivateApiView):
    def get_role(self):
        return 'player'

    def get_model(self, sport_name):
        return SPORT_PLAYER_MODEL_MAPPINGS.get(sport_name, None)

    def get_url_lookup_kwarg(self):
        return 'player_pk'
