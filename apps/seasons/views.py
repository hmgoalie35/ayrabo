from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views import generic

from ayrabo.utils.exceptions import SportNotConfiguredException
from ayrabo.utils.mixins import HasPermissionMixin, HandleSportNotConfiguredMixin
from managers.models import Manager
from sports.models import SportRegistration
from teams.models import Team
from .forms import HockeySeasonRosterCreateUpdateForm
from .models import HockeySeasonRoster

SPORT_FORM_MAPPINGS = {
    'Ice Hockey': HockeySeasonRosterCreateUpdateForm
}

SPORT_MODEL_MAPPINGS = {
    'Ice Hockey': HockeySeasonRoster
}


class SeasonRosterCreateView(LoginRequiredMixin,
                             HandleSportNotConfiguredMixin,
                             HasPermissionMixin,
                             SuccessMessageMixin,
                             generic.CreateView):
    template_name = 'seasons/season_roster_create.html'
    success_message = 'Your season roster has been created.'

    def _get_team(self):
        if hasattr(self, 'team'):
            return self.team
        self.team = get_object_or_404(
            Team.objects.select_related('division', 'division__league', 'division__league__sport'),
            pk=self.kwargs.get('team_pk')
        )
        self.sport = self.team.division.league.sport
        return self.team

    def has_permission_func(self):
        user = self.request.user
        team = self._get_team()
        return Manager.objects.active().filter(user=user, team=team).exists()

    def get_form_class(self):
        form_cls = SPORT_FORM_MAPPINGS.get(self.sport.name)
        if form_cls is None:
            raise SportNotConfiguredException(self.sport)
        return form_cls

    def get_form_kwargs(self):
        form_kwargs = super().get_form_kwargs()
        instance = self.get_form_class().Meta.model(team=self.team, created_by=self.request.user)

        form_kwargs['team'] = self.team
        form_kwargs['instance'] = instance
        return form_kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['team'] = self.team
        return context

    def get_success_url(self):
        sport_registration = SportRegistration.objects.filter(user=self.request.user, sport=self.sport).first()
        return sport_registration.get_absolute_url() if sport_registration else reverse('home')

    def get(self, request, *args, **kwargs):
        self._get_team()
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self._get_team()
        return super().post(request, *args, **kwargs)


class SeasonRosterListView(LoginRequiredMixin, HandleSportNotConfiguredMixin, HasPermissionMixin, generic.ListView):
    template_name = 'seasons/season_roster_list.html'
    context_object_name = 'season_rosters'

    def _get_team(self):
        if hasattr(self, 'team'):
            return self.team
        self.team = get_object_or_404(
            Team.objects.select_related('division', 'division__league', 'division__league__sport'),
            pk=self.kwargs.get('team_pk')
        )
        self.sport = self.team.division.league.sport
        return self.team

    def _get_players(self, season_roster):
        return season_roster.players.active().order_by('jersey_number').select_related('user')

    def has_permission_func(self):
        user = self.request.user
        team = self._get_team()
        return Manager.objects.active().filter(user=user, team=team).exists()

    def get_queryset(self):
        season_roster_cls = SPORT_MODEL_MAPPINGS.get(self.sport.name)
        if season_roster_cls is None:
            raise SportNotConfiguredException(self.sport)
        # Datatables is ordering by season, desc. It seems to be doing a lexicographical sort so it works, but isn't
        # the best way to sort season rosters.
        return season_roster_cls.objects.filter(team=self.team).select_related(
            'season', 'team', 'team__division', 'created_by')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        season_rosters = context.pop(self.context_object_name)
        context['season_rosters'] = {roster: self._get_players(roster) for roster in season_rosters}
        context['team'] = self.team
        return context

    def get(self, request, *args, **kwargs):
        self._get_team()
        return super().get(request, *args, **kwargs)


class SeasonRosterUpdateView(LoginRequiredMixin,
                             HandleSportNotConfiguredMixin,
                             HasPermissionMixin,
                             SuccessMessageMixin,
                             generic.UpdateView):
    template_name = 'seasons/season_roster_update.html'
    context_object_name = 'season_roster'
    success_message = 'Your season roster has been updated.'

    def _get_team(self):
        if hasattr(self, 'team'):
            return self.team
        self.team = get_object_or_404(
            Team.objects.select_related('division', 'division__league', 'division__league__sport'),
            pk=self.kwargs.get('team_pk')
        )
        self.sport = self.team.division.league.sport
        return self.team

    def has_permission_func(self):
        user = self.request.user
        team = self._get_team()
        season_roster = self.get_object()
        return team.id == season_roster.team_id and Manager.objects.active().filter(user=user, team=team).exists()

    def get_form_class(self):
        form_cls = SPORT_FORM_MAPPINGS.get(self.sport.name)
        if form_cls is None:
            raise SportNotConfiguredException(self.sport)
        return form_cls

    def get_form_kwargs(self):
        form_kwargs = super().get_form_kwargs()
        form_kwargs['disable'] = ['season']
        return form_kwargs

    def get_object(self, queryset=None):
        model_cls = SPORT_MODEL_MAPPINGS.get(self.sport.name)
        if model_cls is None:
            raise SportNotConfiguredException(self.sport)
        pk = self.kwargs.get(self.pk_url_kwarg, None)
        return get_object_or_404(model_cls.objects.select_related('season', 'team'), pk=pk)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['team'] = self.team
        return context

    def form_valid(self, form):
        if form.has_changed():
            return super().form_valid(form)
        return redirect(self.get_success_url())

    def get_success_url(self):
        return reverse('teams:season_rosters:list', kwargs={'team_pk': self.team.pk})

    def get(self, request, *args, **kwargs):
        self._get_team()
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self._get_team()
        return super().post(request, *args, **kwargs)
