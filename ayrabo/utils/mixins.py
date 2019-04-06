from django.http import Http404
from waffle import flag_is_active, switch_is_active

from ayrabo.utils import handle_sport_not_configured
from ayrabo.utils.exceptions import SportNotConfiguredException


class HasPermissionMixin(object):
    """
    Provides a function that should be overridden and return True or False. If the function returns True, the request
    will continue as normal. If the function returns False, `on_has_permission_failure` will run, and by default raise
    `exception_cls` with message `exception_msg`.

    This can be used to check if a user has a manager role/is a manager for the team in question. Ex:
    def has_permission_func(self):
        return Manager.objects.active().filter(user=user, team=team).exists()
    """
    exception_cls = Http404
    exception_msg = ''

    def has_permission_func(self):
        raise NotImplementedError('You need to specify has_permission_func')

    def on_has_permission_failure(self):
        raise self.exception_cls(self.exception_msg)

    def dispatch(self, request, *args, **kwargs):
        if self.has_permission_func():
            return super().dispatch(request, *args, **kwargs)

        return self.on_has_permission_failure()


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


class PreSelectedTabMixin(object):
    """
    This mixin takes the last tab selected by a user and makes it the active tab after a page refresh/navigation.
    To use this mixin, redefine the `valid_tabs` and `default_tab` class variables on the desired view. The active tab
    is stored in a `tab` query param and updated via javascript when the user toggles b/w tabs. To enable the
    javascript functionality, add `data-tab=<value>` to the DOM element (which will likely be an anchor tag).
    `<value>` needs to be a value from `valid_tabs`. An `active_tab` variable will be available in the template.
    """
    valid_tabs = []
    default_tab = None

    def validate(self, valid_tabs, default_tab):
        """
        This logic was previously in the constructor but self.request isn't available in the constructor so errors were
        getting thrown. Resort to just calling this function when we know request has been set on self, etc.
        """
        assert isinstance(valid_tabs, list), 'valid_tabs must be a list'
        if default_tab is not None:
            assert isinstance(default_tab, str) and len(default_tab) > 0, 'default_tab must be a non-empty string'
            assert default_tab in valid_tabs, '{} is not a valid choice, choose from {}'.format(default_tab,
                                                                                                ', '.join(valid_tabs))

    def get_default_tab(self):
        return self.default_tab

    def get_valid_tabs(self):
        return self.valid_tabs

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        valid_tabs = self.get_valid_tabs()
        default_tab = self.get_default_tab()
        self.validate(valid_tabs, default_tab)
        tab = self.request.GET.get('tab', None)
        context['active_tab'] = tab if tab in valid_tabs else default_tab
        return context


class AbstractWaffleMixin(object):
    """
    This mixin exists because there may be times where it doesn't even make sense to call the `HasPermissionMixin`, so
    having this mixin run first makes more sense. It also allows us to keep things separate. This mixin should be
    placed before `HasPermissionMixin`.
    """
    waffle_identifier = None  # Name of the flag, switch or sample
    exception_cls = Http404
    exception_msg = ''

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        assert self.waffle_identifier, 'You must specify `waffle_identifier`'

    def dispatch(self, request, *args, **kwargs):
        if self.check(request, *args, **kwargs):
            return super().dispatch(request, *args, **kwargs)
        raise self.exception_cls(self.exception_msg)

    def check(self, request, *args, **kwargs):
        raise NotImplementedError()


class WaffleSwitchMixin(AbstractWaffleMixin):
    def check(self, request, *args, **kwargs):
        return switch_is_active(self.waffle_identifier)


class WaffleFlagMixin(AbstractWaffleMixin):
    def check(self, request, *args, **kwargs):
        return flag_is_active(request, self.waffle_identifier)
