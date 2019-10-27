from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.views.generic import DetailView

from ayrabo.utils.mixins import HandleSportNotConfiguredMixin
from divisions.models import Division
from games.utils import get_game_list_view_context
from leagues.models import League
from leagues.utils import get_chunked_divisions
from seasons.models import Season
from seasons.utils import get_current_season_or_from_pk


class AbstractLeagueDetailView(LoginRequiredMixin, HandleSportNotConfiguredMixin, DetailView):
    context_object_name = 'league'
    queryset = League.objects.select_related('sport')

    def get_object(self, queryset=None):
        if hasattr(self, 'object'):
            return self.object
        self.object = super().get_object(queryset)
        return self.object

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        league = self.get_object()
        season = get_current_season_or_from_pk(league, self.kwargs.get('season_pk'))
        schedule_link = ''
        divisions_link = ''
        if season:
            schedule_link = season.league_detail_schedule_url
            divisions_link = season.league_detail_divisions_url
        context.update({
            'season': season,
            'schedule_link': schedule_link,
            'divisions_link': divisions_link,
            'seasons': Season.objects.get_for_league(league=league)
        })
        return context


class LeagueDetailScheduleView(AbstractLeagueDetailView):
    template_name = 'leagues/league_detail_schedule.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        league = context.get('league')
        season = context.get('season')
        sport = league.sport
        context.update({
            'current_season_page_url': reverse('leagues:schedule', kwargs={'slug': league.slug})
        })
        context.update(get_game_list_view_context(user, sport, season))
        return context


class LeagueDetailDivisionsView(AbstractLeagueDetailView):
    template_name = 'leagues/league_detail_divisions.html'
    queryset = AbstractLeagueDetailView.queryset.prefetch_related('divisions', 'divisions__teams')

    def _get_divisions(self, league, season):
        # This is a little confusing, but all we're doing is showing all divisions when viewing the current season
        # because we don't have a general list view, and only showing the divisions for the current season here would
        # mean we never actually show all divisions for the league
        if season.is_current:
            return league.divisions.all()
        teams = season.teams.all()
        division_ids = teams.values_list('division', flat=True)
        return Division.objects.prefetch_related('teams').filter(id__in=division_ids)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        league = context.get('league')
        season = context.get('season')
        if season.is_current:
            header_text = 'All Divisions'
        else:
            header_text = f'{season} Divisions'
        divisions = self._get_divisions(league, season)
        chunked_divisions = get_chunked_divisions(divisions)
        context.update({
            'active_tab': 'divisions',
            'chunked_divisions': chunked_divisions,
            'current_season_page_url': reverse('leagues:divisions', kwargs={'slug': league.slug}),
            'header_text': header_text
        })
        return context
