from django import forms

from escoresheet.utils import set_fields_disabled
from escoresheet.fields import TeamModelChoiceField
from teams.models import Team
from .models import Manager


class ManagerForm(forms.ModelForm):
    prefix = 'manager'

    def __init__(self, *args, **kwargs):
        """
        Override the constructor to allow for custom kwargs to be passed to this form.
        sport -- The sport to filter teams by
        read_only_fields -- A list of fields that should be disabled in an HTML form. Note that using this will make
        django think the form 'has_changed' when it really hasn't.
        """
        sport = kwargs.pop('sport', None)
        read_only_fields = kwargs.pop('read_only_fields', None)
        super(ManagerForm, self).__init__(*args, **kwargs)
        if sport is not None:
            self.fields['team'].queryset = Team.objects.filter(division__league__sport=sport).select_related('division')
        if read_only_fields is not None:
            set_fields_disabled(read_only_fields, self.fields)

    team = TeamModelChoiceField(queryset=Team.objects.all().select_related('division'))

    class Meta:
        model = Manager
        fields = ['team']
