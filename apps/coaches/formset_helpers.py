from ayrabo.utils.formsets import BaseFormSetHelper


class CoachFormSetHelper(BaseFormSetHelper):  # pragma: no cover
    def get_extra_field_names(self):
        return ['team', 'position']
