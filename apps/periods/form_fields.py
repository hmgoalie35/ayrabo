from django import forms


class PeriodDurationField(forms.IntegerField):
    def __init__(self, *args, **kwargs):
        from periods.model_fields import PERIOD_DURATION_MAX, PERIOD_DURATION_MIN
        kwargs.update({
            'min_value': PERIOD_DURATION_MIN,
            'max_value': PERIOD_DURATION_MAX,
        })
        super().__init__(*args, **kwargs)
