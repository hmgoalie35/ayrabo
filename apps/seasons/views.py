from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.urlresolvers import reverse
from django.http import Http404
from django.shortcuts import render, get_object_or_404, redirect
from django.views import generic
from django.views.generic.base import ContextMixin

from managers.models import Manager
from teams.models import Team
from .forms import CreateHockeySeasonRosterForm, UpdateHockeySeasonRosterForm
from .mixins import UserHasRolesMixin
from .models import HockeySeasonRoster

SPORT_CREATE_FORM_MAPPINGS = {
    'Ice Hockey': CreateHockeySeasonRosterForm
}

SPORT_UPDATE_FORM_MAPPINGS = {
    'Ice Hockey': UpdateHockeySeasonRosterForm
}

SPORT_MODEL_MAPPINGS = {
    'Ice Hockey': HockeySeasonRoster
}


class CreateSeasonRosterView(LoginRequiredMixin, UserHasRolesMixin, ContextMixin, generic.View):
    template_name = 'seasons/create_season_roster.html'
    roles_to_check = ['Manager']
    user_has_no_role_msg = 'You do not have permission to perform this action.'

    def get_context_data(self, **kwargs):
        context = super(CreateSeasonRosterView, self).get_context_data(**kwargs)
        team = get_object_or_404(Team, pk=kwargs.get('team_pk', None))

        # A user has many manager objects, with each manager object being tied to a team
        manager_objects = Manager.objects.filter(user=self.request.user).select_related('team',
                                                                                        'team__division__league__sport')
        teams_managed = [manager.team for manager in manager_objects]
        if team not in teams_managed:
            raise Http404

        sport_name = team.division.league.sport.name

        if sport_name not in SPORT_CREATE_FORM_MAPPINGS:
            raise Exception(
                    'Form class for {sport} has not been configured yet, please add it to SPORT_CREATE_FORM_MAPPINGS'.format(
                            sport=sport_name))

        context['team'] = team
        context['form'] = SPORT_CREATE_FORM_MAPPINGS[sport_name](self.request.POST or None,
                                                                 initial={'team': team.pk},
                                                                 read_only_fields=['team'],
                                                                 league=team.division.league.full_name, team=team)
        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        form = context.get('form')
        if form.is_valid():
            form.save()
            messages.success(request, 'Season roster created for {team}'.format(team=context.get('team')))
            return redirect(reverse('home'))
        return render(request, self.template_name, context)


class ListSeasonRosterView(LoginRequiredMixin, UserHasRolesMixin, generic.TemplateView):
    roles_to_check = ['Manager']
    template_name = 'seasons/list_season_roster.html'

    def get_context_data(self, **kwargs):
        context = super(ListSeasonRosterView, self).get_context_data(**kwargs)

        team = get_object_or_404(Team, pk=kwargs.get('team_pk', None))

        # Can also do Manager.objects.filter(user=self.request.user, team=team)
        is_user_manager_for_team = team.manager_set.filter(user=self.request.user).exists()
        if not is_user_manager_for_team:
            raise Http404

        sport_name = team.division.league.sport.name
        season_rosters = SPORT_MODEL_MAPPINGS[sport_name].objects.order_by('-created').filter(team=team).select_related(
                'season', 'team')
        context['season_rosters'] = season_rosters
        context['team'] = team

        return context


class UpdateSeasonRosterView(LoginRequiredMixin, UserHasRolesMixin, ContextMixin, generic.View):
    roles_to_check = ['Manager']
    template_name = 'seasons/update_season_roster.html'

    def get_context_data(self, **kwargs):
        context = super(UpdateSeasonRosterView, self).get_context_data(**kwargs)
        team = get_object_or_404(Team, pk=kwargs.get('team_pk', None))

        is_user_manager_for_team = team.manager_set.filter(user=self.request.user).exists()
        if not is_user_manager_for_team:
            raise Http404

        sport_name = team.division.league.sport.name
        season_roster_cls = SPORT_MODEL_MAPPINGS[sport_name]
        season_roster = get_object_or_404(season_roster_cls, pk=kwargs.get('pk', None))

        if season_roster.team_id != team.id:
            raise Http404

        form = SPORT_UPDATE_FORM_MAPPINGS[sport_name](self.request.POST or None, instance=season_roster, team=team)

        context['team'] = team
        context['form'] = form

        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        team = context.get('team')
        form = context.get('form')
        if form.is_valid():
            if form.has_changed():
                form.save()
                messages.success(request, 'Season roster for {team} successfully updated.'.format(team=team))
            return redirect(reverse('team:list_season_roster', kwargs={'team_pk': team.pk}))

        return render(request, self.template_name, context)
