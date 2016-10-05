from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.urlresolvers import reverse
from django.http import Http404
from django.shortcuts import render, get_object_or_404, redirect
from django.views import generic
from django.views.generic.base import ContextMixin

from managers.models import Manager
from teams.models import Team
from .forms import CreateHockeySeasonRosterForm
from .mixins import UserHasRolesMixin

SPORT_FORM_MAPPINGS = {
    'Ice Hockey': CreateHockeySeasonRosterForm
}


class CreateSeasonRosterView(LoginRequiredMixin, UserHasRolesMixin, ContextMixin, generic.View):
    template_name = 'seasons/create_season_roster.html'
    roles_to_check = ['Manager']
    user_has_no_role_msg = 'You do not have permission to perform this action.'

    def get_context_data(self, **kwargs):
        context = super(CreateSeasonRosterView, self).get_context_data(**kwargs)
        team_pk = kwargs.get('team_pk', None)
        context['team'] = None
        # A user has many manager objects, with each manager object being tied to a team
        manager_objects = Manager.objects.filter(user=self.request.user).select_related('team',
                                                                                        'team__division__league__sport')
        teams_managed = [manager.team for manager in manager_objects]
        if team_pk:
            team = get_object_or_404(Team, pk=team_pk)
            if team not in teams_managed:
                raise Http404

            context['team'] = team
            sport_name = team.division.league.sport.name

            if sport_name not in SPORT_FORM_MAPPINGS:
                raise Exception(
                        'Form class for {sport} has not been configured yet, please add it to SPORT_FORM_MAPPINGS'.format(
                                sport=sport_name))

            context['form'] = SPORT_FORM_MAPPINGS[sport_name](self.request.POST or None,
                                                              initial={'team': team.pk},
                                                              read_only_fields=['team'],
                                                              league=team.division.league.full_name)
        else:
            sport_team_mappings = {}
            for team in teams_managed:
                sport_name = team.division.league.sport.name
                if sport_name not in sport_team_mappings.keys():
                    sport_team_mappings[sport_name] = team
            context['sport_team_mappings'] = sport_team_mappings
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
