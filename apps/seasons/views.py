from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core import mail
from django.core.urlresolvers import reverse
from django.http import Http404
from django.shortcuts import render, get_object_or_404, redirect
from django.views import generic
from django.views.generic.base import ContextMixin

from escoresheet.utils import UserHasRolesMixin
from managers.models import Manager
from teams.models import Team
from .forms import CreateHockeySeasonRosterForm, UpdateHockeySeasonRosterForm
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

SPORT_NOT_CONFIGURED_MSG = "{sport} hasn't been configured correctly in our system. If you believe this is an error please contact us."


def email_admins_sport_not_configured(sport_name, view_cls):
    subject = '{sport_name} incorrectly configured'.format(sport_name=sport_name)
    mail.mail_admins(subject,
                     '{sport} incorrectly configured on the {page} ({cls}) page. You will likely need to add a mapping to the appropriate dictionary.'.format(
                             sport=sport_name, page=view_cls.request.path, cls=view_cls.__class__.__name__))


def get_create_form_for_sport(sport_name):
    """
    Gets the correct create season roster form class for the specified sport

    :param sport_name: The sport to get the season roster form for

    :return: The create season roster form class if the sport is a valid key and None otherwise
    """
    return SPORT_CREATE_FORM_MAPPINGS[sport_name] if sport_name in SPORT_CREATE_FORM_MAPPINGS.keys() else None


def get_update_form_for_sport(sport_name):
    """
    Gets the correct update season roster form class for the specified sport

    :param sport_name: The sport to get the season roster form for

    :return: The update season roster form class if the sport is a valid key and None otherwise
    """
    return SPORT_UPDATE_FORM_MAPPINGS[sport_name] if sport_name in SPORT_UPDATE_FORM_MAPPINGS.keys() else None


def get_model_for_sport(sport_name):
    """
    Gets the correct season roster model class for the specified sport

    :param sport_name: The sport to get the season roster model for

    :return: The season roster model class if the sport is a valid key and None otherwise
    """
    return SPORT_MODEL_MAPPINGS[sport_name] if sport_name in SPORT_MODEL_MAPPINGS.keys() else None


class CreateSeasonRosterView(LoginRequiredMixin, UserHasRolesMixin, ContextMixin, generic.View):
    template_name = 'seasons/season_roster_create.html'
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

        form_cls = get_create_form_for_sport(sport_name)
        form = None
        if form_cls:
            form = form_cls(self.request.POST or None, initial={'team': team.pk}, read_only_fields=['team'],
                            league=team.division.league.full_name, team=team)
        context['team'] = team
        context['form'] = form
        context['sport_name'] = sport_name
        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        if context.get('form') is None:
            sport = context.get('sport_name')
            email_admins_sport_not_configured(sport, self)
            return render(request, 'message.html', {'message': SPORT_NOT_CONFIGURED_MSG.format(sport=sport)})
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        form = context.get('form')
        if context.get('form') is None:
            sport = context.get('sport_name')
            email_admins_sport_not_configured(sport, self)
            return render(request, 'message.html', {'message': SPORT_NOT_CONFIGURED_MSG.format(sport=sport)})
        if form.is_valid():
            form.save()
            messages.success(request, 'Season roster created for {team}'.format(
                    team=context.get('team')))
            return redirect(reverse('home'))
        return render(request, self.template_name, context)


class ListSeasonRosterView(LoginRequiredMixin, UserHasRolesMixin, generic.TemplateView):
    roles_to_check = ['Manager']
    template_name = 'seasons/season_roster_list.html'

    def get_context_data(self, **kwargs):
        context = super(ListSeasonRosterView, self).get_context_data(**kwargs)

        team = get_object_or_404(Team, pk=kwargs.get('team_pk', None))

        # Can also do Manager.objects.filter(user=self.request.user, team=team)
        is_user_manager_for_team = team.manager_set.filter(user=self.request.user).exists()
        if not is_user_manager_for_team:
            raise Http404

        sport_name = team.division.league.sport.name
        season_roster_cls = get_model_for_sport(sport_name)
        season_rosters = None
        if season_roster_cls:
            season_rosters = season_roster_cls.objects.order_by('-created').filter(team=team).select_related(
                    'season', 'team')
        context['season_rosters'] = season_rosters
        context['team'] = team

        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        if context.get('season_rosters') is None:
            sport = context.get('team').division.league.sport
            email_admins_sport_not_configured(sport, self)
            return render(request, 'message.html', {'message': SPORT_NOT_CONFIGURED_MSG.format(sport=sport)})
        return super(ListSeasonRosterView, self).get(request, *args, **kwargs)


class UpdateSeasonRosterView(LoginRequiredMixin, UserHasRolesMixin, ContextMixin, generic.View):
    roles_to_check = ['Manager']
    template_name = 'seasons/season_roster_update.html'

    def get_context_data(self, **kwargs):
        context = super(UpdateSeasonRosterView, self).get_context_data(**kwargs)
        team = get_object_or_404(Team, pk=kwargs.get('team_pk', None))

        is_user_manager_for_team = team.manager_set.filter(user=self.request.user).exists()
        if not is_user_manager_for_team:
            raise Http404

        sport_name = team.division.league.sport.name

        season_roster_cls = get_model_for_sport(sport_name)
        season_roster = None
        if season_roster_cls:
            season_roster = get_object_or_404(season_roster_cls, pk=kwargs.get('pk', None))

        context['season_roster'] = season_roster
        context['sport_name'] = sport_name
        if season_roster is None:
            return context

        if season_roster.team_id != team.id:
            raise Http404

        form_cls = get_update_form_for_sport(sport_name)
        form = None
        if form_cls:
            form = form_cls(self.request.POST or None, instance=season_roster, team=team)

        context['team'] = team
        context['form'] = form

        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        if context.get('season_roster') is None or context.get('form') is None:
            sport = context.get('sport_name')
            email_admins_sport_not_configured(sport, self)
            return render(request, 'message.html',
                          {'message': SPORT_NOT_CONFIGURED_MSG.format(sport=sport)})
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        team = context.get('team')
        form = context.get('form')
        if context.get('season_roster') is None or form is None:
            sport = context.get('sport_name')
            email_admins_sport_not_configured(sport, self)
            return render(request, 'message.html',
                          {'message': SPORT_NOT_CONFIGURED_MSG.format(sport=sport)})
        if form.is_valid():
            if form.has_changed():
                form.save()
                messages.success(
                        request, 'Season roster for {team} successfully updated.'.format(team=team))
            return redirect(reverse('team:list_season_roster', kwargs={'team_pk': team.pk}))

        return render(request, self.template_name, context)
