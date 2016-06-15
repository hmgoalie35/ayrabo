from django import forms
from django.forms import TextInput

from .models import Sport


class SportForm(forms.ModelForm):
    class Meta:
        model = Sport
        fields = ['name', 'description']
        widgets = {
            'name': TextInput(attrs={'autofocus': 'true'})
        }
