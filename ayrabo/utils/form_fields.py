"""
A module containing custom form fields
"""
from django import forms


class TeamModelMultipleChoiceField(forms.ModelMultipleChoiceField):
    def label_from_instance(self, obj):
        return '{name} - {division}'.format(name=obj.name, division=obj.division.name)


class TeamModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return '{name} - {division}'.format(name=obj.name, division=obj.division.name)


class SeasonModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return '{}: {}-{} Season'.format(obj.league.abbreviated_name, obj.start_date.year, obj.end_date.year)


class PlayerModelMultipleChoiceField(forms.ModelMultipleChoiceField):
    def __init__(self, *args, **kwargs):
        self.position_field = kwargs.pop('position_field')
        super().__init__(*args, **kwargs)

    def label_from_instance(self, obj):
        position = getattr(obj, self.position_field)
        return '#{} {} {}'.format(obj.jersey_number, obj.user.get_full_name(), position)
