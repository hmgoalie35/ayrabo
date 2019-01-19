from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView

from ayrabo.utils.mixins import HandleSportNotConfiguredMixin
from games.utils import get_game_list_view_context
from leagues.models import League
from seasons.models import Season
from seasons.utils import get_chunked_divisions


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
        past_seasons = Season.objects.get_past(league=league)
        context.update({
            'past_seasons': past_seasons
        })
        return context


class LeagueDetailScheduleView(AbstractLeagueDetailView):
    template_name = 'leagues/league_detail_schedule.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        league = context.get('league')
        sport = league.sport
        current_season = Season.objects.get_current(league=league)
        context.update(get_game_list_view_context(user, sport, current_season))
        return context


class LeagueDetailDivisionsView(AbstractLeagueDetailView):
    template_name = 'leagues/league_detail_divisions.html'
    queryset = AbstractLeagueDetailView.queryset.prefetch_related('divisions', 'divisions__teams')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        league = context.get('league')
        chunked_divisions = get_chunked_divisions(league.divisions.all())
        context.update({
            'active_tab': 'divisions',
            'chunked_divisions': chunked_divisions,
        })
        return context
