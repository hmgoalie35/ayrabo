from ayrabo.utils.formsets import BaseFormSetHelper


class HockeyPlayerFormSetHelper(BaseFormSetHelper):
    def get_extra_field_names(self):
        return ['team', 'jersey_number', 'position', 'handedness']


class BaseballPlayerFormSetHelper(BaseFormSetHelper):
    def get_extra_field_names(self):
        return ['team', 'jersey_number', 'position', 'catches', 'bats']
