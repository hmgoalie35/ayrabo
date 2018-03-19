from django.http import Http404

from ayrabo.utils import handle_sport_not_configured
from ayrabo.utils.exceptions import SportNotConfiguredException


class HasPermissionMixin(object):
    """
    Provides a function that should be overridden and return True or False. If the function returns True, the request
    will continue as normal. If the function returns False, the specified `exception_cls` will be raised with the
    optional `exception_msg`.

    This can be used to check if a user has a manager role/is a manager for the team in question. Ex:
    def has_permission_func(self):
        return Manager.objects.active().filter(user=user, team=team).exists()
    """
    exception_cls = Http404
    exception_msg = ''

    def has_permission_func(self):
        raise NotImplementedError('You need to specify has_permission_func')

    def dispatch(self, request, *args, **kwargs):
        if self.has_permission_func():
            return super().dispatch(request, *args, **kwargs)

        raise self.exception_cls(self.exception_msg)


class HandleSportNotConfiguredMixin(object):
    """
    Useful when a view needs to fetch a model, form, etc for a specific sport. If that sport hasn't been configured
    correctly (i.e. exist in the dictionary mapping) the view should raise `SportNotConfiguredException`. This mixin
    will catch the exception and handle it appropriately.
    """

    def dispatch(self, request, *args, **kwargs):
        try:
            return super().dispatch(request, *args, **kwargs)
        except SportNotConfiguredException as e:
            return handle_sport_not_configured(request, self, e)


class DisableFormFieldsMixin(object):
    def __init__(self, *args, **kwargs):
        """
        :param disable: List of field names to disable. The special value '__all__' will disable all form fields and
        does not need to be passed as a list.
        """
        self.disable = kwargs.pop('disable', None)
        super().__init__(*args, **kwargs)
        if self.disable:
            for field_name in self.fields:
                if field_name in self.disable or self.disable == '__all__':
                    field = self.fields.get(field_name)
                    field.disabled = True
