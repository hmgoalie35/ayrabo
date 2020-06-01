from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import get_object_or_404, redirect, reverse
from django.views import generic

from ayrabo.utils.exceptions import SportNotConfiguredException
from ayrabo.utils.mixins import HandleSportNotConfiguredMixin, HasPermissionMixin
from games.forms import DATETIME_INPUT_FORMAT
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
            Team.objects.select_related('division', 'division__league', 'division__league__sport', 'organization'),
            pk=self.kwargs.get('team_pk', None)
        )
        self.sport = self.team.division.league.sport
        return self.team

    def has_permission_func(self):
        team = self._get_team()
        game = self.get_object()
        game_authorizer = GameAuthorizer(user=self.request.user)
        # NOTE: we are purposefully checking if the user can update the game's team, not game home team or game away
        # team. We also need to remember to make sure the game is actually for the team from the url.
        return game_authorizer.can_user_update(team=game.team) and team.id == game.team_id

    def get_success_url(self):
        return reverse('teams:schedule', kwargs={'team_pk': self.team.pk})

    def get_object(self, queryset=None):
        model_cls = mappings.SPORT_GAME_MODEL_MAPPINGS.get(self.sport.name, None)
        if model_cls is None:
            raise SportNotConfiguredException(self.sport)
        return get_object_or_404(
            model_cls.objects.select_related(
                'home_team',
                'home_team__division',
                'away_team',
                'away_team__division',
                'team'
            ),
            pk=self.kwargs.get(self.pk_url_kwarg, None)
        )

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

    def setup(self, *args, **kwargs):
        super().setup(*args, **kwargs)
        self.game_authorizer = GameAuthorizer(user=self.request.user)

    def has_permission_func(self):
        self._get_game()
        return self.game_authorizer.can_user_update_game_rosters(
            home_team=self.game.home_team,
            away_team=self.game.away_team,
            sport=self.sport
        )

    def _get_sport(self):
        if hasattr(self, 'sport'):
            return self.sport
        self.sport = get_object_or_404(Sport, slug=self.kwargs.get('slug'))
        return self.sport

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
                'home_team__organization',
                'away_team__division',
                'away_team__organization',
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
        can_update_game = self.game.can_update()

        context.update({
            'game': self.game,
            'home_team': home_team,
            'home_team_name': f'{home_team.name} {home_team.division.name}',
            'away_team': away_team,
            'away_team_name': f'{away_team.name} {away_team.division.name}',
            'can_update_home_team_roster': can_update_game and self.game_authorizer.can_user_update_game_roster(
                team=home_team, sport=self.sport
            ),
            'can_update_away_team_roster': can_update_game and self.game_authorizer.can_user_update_game_roster(
                team=away_team, sport=self.sport
            ),
            'sport': self.sport,
        })
        return context
