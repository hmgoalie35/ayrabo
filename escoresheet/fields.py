"""
A module containing custom form fields
"""
from django import forms


class TeamModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return '{name} - {division}'.format(name=obj.name, division=obj.division.name)


class SeasonModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return '{division}: {start_year} - {end_year} Season'.format(division=obj.division.name, start_year=obj.start_date.year, end_year=obj.end_date.year)
