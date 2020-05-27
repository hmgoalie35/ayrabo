from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, reverse
from django.views import generic

from ayrabo.utils.exceptions import SportNotConfiguredException
from ayrabo.utils.mixins import HandleSportNotConfiguredMixin, HasPermissionMixin
from games.forms import DATETIME_INPUT_FORMAT
from managers.models import Manager
from scorekeepers.models import Scorekeeper
from sports.models import Sport
from teams.models import Team
from teams.utils import get_team_detail_view_context
from users.authorizers import GameAuthorizer
from . import mappings


class GameCreateView(LoginRequiredMixin,
                     HandleSportNotConfiguredMixin,
                     HasPermissionMixin,
                     SuccessMessageMixin,
                     generic.CreateView):
    template_name = 'games/game_create.html'
    success_message = 'Your game has been created.'

    def get_success_url(self):
        return reverse('teams:schedule', kwargs={'team_pk': self.team.pk})

    def _get_team(self):
        if hasattr(self, 'team'):
            return self.team
        self.team = get_object_or_404(
            Team.objects.select_related('division', 'division__league', 'division__league__sport'),
            pk=self.kwargs.get('team_pk', None)
        )
        self.sport = self.team.division.league.sport
        return self.team

    def has_permission_func(self):
        team = self._get_team()
        game_authorizer = GameAuthorizer(user=self.request.user)
        return game_authorizer.can_user_create(team=team)

    def get_form_class(self):
        form_cls = mappings.SPORT_GAME_CREATE_FORM_MAPPINGS.get(self.sport.name)
        if form_cls is None:
            raise SportNotConfiguredException(self.sport)
        return form_cls

    def get_form_kwargs(self):
        form_kwargs = super().get_form_kwargs()
        form_kwargs['team'] = self.team
        return form_kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'team': self.team,
            'active_tab': 'schedule'
        })
        context.update(get_team_detail_view_context(self.team))
        return context

    def form_valid(self, form):
        form.instance.team = self.team
        form.instance.created_by = self.request.user
        return super().form_valid(form)

    def get(self, request, *args, **kwargs):
        self._get_team()
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self._get_team()
        return super().post(request, *args, **kwargs)


class GameUpdateView(LoginRequiredMixin,
                     HandleSportNotConfiguredMixin,
                     HasPermissionMixin,
                     SuccessMessageMixin,
                     generic.UpdateView):
    template_name = 'games/game_update.html'
    success_message = 'Your game has been updated.'
    context_object_name = 'game'

    def _get_team(self):
        if hasattr(self, 'team'):
            return self.team
        self.team = get_object_or_404(
            Team.objects.select_related('division', 'division__league', 'division__league__sport'),
            pk=self.kwargs.get('team_pk', None)
        )
        self.sport = self.team.division.league.sport
        return self.team

    def has_permission_func(self):
        team = self._get_team()
        user = self.request.user
        game = self.get_object()
        can_update_game = Manager.objects.active().filter(user=user, team=game.team).exists()
        # Allow active managers for the game's team and make sure the game is actually for the team from the url.
        return can_update_game and team.id == game.team_id

    def get_success_url(self):
        return reverse('teams:schedule', kwargs={'team_pk': self.team.pk})

    def get_object(self, queryset=None):
        model_cls = mappings.SPORT_GAME_MODEL_MAPPINGS.get(self.sport.name, None)
        if model_cls is None:
            raise SportNotConfiguredException(self.sport)
        pk = self.kwargs.get(self.pk_url_kwarg, None)
        return get_object_or_404(model_cls.objects.select_related('home_team', 'home_team__division', 'away_team',
                                                                  'away_team__division', 'team'), pk=pk)

    def get_form_kwargs(self):
        form_kwargs = super().get_form_kwargs()
        game = self.object

        form_kwargs['team'] = self.team
        form_kwargs['initial'] = {
            'start': game.datetime_formatted(game.start, DATETIME_INPUT_FORMAT),
            'end': game.datetime_formatted(game.end, DATETIME_INPUT_FORMAT)
        }
        if not game.can_update():
            form_kwargs['disable'] = '__all__'
        return form_kwargs

    def get_form_class(self):
        form_cls = mappings.SPORT_GAME_UPDATE_FORM_MAPPINGS.get(self.sport.name)
        if form_cls is None:
            raise SportNotConfiguredException(self.sport)
        return form_cls

    def form_valid(self, form):
        if form.has_changed():
            response = super().form_valid(form)
            if 'home_team' in form.changed_data:
                self.object.home_players.clear()
            if 'away_team' in form.changed_data:
                self.object.away_players.clear()
            return response
        return redirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'team': self.team,
            'active_tab': 'schedule'
        })
        context.update(get_team_detail_view_context(self.team))
        return context

    def get(self, request, *args, **kwargs):
        self._get_team()
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self._get_team()
        return super().post(request, *args, **kwargs)


class GameRostersUpdateView(LoginRequiredMixin,
                            HandleSportNotConfiguredMixin,
                            HasPermissionMixin,
                            generic.TemplateView):
    template_name = 'games/game_rosters_update.html'

    def has_permission_func(self):
        self._get_game()
        managers = self._get_managers()
        scorekeepers = self._get_scorekeepers()
        return managers.exists() or scorekeepers.exists()

    def _get_sport(self):
        if hasattr(self, 'sport'):
            return self.sport
        self.sport = get_object_or_404(Sport, slug=self.kwargs.get('slug'))
        return self.sport

    def _get_managers(self):
        if hasattr(self, 'managers'):
            return self.managers
        user = self.request.user
        self.managers = Manager.objects.active().filter(Q(team=self.game.home_team) | Q(team=self.game.away_team),
                                                        user=user)
        return self.managers

    def _get_scorekeepers(self):
        if hasattr(self, 'scorekeepers'):
            return self.scorekeepers
        user = self.request.user
        self.scorekeepers = Scorekeeper.objects.active().filter(user=user, sport=self.sport)
        return self.scorekeepers

    def _get_game(self):
        self._get_sport()
        if hasattr(self, 'game'):
            return self.game
        model_cls = mappings.SPORT_GAME_MODEL_MAPPINGS.get(self.sport.name)
        if model_cls is None:
            raise SportNotConfiguredException(self.sport)
        self.game = get_object_or_404(
            model_cls.objects.select_related(
                'home_team__division',
                'away_team__division',
                'team__division__league__sport',
                'season',
                'location',
            ),
            pk=self.kwargs.get('game_pk')
        )
        return self.game

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        home_team = self.game.home_team
        away_team = self.game.away_team
        is_scorekeeper = self.scorekeepers.exists()
        can_update_game = self.game.can_update()

        context.update({
            'game': self.game,
            'home_team': home_team,
            'home_team_name': f'{home_team.name} {home_team.division.name}',
            'away_team': away_team,
            'away_team_name': f'{away_team.name} {away_team.division.name}',
            'can_update_home_team_roster': can_update_game and (
                self.managers.filter(team=home_team).exists() or is_scorekeeper),
            'can_update_away_team_roster': can_update_game and (
                self.managers.filter(team=away_team).exists() or is_scorekeeper),
            'sport': self.sport,
        })
        return context
