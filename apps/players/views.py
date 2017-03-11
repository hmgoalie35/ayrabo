from common.views import BaseCreateRelatedObjectsView
from .forms import HockeyPlayerForm, BaseballPlayerForm, BasketballPlayerForm, PlayerModelFormSet
from .formset_helpers import HockeyPlayerFormSetHelper, BaseballPlayerFormSetHelper
from .models import HockeyPlayer, BasketballPlayer, BaseballPlayer

SPORT_PLAYER_FORM_MAPPINGS = {
    'Ice Hockey': HockeyPlayerForm,
    'Baseball': BaseballPlayerForm,
    'Basketball': BasketballPlayerForm
}

SPORT_PLAYER_MODEL_MAPPINGS = {
    'Ice Hockey': HockeyPlayer,
    'Basketball': BasketballPlayer,
    'Baseball': BaseballPlayer
}

SPORT_PLAYER_FORMSET_HELPER_MAPPINGS = {
    'Ice Hockey': HockeyPlayerFormSetHelper,
    'Basketball': BasketballPlayer,
    'Baseball': BaseballPlayerFormSetHelper
}


class CreatePlayersView(BaseCreateRelatedObjectsView):
    def get_formset_prefix(self):
        return 'players'

    def get_model_class(self, sport_name):
        return SPORT_PLAYER_MODEL_MAPPINGS.get(sport_name)

    def get_form_class(self, sport_name):
        return SPORT_PLAYER_FORM_MAPPINGS.get(sport_name)

    def get_formset_class(self, sport_name):
        return PlayerModelFormSet

    def get_formset_helper_class(self, sport_name):
        return SPORT_PLAYER_FORMSET_HELPER_MAPPINGS.get(sport_name)

    def get_template_name(self):
        return 'players/players_create.html'

    def get_form_kwargs(self, **kwargs):
        sport_registration = kwargs.get('sport_registration')
        return {
            'sport': sport_registration.sport
        }

    def get_role(self):
        return 'Player'
