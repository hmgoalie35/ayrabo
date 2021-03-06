from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views import generic

from ayrabo.utils.exceptions import SportNotConfiguredException
from ayrabo.utils.mixins import HandleSportNotConfiguredMixin, HasPermissionMixin, WaffleSwitchMixin
from ayrabo.utils.urls import url_with_query_string
from players.mappings import get_player_model_cls
from sports.models import Sport, SportRegistration
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
    waffle_identifier = 'player_update'

    def get_success_url(self):
        return url_with_query_string(reverse('sports:dashboard', kwargs={'slug': self.sport.slug}),
                                     tab=SportRegistration.PLAYER)

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
        model_cls = get_player_model_cls(sport)
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
