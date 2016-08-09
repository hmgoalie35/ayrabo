from django import forms

from leagues.models import League
from .models import Referee
from escoresheet.utils import set_fields_disabled


class RefereeForm(forms.ModelForm):
    prefix = 'referee'

    def __init__(self, *args, **kwargs):
        sport = kwargs.pop('sport', None)
        read_only_fields = kwargs.pop('read_only_fields', None)
        super(RefereeForm, self).__init__(*args, **kwargs)
        if sport is not None:
            self.fields['league'].queryset = League.objects.filter(sport=sport)
        if read_only_fields is not None:
            set_fields_disabled(read_only_fields, self.fields)

    class Meta:
        model = Referee
        fields = ['league']
