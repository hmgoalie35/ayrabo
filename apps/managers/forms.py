from django import forms

from teams.models import Team
from .models import Manager


class ManagerForm(forms.ModelForm):
    prefix = 'manager'

    def __init__(self, *args, **kwargs):
        sport = kwargs.pop('sport', None)
        super(ManagerForm, self).__init__(*args, **kwargs)
        if sport is not None:
            self.fields['team'].queryset = Team.objects.filter(division__league__sport=sport)

    class Meta:
        model = Manager
        fields = ['team']
