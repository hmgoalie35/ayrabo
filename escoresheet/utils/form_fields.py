"""
A module containing custom form fields
"""
from django import forms


class TeamModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return '{name} - {division}'.format(name=obj.name, division=obj.division.name)


class SeasonModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return '{league}: {start_year} - {end_year} Season'.format(
                league=obj.league.full_name, start_year=obj.start_date.year, end_year=obj.end_date.year)
