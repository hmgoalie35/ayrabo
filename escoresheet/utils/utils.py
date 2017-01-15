"""
A module to store useful helper functions used throughout the code base
"""


def remove_form_placeholders(field_list):
    """
    Django all-auth by default adds in annoying placeholders, so remove them from all fields in the given list

    :param field_list: A list of fields to have placeholders removed
    """
    for field_name in field_list:
        attributes = field_list.get(field_name).widget.attrs
        if 'placeholder' in attributes:
            attributes.pop('placeholder')


def add_autofocus_to_field(field):
    field.widget.attrs['autofocus'] = 'true'


def set_fields_disabled(read_only_fields, field_list):
    """
    Given a list of form fields, sets them to disabled so the HTML form being rendered shows them as disabled.
    Django will also ignore any POST data that has the field's name attribute in it (in the case of tampering)

    __all__ can be specified to disable all fields.

    :param read_only_fields: The fields to mark as disabled
    :param field_list: The list of fields of the form
    """
    if '__all__' in read_only_fields:
        read_only_fields = [field for field in field_list]

    for field in read_only_fields:
        the_field = field_list.get(field, None)
        if the_field is not None:
            the_field.disabled = True
