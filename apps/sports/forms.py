from django import forms
from .models import Sport
from django.forms import TextInput


class SportForm(forms.ModelForm):
    class Meta:
        model = Sport
        fields = ['name', 'description']
        widgets = {
            'name': TextInput(attrs={'autofocus': 'true'})
        }
