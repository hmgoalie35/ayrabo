from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.urls import reverse
from django.views.generic import DetailView

from ayrabo.utils import send_season_not_configured_email
from ayrabo.utils.mixins import HandleSportNotConfiguredMixin
from games.utils import get_game_list_view_context
from players.mappings import get_player_model_cls
from seasons.mappings import get_season_roster_model_cls
from seasons.utils import get_current_season_or_from_pk
from teams.utils import get_team_detail_view_context
from users.authorizers import GameAuthorizer, SeasonRosterAuthorizer
from .models import Team


class AbstractTeamDetailView(LoginRequiredMixin, HandleSportNotConfiguredMixin, DetailView):
    context_object_name = 'team'
    pk_url_kwarg = 'team_pk'
    queryset = Team.objects.select_related('division__league__sport', 'organization')

    def get_object(self, queryset=None):
        if hasattr(self, 'object'):
            return self.object
        self.object = super().get_object(queryset)
        self.division = self.object.division
        self.league = self.division.league
        self.sport = self.league.sport
        self.season = get_current_season_or_from_pk(self.league, self.kwargs.get('season_pk'))
        return self.object

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        team = self.get_object()
        context.update(get_team_detail_view_context(team=team, season=self.season))
        return context

    def get(self, request, *args, **kwargs):
        self.get_object()
        if self.season is None:
            msg = f'Site configuration for {self.object.name} is still in progress.'
            send_season_not_configured_email(obj_name=self.object.name, view_cls=self)
            return render(request, 'misconfigurations/base.html', {'message': msg})
        return super().get(request, *args, **kwargs)


class TeamDetailScheduleView(AbstractTeamDetailView):
    template_name = 'teams/team_detail_schedule.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        team = self.get_object()
        season = context.get('season')
        game_list_context = get_game_list_view_context(user, self.sport, season, team=team)
        game_authorizer = GameAuthorizer(user=user)
        context.update({
            # Game create form displays all seasons, might as well display the button as long as the user is a manager
            'can_create_game': game_authorizer.can_user_create(team=team),
            'current_season_page_url': reverse('teams:schedule', kwargs={'team_pk': team.pk})
        })
        context.update(game_list_context)
        return context


class TeamDetailSeasonRostersView(AbstractTeamDetailView):
    template_name = 'teams/team_detail_season_rosters.html'

    def get_season_rosters(self, season, can_user_list):
        season_roster_cls = get_season_roster_model_cls(self.sport)
        if can_user_list:
            # Prefetching players__user doesn't work because the get_players call is using .filter so django can't use
            # the prefetched records. It actually hurts performance because it's a db query we don't end up using. If we
            # were to use .all, then the prefetching would work.
            qs = season_roster_cls.objects.filter(team=self.object, season=season)
            qs = qs.select_related('season', 'team', 'team__division', 'created_by')
            return qs
        return season_roster_cls.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        team = self.get_object()
        sport = team.division.league.sport
        season = context.get('season')
        season_roster_authorizer = SeasonRosterAuthorizer(user=self.request.user)
        can_user_list = season_roster_authorizer.can_user_list(team=team, sport=sport)
        season_rosters = self.get_season_rosters(season, can_user_list)
        context.update({
            'season_rosters': season_rosters,  # We'll just sort with datatables
            'has_season_rosters': season_rosters.exists(),
            'active_tab': 'season_rosters',
            'can_user_list': can_user_list,
            'can_user_create': season_roster_authorizer.can_user_create(team=team),
            'current_season_page_url': reverse('teams:season_rosters:list', kwargs={'team_pk': team.pk})
        })
        return context


class TeamDetailPlayersView(AbstractTeamDetailView):
    template_name = 'teams/team_detail_players.html'

    def _get_players(self, team):
        player_model_cls = get_player_model_cls(self.sport)
        return player_model_cls.objects.active().filter(team=team).select_related('user')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        team = self.get_object()
        players = self._get_players(team)
        has_players = players.exists()
        # The default columns to show if there are no players.
        columns = ['Jersey Number', 'Name']
        if has_players:
            # Player subclasses can define different fields, so we need to dynamically generate the columns.
            player = players.first()
            columns = list(player.table_fields.keys())
        context.update({
            'columns': columns,
            'players': players,
            'has_players': has_players,
            'header_text': 'All Players',
            'sport': self.sport,
            'active_tab': 'players'
        })
        return context
