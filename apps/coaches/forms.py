from django import forms

from teams.models import Team
from .models import Coach


class CoachForm(forms.ModelForm):
    prefix = 'coach'

    def __init__(self, *args, **kwargs):
        sport = kwargs.pop('sport', None)
        super(CoachForm, self).__init__(*args, **kwargs)
        if sport is not None:
            self.fields['team'].queryset = Team.objects.filter(division__league__sport=sport)

    class Meta:
        model = Coach
        fields = ['position', 'team']
