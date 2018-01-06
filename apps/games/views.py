from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Q
from django.shortcuts import get_object_or_404, reverse
from django.urls import reverse_lazy
from django.views import generic

from common.views import CsvBulkUploadView
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
        return context

    def get_form_kwargs(self):
        form_kwargs = super().get_form_kwargs()
        form_kwargs['team'] = self._get_team()
        return form_kwargs


class HockeyGameListView(LoginRequiredMixin, generic.ListView):
    template_name = 'games/hockey_game_list.html'
    context_object_name = 'games'
    ordering = ['-season', '-start']
    model = HockeyGame

    def _get_team(self):
        if hasattr(self, 'team'):
            return self.team
        self.team = get_object_or_404(
            Team.objects.select_related('division', 'division__league'),
            pk=self.kwargs.get('team_pk', None)
        )
        return self.team

    def get_queryset(self):
        qs = super().get_queryset()
        team = self._get_team()
        return qs.filter(Q(home_team=team) | Q(away_team=team)).select_related('home_team', 'away_team', 'type',
                                                                               'location', 'season')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        team = self._get_team()
        user = self.request.user
        is_manager_for_team = Manager.objects.active().filter(user=user, team=team).exists()
        context['can_create_game'] = is_manager_for_team
        context['team'] = team
        return context


class BulkUploadHockeyGamesView(CsvBulkUploadView):
    success_url = reverse_lazy('bulk_upload_hockeygames')
    model = HockeyGame
    model_form_class = HockeyGameCreateForm

    def get_model_form_kwargs(self, data, raw_data):
        form_kwargs = super().get_model_form_kwargs(data, raw_data)
        try:
            form_kwargs['team'] = Team.objects.get(pk=raw_data[0].get('home_team'))
        except (Team.DoesNotExist, IndexError):
            pass
        return form_kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['model_cls'] = 'HockeyGame'
        context['url'] = reverse_lazy('admin:games_hockeygame_changelist')
        return context
