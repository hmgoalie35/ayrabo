from django import forms

from escoresheet.utils import set_fields_disabled
from teams.models import Team
from .models import Coach


class CoachForm(forms.ModelForm):
    prefix = 'coach'

    def __init__(self, *args, **kwargs):
        """
        Override the constructor to allow for custom kwargs to be passed to this form.
        sport -- The sport to filter teams by
        read_only_fields -- A list of fields that should be disabled in an HTML form. Note that using this will make
        django think the form 'has_changed' when it really hasn't.
        """
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
