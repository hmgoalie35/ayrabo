"""
A module to store useful helper functions used throughout the code base
"""


def remove_form_placeholders(field_list):
    """
    Django all-auth by default adds in annoying placeholders, so remove them from all fields in the given list
    :param field_list: A list of fields to have placeholders removed
    :return:
    """
    for field_name in field_list:
        attributes = field_list.get(field_name).widget.attrs
        if 'placeholder' in attributes:
            attributes.pop('placeholder')


def add_autofocus_to_field(field):
    field.widget.attrs['autofocus'] = 'true'

def set_fields_disabled(read_only_fields, field_list):
    """

    :param field_list:
    :return:
    """
    for field in read_only_fields:
        the_field = field_list.get(field, None)
        if the_field is not None:
            the_field.disabled = True
