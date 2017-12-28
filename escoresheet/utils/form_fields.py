"""
A module containing custom form fields
"""
from django import forms


class TeamModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return '{name} - {division}'.format(name=obj.name, division=obj.division.name)


class SeasonModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return '{}: {}-{} Season'.format(obj.league.abbreviated_name, obj.start_date.year, obj.end_date.year)
