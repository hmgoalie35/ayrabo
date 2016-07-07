from django import forms

from .models import Manager


class ManagerForm(forms.ModelForm):
    prefix = 'manager'

    class Meta:
        model = Manager
        fields = ['team']
