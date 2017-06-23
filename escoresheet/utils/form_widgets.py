"""
A module containing custom form widgets
"""
from django.forms import extras


class SelectDateMonthDayYearInitiallyBlankWidget(extras.SelectDateWidget):
    """
    A custom date widget that initially populates month, day, year select tags with "Month", "Day", "Year" instead of
    a valid month, day, year combo.
    """

    def create_select(self, name, field, value, val, choices, none_value):
        custom_none_value = ()
        if 'year' in field:
            custom_none_value = (0, 'Year')
        elif 'month' in field:
            custom_none_value = (0, 'Month')
        elif 'day' in field:
            custom_none_value = (0, 'Day')
        choices.insert(0, custom_none_value)
        return super(SelectDateMonthDayYearInitiallyBlankWidget, self).create_select(name, field, value, val, choices,
                                                                                     none_value)
