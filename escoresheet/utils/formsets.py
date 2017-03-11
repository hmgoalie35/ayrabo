from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, HTML, Div, Field
from django import forms


class BaseModelFormSet(forms.BaseModelFormSet):
    """
    Base model formset class that provides the necessary field(s) to support adding/removing of forms via JavaScript.
    """

    def add_fields(self, form, index):
        super(BaseModelFormSet, self).add_fields(form, index)
        # The empty form would have value `None`, so default to an invalid form_num for use in the js.
        form_num = index if index is not None else -1
        form.fields['form_num'] = forms.IntegerField(required=False, widget=forms.HiddenInput(
                attrs={'data-form-num': form_num, 'class': 'form-num'}))


class BaseFormSetHelper(FormHelper):
    """
    Base formset helper class that renders out an icon to remove the form, form_num field for the JavaScript to work
    and any additional fields to display.
    """
    def __init__(self, *args, **kwargs):
        super(BaseFormSetHelper, self).__init__(*args, **kwargs)
        field_names = self.get_extra_field_names()
        fields = [Field(f) for f in field_names]
        self.layout = Layout(
                Div(
                        HTML(
                                "{% if not forloop.first %}<span data-toggle=\"tooltip\" data-placement=\"top\" "
                                "title=\"Remove form\" class=\"fa fa-trash fa-trash-red pull-right\"></span>{% endif %}"
                        ),
                        *fields,
                        Field('form_num'),
                        Field('id'),
                        css_class="multiField"
                )
        )
        self.form_tag = False
        # csrf token is added in the template
        self.disable_csrf = True

    def get_extra_field_names(self):
        """
        Override this to specify additional fields that should be rendered in the formset. Should return a list of field
        names as strings. `Field` objects will be instantiated for you.
        """
        raise NotImplementedError()
