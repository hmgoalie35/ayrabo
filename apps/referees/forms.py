from django import forms

from .models import Referee


class RefereeForm(forms.ModelForm):
    prefix = 'referee'

    class Meta:
        model = Referee
        fields = ['division']
