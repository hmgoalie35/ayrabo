from api.v1.common.views import BaseDeactivateApiView
from managers.models import Manager


class DeactivateManagerApiView(BaseDeactivateApiView):
    def get_role(self):
        return 'manager'

    def get_model(self, sport_name):
        return Manager

    def get_url_lookup_kwarg(self):
        return 'manager_pk'
