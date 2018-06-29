from ayrabo.utils.formsets import BaseFormSetHelper


class SportRegistrationCreateFormSetHelper(BaseFormSetHelper):  # pragma: no cover
    def get_extra_field_names(self):
        return ['sport', 'roles']
