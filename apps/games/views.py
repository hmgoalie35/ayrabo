from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import get_object_or_404, reverse
from django.views import generic

from escoresheet.utils.mixins import HasPermissionMixin
from games.forms import HockeyGameCreateForm
from games.models import HockeyGame
from managers.models import Manager
from teams.models import Team


class HockeyGameCreateView(LoginRequiredMixin,
                           HasPermissionMixin,
                           SuccessMessageMixin,
                           generic.CreateView):
    template_name = 'games/hockey_game_create.html'
    model = HockeyGame
    form_class = HockeyGameCreateForm
    success_message = 'Your game has been created.'

    def has_permission_func(self):
        user = self.request.user
        team = self._get_team()
        return Manager.objects.active().filter(user=user, team=team).exists()

    def get_success_url(self):
        return self._get_sport_registration_url()

    def _get_sport_registration_url(self):
        sport_registration = self.request.user.sportregistration_set.get(sport_id=self.team.division.league.sport_id)
        return reverse('sportregistrations:detail', kwargs={'pk': sport_registration.id})

    def _get_team(self):
        if hasattr(self, 'team'):
            return self.team
        self.team = get_object_or_404(
            Team.objects.select_related('division', 'division__league', 'division__league__sport'),
            pk=self.kwargs.get('team_pk', None)
        )
        return self.team

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['team'] = self._get_team()
        context['sport_registration_url'] = self._get_sport_registration_url()
        return context

    def get_form_kwargs(self):
        form_kwargs = super().get_form_kwargs()
        form_kwargs['team'] = self._get_team()
        return form_kwargs
