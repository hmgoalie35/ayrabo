from django import forms
from django.core.exceptions import ValidationError
from django.forms import widgets

from players.models import HockeyPlayer


class GamePlayerWidget(widgets.Widget):
    template_name = 'games/widgets/game_player.html'

    def __init__(self, queryset, *args, **kwargs):
        self.queryset = queryset
        super().__init__(*args, **kwargs)

    def get_context(self, *args, **kwargs):
        context = super().get_context(*args, **kwargs)
        context.update({
            'queryset': self.queryset,
        })
        return context


class GamePlayerField(forms.Field):

    def __init__(self, queryset, *args, **kwargs):
        self.queryset = queryset or None
        kwargs.update({
            'disabled': True,
            'required': True,
            'initial': self.queryset,
        })
        self.widget = GamePlayerWidget(queryset=self.queryset)
        super().__init__(*args, **kwargs)

    def validate(self, value):
        super().validate(value)
        # This needs to be updated to handle other sports but for now we're hardcoding hockey
        if not value.filter(is_starting=True, player__position=HockeyPlayer.GOALTENDER).exists():
            raise ValidationError('Please select a starting goaltender.')
