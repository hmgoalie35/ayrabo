from django import forms
from .models import Coach


class CoachForm(forms.ModelForm):
    prefix = 'coach'

    class Meta:
        model = Coach
        fields = ['position', 'team']
