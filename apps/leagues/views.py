from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.views.generic import DetailView

from ayrabo.utils import chunk
from ayrabo.utils.mixins import HandleSportNotConfiguredMixin
from games.mappings import get_game_model_cls
from games.utils import get_game_list_context, optimize_games_query
from leagues.models import League
from seasons.models import Season


class AbstractLeagueDetailView(LoginRequiredMixin, HandleSportNotConfiguredMixin, DetailView):
    context_object_name = 'league'
    queryset = League.objects.select_related('sport')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        league = self.object
        past_seasons = Season.objects.get_past(league=league)
        context.update({
            'past_seasons': past_seasons
        })
        return context


class LeagueScheduleView(AbstractLeagueDetailView):
    """
    League detail view that defaults to displaying the league's schedule for the current season
    """
    template_name = 'leagues/league_detail_schedule.html'

    def _get_games(self, sport, season):
        model_cls = get_game_model_cls(sport)
        # Seasons are tied to leagues so we don't need to exclude games for other leagues
        qs = model_cls.objects.filter(season=season)
        return optimize_games_query(qs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        league = self.object
        season_pk = self.kwargs.get('season_pk')
        if season_pk is not None:
            season = get_object_or_404(Season.objects.filter(league=league), pk=season_pk)
            active_tab = 'past_seasons'
        else:
            season = Season.objects.get_current(league=league)
            active_tab = 'schedule'
        sport = league.sport
        game_list_context = get_game_list_context(user, sport)
        games = self._get_games(sport, season)
        context.update({
            'active_tab': active_tab,
            'season': season,
            'games': games,
        })
        context.update(game_list_context)
        return context


class LeagueDivisionsView(AbstractLeagueDetailView):
    template_name = 'leagues/league_detail_divisions.html'
    queryset = AbstractLeagueDetailView.queryset.prefetch_related('divisions', 'divisions__teams')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        league = self.object
        divisions = league.divisions.all()
        per_row = 4
        # The generator gets exhausted after the template loops over the chunked divisions so using it anywhere else
        # resulted in an empty array. Convert to a list here to prevent this problem.
        chunked_divisions = list(chunk(divisions, per_row))
        context.update({
            'active_tab': 'divisions',
            'chunked_divisions': chunked_divisions,
        })
        return context
