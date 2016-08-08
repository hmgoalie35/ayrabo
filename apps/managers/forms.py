from django import forms

from teams.models import Team
from .models import Manager
from escoresheet.utils import set_fields_disabled


class ManagerForm(forms.ModelForm):
    prefix = 'manager'

    def __init__(self, *args, **kwargs):
        sport = kwargs.pop('sport', None)
        read_only_fields = kwargs.pop('read_only_fields', None)
        super(ManagerForm, self).__init__(*args, **kwargs)
        if sport is not None:
            self.fields['team'].queryset = Team.objects.filter(division__league__sport=sport)
        if read_only_fields is not None:
            set_fields_disabled(read_only_fields, self.fields)

    class Meta:
        model = Manager
        fields = ['team']
