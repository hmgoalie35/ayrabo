from escoresheet.utils.formsets import BaseFormSetHelper


class CreateSportRegistrationFormSetHelper(BaseFormSetHelper):
    def get_extra_field_names(self):
        return ['sport', 'roles']
