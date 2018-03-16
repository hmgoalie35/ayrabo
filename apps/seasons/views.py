from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.http import Http404
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.views import generic
from django.views.generic.base import ContextMixin

from ayrabo.utils import handle_sport_not_configured
from ayrabo.utils.exceptions import SportNotConfiguredException
from ayrabo.utils.mixins import UserHasRolesMixin, HasPermissionMixin, HandleSportNotConfiguredMixin
from managers.models import Manager
from sports.models import SportRegistration
from teams.models import Team
from .forms import HockeySeasonRosterCreateForm, HockeySeasonRosterUpdateForm
from .models import HockeySeasonRoster

SPORT_CREATE_FORM_MAPPINGS = {
    'Ice Hockey': HockeySeasonRosterCreateForm
}

SPORT_UPDATE_FORM_MAPPINGS = {
    'Ice Hockey': HockeySeasonRosterUpdateForm
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
        form_cls = SPORT_CREATE_FORM_MAPPINGS.get(self.sport.name)
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


class SeasonRosterListView(LoginRequiredMixin, UserHasRolesMixin, generic.TemplateView):
    roles_to_check = ['Manager']
    template_name = 'seasons/season_roster_list.html'

    def get_context_data(self, **kwargs):
        context = super(SeasonRosterListView, self).get_context_data(**kwargs)

        team = get_object_or_404(Team.objects.select_related('division', 'division__league', 'division__league__sport'),
                                 pk=kwargs.get('team_pk', None))

        # Can also do Manager.objects.filter(user=self.request.user, team=team)
        is_user_manager_for_team = team.manager_set.active().filter(user=self.request.user).exists()
        if not is_user_manager_for_team:
            raise Http404

        sport_name = team.division.league.sport.name
        season_roster_cls = SPORT_MODEL_MAPPINGS.get(sport_name)
        if season_roster_cls is None:
            raise SportNotConfiguredException(sport_name)

        season_rosters = {}
        temp = season_roster_cls.objects.order_by('-created').filter(team=team).select_related(
            'season', 'team', 'team__division')
        for season_roster in temp:
            season_rosters[season_roster] = season_roster.players.active().select_related('user').order_by(
                'jersey_number')
        context['season_rosters'] = season_rosters
        context['team'] = team

        return context

    def get(self, request, *args, **kwargs):
        try:
            self.get_context_data(**kwargs)
        except SportNotConfiguredException as e:
            return handle_sport_not_configured(self.request, self, e)
        return super(SeasonRosterListView, self).get(request, *args, **kwargs)


class SeasonRosterUpdateView(LoginRequiredMixin, UserHasRolesMixin, ContextMixin, generic.View):
    roles_to_check = ['Manager']
    template_name = 'seasons/season_roster_update.html'

    def get_context_data(self, **kwargs):
        context = super(SeasonRosterUpdateView, self).get_context_data(**kwargs)
        team = get_object_or_404(Team.objects.select_related('division', 'division__league', 'division__league__sport'),
                                 pk=kwargs.get('team_pk', None))

        is_user_manager_for_team = team.manager_set.active().filter(user=self.request.user).exists()
        if not is_user_manager_for_team:
            raise Http404

        sport_name = team.division.league.sport.name

        season_roster_cls = SPORT_MODEL_MAPPINGS.get(sport_name)
        if season_roster_cls is None:
            raise SportNotConfiguredException(sport_name)

        season_roster = get_object_or_404(season_roster_cls.objects.select_related('season'), pk=kwargs.get('pk', None))

        if season_roster.team_id != team.id:
            raise Http404

        form_cls = SPORT_UPDATE_FORM_MAPPINGS.get(sport_name)
        if form_cls is None:
            raise SportNotConfiguredException(sport_name)

        form = form_cls(self.request.POST or None, instance=season_roster, team=team)

        context['season_roster'] = season_roster
        context['sport_name'] = sport_name
        context['team'] = team
        context['form'] = form

        return context

    def get(self, request, *args, **kwargs):
        try:
            context = self.get_context_data(**kwargs)
        except SportNotConfiguredException as e:
            return handle_sport_not_configured(self.request, self, e)
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        try:
            context = self.get_context_data(**kwargs)
        except SportNotConfiguredException as e:
            return handle_sport_not_configured(self.request, self, e)
        team = context.get('team')
        form = context.get('form')
        if form.is_valid():
            if form.has_changed():
                form.save()
                messages.success(
                    request, 'Season roster for {team} successfully updated.'.format(team=team))
            return redirect(reverse('teams:season_rosters:list', kwargs={'team_pk': team.pk}))

        return render(request, self.template_name, context)
