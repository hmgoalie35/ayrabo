from escoresheet.utils.formsets import BaseFormSetHelper


class CoachFormSetHelper(BaseFormSetHelper):
    def get_extra_field_names(self):
        return ['team', 'position']
