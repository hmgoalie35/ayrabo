from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, HTML, Div, Field


# TODO move this to a base class for use with creating sport regs. Only thing that differs is the model specific fields
class BasePlayerFormSetHelper(FormHelper):
    def __init__(self, *args, **kwargs):
        player_specific_fields = kwargs.pop('player_specific_fields', [])
        fields = [Field(f) for f in player_specific_fields]
        super(BasePlayerFormSetHelper, self).__init__(*args, **kwargs)
        self.layout = Layout(
                Div(
                        HTML(
                                "{% if not forloop.first %}<span data-toggle=\"tooltip\" data-placement=\"top\" "
                                "title=\"Remove form\" class=\"fa fa-trash fa-trash-red pull-right\"></span>{% endif %}"
                        ),
                        Field('team'),
                        Field('jersey_number'),
                        Field('position'),
                        *fields,
                        Field('form_num'),
                        Field('id'),
                        css_class="multiField"
                )
        )
        self.form_tag = False
        # csrf token is added in the template
        self.disable_csrf = True


class HockeyPlayerFormSetHelper(BasePlayerFormSetHelper):
    def __init__(self, *args, **kwargs):
        player_specific_fields = ['handedness']
        super(HockeyPlayerFormSetHelper, self).__init__(player_specific_fields=player_specific_fields, *args, **kwargs)


class BaseballPlayerFormSetHelper(BasePlayerFormSetHelper):
    def __init__(self, *args, **kwargs):
        player_specific_fields = ['catches', 'bats']
        super(BaseballPlayerFormSetHelper, self).__init__(player_specific_fields=player_specific_fields, *args,
                                                          **kwargs)
