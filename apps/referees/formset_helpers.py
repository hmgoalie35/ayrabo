from escoresheet.utils.formsets import BaseFormSetHelper


class RefereeFormSetHelper(BaseFormSetHelper):
    def get_extra_field_names(self):
        return ['league']
