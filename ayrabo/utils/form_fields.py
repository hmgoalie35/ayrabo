from django import forms
from django.utils import timezone


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


class BirthdayField(forms.DateField):
    """
    Custom birthday field that displays Year, Month and Day as the empty labels. In order to implement this, we needed
    to set required=False. This field is actually required and validation is done in the `.clean` function.
    """

    def _get_year_range(self):
        """
        :return: Last 100 years in descending order.
        """
        max_age = 100
        # Should be using `timezone.localdate` here, but it's possible the user hasn't selected a timezone
        # yet (ex: user profile creation). Just use UTC to be consistent.
        current_year = timezone.now().year
        return range(current_year, current_year - (max_age + 1), -1)

    def __init__(self, **kwargs):
        widget = forms.SelectDateWidget(years=self._get_year_range(), empty_label=('Year', 'Month', 'Day'))
        kwargs.update({
            'widget': widget,
            'required': False
        })
        super().__init__(**kwargs)

    def clean(self, value):
        # This should come before any other validation.
        if not value:
            raise forms.ValidationError('This field is required.')
        # The models.DateField displays a non-user friendly error message for invalid dates. forms.DateField doesn't try
        # to validate dates, it lets the model field handle that. I didn't think it was necessary to create a model date
        # field subclass so I figured this is an ok solution for now (it is reusing some code defined in
        # forms.BaseTemporalField).
        valid_date = False
        for fmt in self.input_formats:
            try:
                self.strptime(value, fmt)
                valid_date = True
            except (ValueError, TypeError):
                continue
        if not valid_date:
            raise forms.ValidationError('Please choose a valid date.')
        return value


class WeightField(forms.IntegerField):
    def __init__(self, **kwargs):
        kwargs.update({
            'label': 'Weight (in lbs)',
            'help_text': 'Round to the nearest whole number.'
        })
        super().__init__(**kwargs)


class FirstNameField(forms.CharField):
    def __init__(self, **kwargs):
        kwargs.update({
            'required': True,
            'max_length': 30  # Taken from AbstractBaseUser
        })
        super().__init__(**kwargs)


class LastNameField(forms.CharField):
    def __init__(self, **kwargs):
        kwargs.update({
            'required': True,
            'max_length': 150  # Taken from AbstractBaseUser
        })
        super().__init__(**kwargs)
