from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views import generic

from ayrabo.utils.mixins import HandleSportNotConfiguredMixin, HasPermissionMixin
from seasons.mappings import get_season_roster_create_update_form_cls, get_season_roster_model_cls
from teams.models import Team
from teams.utils import get_team_detail_view_context
from users.authorizers import SeasonRosterAuthorizer


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
            Team.objects.select_related('division__league__sport', 'organization'),
            pk=self.kwargs.get('team_pk')
        )
        self.sport = self.team.division.league.sport
        return self.team

    def has_permission_func(self):
        season_roster_authorizer = SeasonRosterAuthorizer(user=self.request.user)
        team = self._get_team()
        return season_roster_authorizer.can_user_create(team=team, sport=self.sport)

    def get_form_class(self):
        return get_season_roster_create_update_form_cls(self.sport)

    def get_form_kwargs(self):
        form_kwargs = super().get_form_kwargs()
        instance = self.get_form_class().Meta.model(team=self.team, created_by=self.request.user)

        form_kwargs['team'] = self.team
        form_kwargs['instance'] = instance
        return form_kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'team': self.team,
            'active_tab': 'season_rosters'
        })
        context.update(get_team_detail_view_context(self.team))
        return context

    def get_success_url(self):
        return reverse('teams:season_rosters:list', kwargs={'team_pk': self.team.pk})

    def get(self, request, *args, **kwargs):
        self._get_team()
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self._get_team()
        return super().post(request, *args, **kwargs)


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
            Team.objects.select_related('division__league__sport', 'organization'),
            pk=self.kwargs.get('team_pk')
        )
        self.sport = self.team.division.league.sport
        return self.team

    def has_permission_func(self):
        season_roster_authorizer = SeasonRosterAuthorizer(user=self.request.user)
        team = self._get_team()
        return season_roster_authorizer.can_user_update(team=team, sport=self.sport)

    def get_form_class(self):
        return get_season_roster_create_update_form_cls(self.sport)

    def get_form_kwargs(self):
        form_kwargs = super().get_form_kwargs()
        disable = ['season']
        if not self.object.can_update():
            disable = '__all__'
        form_kwargs.update({'disable': disable})
        return form_kwargs

    def get_object(self, queryset=None):
        model_cls = get_season_roster_model_cls(self.sport)
        pk = self.kwargs.get(self.pk_url_kwarg, None)
        qs = model_cls.objects.filter(team=self.team).select_related('season', 'team')
        return get_object_or_404(qs, pk=pk)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'team': self.team,
            'active_tab': 'season_rosters'
        })
        context.update(get_team_detail_view_context(self.team))
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
