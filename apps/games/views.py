from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Q
from django.shortcuts import get_object_or_404, reverse, redirect
from django.urls import reverse_lazy
from django.views import generic

from common.views import CsvBulkUploadView
from escoresheet.utils.exceptions import SportNotConfiguredException
from escoresheet.utils.mixins import HasPermissionMixin, HandleSportNotConfiguredMixin
from games.forms import HockeyGameCreateForm, HockeyGameUpdateForm, DATETIME_INPUT_FORMAT
from games.models import HockeyGame
from managers.models import Manager
from scorekeepers.models import Scorekeeper
from sports.models import Sport
from teams.models import Team

SPORT_GAME_CREATE_FORM_MAPPINGS = {
    'Ice Hockey': HockeyGameCreateForm
}

SPORT_GAME_UPDATE_FORM_MAPPINGS = {
    'Ice Hockey': HockeyGameUpdateForm
}

SPORT_GAME_MODEL_MAPPINGS = {
    'Ice Hockey': HockeyGame
}


class GameCreateView(LoginRequiredMixin,
                     HandleSportNotConfiguredMixin,
                     HasPermissionMixin,
                     SuccessMessageMixin,
                     generic.CreateView):
    template_name = 'games/game_create.html'
    success_message = 'Your game has been created.'

    def _get_sport_registration_url(self):
        sport_registration = self.request.user.sportregistration_set.get(sport_id=self.sport.id)
        return reverse('sportregistrations:detail', kwargs={'pk': sport_registration.id})

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
        user = self.request.user
        team = self._get_team()
        return Manager.objects.active().filter(user=user, team=team).exists()

    def get_success_url(self):
        return self._get_sport_registration_url()

    def get_form_class(self):
        form_cls = SPORT_GAME_CREATE_FORM_MAPPINGS.get(self.sport.name)
        if form_cls is None:
            raise SportNotConfiguredException(self.sport)
        return form_cls

    def get_form_kwargs(self):
        form_kwargs = super().get_form_kwargs()
        form_kwargs['team'] = self.team
        return form_kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['team'] = self.team
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
        return reverse('teams:games:list', kwargs={'team_pk': self.team.pk})

    def get_object(self, queryset=None):
        model_cls = SPORT_GAME_MODEL_MAPPINGS.get(self.sport.name, None)
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
        form_cls = SPORT_GAME_UPDATE_FORM_MAPPINGS.get(self.sport.name)
        if form_cls is None:
            raise SportNotConfiguredException(self.sport)
        return form_cls

    def form_valid(self, form):
        if form.has_changed():
            return super().form_valid(form)
        return redirect(reverse('teams:games:list', kwargs={'team_pk': self.team.pk}))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['team'] = self.team
        return context

    def get(self, request, *args, **kwargs):
        self._get_team()
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self._get_team()
        return super().post(request, *args, **kwargs)


class GameListView(LoginRequiredMixin, HandleSportNotConfiguredMixin, generic.ListView):
    template_name = 'games/game_list.html'
    context_object_name = 'games'

    def _get_team(self):
        if hasattr(self, 'team'):
            return self.team
        self.team = get_object_or_404(
            Team.objects.select_related('division', 'division__league', 'division__league__sport'),
            pk=self.kwargs.get('team_pk', None)
        )
        self.sport = self.team.division.league.sport
        return self.team

    def get_queryset(self):
        model_cls = SPORT_GAME_MODEL_MAPPINGS.get(self.sport.name, None)
        if model_cls is None:
            raise SportNotConfiguredException(self.sport)
        return model_cls.objects.filter(Q(home_team=self.team) | Q(away_team=self.team)).select_related(
            'home_team', 'away_team', 'type', 'location', 'season', 'team')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        managers_for_user = Manager.objects.active().filter(user=user)
        context['can_create_game'] = managers_for_user.filter(team=self.team).exists()
        context['is_scorekeeper'] = Scorekeeper.objects.active().filter(user=user, sport=self.sport).exists()
        context['team_ids_for_manager'] = managers_for_user.filter(
            team__division__league__sport=self.sport).values_list('team_id', flat=True)
        context['team'] = self.team
        context['sport'] = self.sport
        return context

    def get(self, request, *args, **kwargs):
        self._get_team()
        return super().get(request, *args, **kwargs)


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
        model_cls = SPORT_GAME_MODEL_MAPPINGS.get(self.sport.name)
        if model_cls is None:
            raise SportNotConfiguredException(self.sport)

        self.game = get_object_or_404(
            model_cls.objects.select_related('home_team', 'home_team__division', 'away_team',
                                             'away_team__division', 'team', 'team__division',
                                             'team__division__league',
                                             'team__division__league__sport'),
            pk=self.kwargs.get('game_pk')
        )
        return self.game

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        home_team = self.game.home_team
        away_team = self.game.away_team
        is_scorekeeper = self.scorekeepers.exists()
        can_update_game = self.game.can_update()

        context['game'] = self.game
        context['home_team'] = '{} {}'.format(home_team.name, home_team.division.name)
        context['away_team'] = '{} {}'.format(away_team.name, away_team.division.name)
        context['can_update_home_team_roster'] = can_update_game and (
                self.managers.filter(team=home_team).exists() or is_scorekeeper)
        context['can_update_away_team_roster'] = can_update_game and (
                self.managers.filter(team=away_team).exists() or is_scorekeeper)
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
