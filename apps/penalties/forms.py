from django import forms

from sports.models import Sport
from .models import HockeyPenalty


class HockeyPenaltyAdminForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        sport = Sport.objects.get(name='Ice Hockey')

        HockeyPlayerModel = self.fields['player'].queryset.model
        self.fields['player'].queryset = HockeyPlayerModel.objects.active().select_related('user').filter(sport=sport)

    class Meta:
        model = HockeyPenalty
        fields = ['game', 'period', 'type', 'duration', 'player', 'time_in', 'time_out']
