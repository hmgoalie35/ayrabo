from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import Http404, get_object_or_404, redirect, render
from django.views import generic
from django.views.generic import base

from ayrabo.utils.mappings import SPORT_PLAYER_MODEL_MAPPINGS
from sports.models import SportRegistration
from . import forms
from .formset_helpers import BaseballPlayerFormSetHelper, HockeyPlayerFormSetHelper

SPORT_CREATE_PLAYER_FORM_MAPPINGS = {
    'Ice Hockey': forms.HockeyPlayerForm,
    'Baseball': forms.BaseballPlayerForm,
    'Basketball': forms.BasketballPlayerForm
}

SPORT_UPDATE_PLAYER_FORM_MAPPINGS = {
    'Ice Hockey': forms.HockeyPlayerUpdateForm,
    'Baseball': forms.BaseballPlayerUpdateForm,
    'Basketball': forms.BasketballPlayerUpdateForm
}

SPORT_PLAYER_FORMSET_HELPER_MAPPINGS = {
    'Ice Hockey': HockeyPlayerFormSetHelper,
    'Basketball': None,
    'Baseball': BaseballPlayerFormSetHelper
}


# NOTE: I am currently omitting checks for improperly configured sports because I don't
# think it's possible to even get to this page.
class PlayerUpdateView(LoginRequiredMixin, base.ContextMixin, generic.View):
    template_name = 'players/players_update.html'

    def _get_sport_registration(self):
        return get_object_or_404(SportRegistration.objects.select_related('sport'), pk=self.kwargs.get('pk'))

    def _get_player(self, sport_name):
        model_cls = SPORT_PLAYER_MODEL_MAPPINGS.get(sport_name)
        return get_object_or_404(model_cls.objects.select_related('team'), pk=self.kwargs.get('player_pk'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        sport_registration = self._get_sport_registration()
        sport_name = sport_registration.sport.name
        player = self._get_player(sport_name)

        user_id = self.request.user.id
        if user_id != sport_registration.user_id or user_id != player.user_id:
            raise Http404

        context['player'] = player
        context['sport_registration'] = sport_registration
        form_cls = SPORT_UPDATE_PLAYER_FORM_MAPPINGS.get(sport_name)
        context['form'] = form_cls(self.request.POST or None, instance=player)
        return context

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, self.get_context_data(**kwargs))

    def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        sr = context.get('sport_registration')
        form = context.get('form')
        if form.is_valid():
            if form.has_changed():
                form.save()
                messages.success(request, 'Your player information has been updated.')
            return redirect(sr.get_absolute_url())
        return render(request, self.template_name, context)
