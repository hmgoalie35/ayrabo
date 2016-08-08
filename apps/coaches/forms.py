from django import forms

from teams.models import Team
from .models import Coach
from escoresheet.utils import set_fields_disabled


class CoachForm(forms.ModelForm):
    prefix = 'coach'

    def __init__(self, *args, **kwargs):
        sport = kwargs.pop('sport', None)
        read_only_fields = kwargs.pop('read_only_fields', None)
        super(CoachForm, self).__init__(*args, **kwargs)
        if sport is not None:
            self.fields['team'].queryset = Team.objects.filter(division__league__sport=sport)
        if read_only_fields is not None:
            set_fields_disabled(read_only_fields, self.fields)

    class Meta:
        model = Coach
        fields = ['position', 'team']
