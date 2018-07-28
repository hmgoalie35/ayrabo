from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import generic

from ayrabo.utils.exceptions import SportNotConfiguredException
from ayrabo.utils.mappings import SPORT_PLAYER_MODEL_MAPPINGS
from ayrabo.utils.mixins import HandleSportNotConfiguredMixin, HasPermissionMixin, WaffleSwitchMixin
from sports.models import Sport
from . import forms

SPORT_UPDATE_PLAYER_FORM_MAPPINGS = {
    'Ice Hockey': forms.HockeyPlayerUpdateForm,
    'Baseball': forms.BaseballPlayerUpdateForm,
    'Basketball': forms.BasketballPlayerUpdateForm
}


class PlayerUpdateView(LoginRequiredMixin,
                       WaffleSwitchMixin,
                       HandleSportNotConfiguredMixin,
                       HasPermissionMixin,
                       SuccessMessageMixin,
                       generic.UpdateView):
    template_name = 'players/players_update.html'
    pk_url_kwarg = 'player_pk'
    context_object_name = 'player'
    success_message = 'Your player information has been updated.'
    success_url = reverse_lazy('home')
    waffle_identifier = 'player_update'

    def _get_sport(self):
        if hasattr(self, 'sport'):
            return self.sport
        self.sport = get_object_or_404(Sport, slug=self.kwargs.get('slug'))
        return self.sport

    def has_permission_func(self):
        user = self.request.user
        player = self.get_object()
        return user.id == player.user_id

    def get_object(self, queryset=None):
        sport = self._get_sport()
        model_cls = SPORT_PLAYER_MODEL_MAPPINGS.get(sport.name)
        if model_cls is None:
            raise SportNotConfiguredException(sport)
        pk = self.kwargs.get(self.pk_url_kwarg, None)
        return get_object_or_404(model_cls.objects.select_related('team'), pk=pk)

    def get_form_class(self):
        sport = self._get_sport()
        form_cls = SPORT_UPDATE_PLAYER_FORM_MAPPINGS.get(sport.name)
        if form_cls is None:
            raise SportNotConfiguredException(self.sport)
        return form_cls

    def form_valid(self, form):
        if form.has_changed():
            return super().form_valid(form)
        return redirect(self.get_success_url())

    def get(self, request, *args, **kwargs):
        self._get_sport()
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self._get_sport()
        return super().post(request, *args, **kwargs)
