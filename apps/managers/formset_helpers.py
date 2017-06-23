from escoresheet.utils.formsets import BaseFormSetHelper


class ManagerFormSetHelper(BaseFormSetHelper):
    def get_extra_field_names(self):
        return ['team']
