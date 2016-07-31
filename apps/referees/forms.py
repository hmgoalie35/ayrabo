from django import forms

from leagues.models import League
from .models import Referee


class RefereeForm(forms.ModelForm):
    prefix = 'referee'

    def __init__(self, *args, **kwargs):
        sport = kwargs.pop('sport', None)
        super(RefereeForm, self).__init__(*args, **kwargs)
        if sport is not None:
            self.fields['league'].queryset = League.objects.filter(sport=sport)

    class Meta:
        model = Referee
        fields = ['league']
