from django.urls import reverse

from ayrabo.utils.urls import url_with_query_string
from users.tabs import CHANGE_PASSWORD_TAB_KEY, INFO_TAB_KEY, SPORTS_TAB_KEY


def get_user_detail_view_context(request, user_obj, include_user_obj):
    """
    Computes common context variables needed by templates inheriting from `user_detail_base.html`. If the user is
    viewing their own profile, we want to show the change password tab. The change password functionality has it's own
    url, view, template and I didn't want to change that. As a result, if the user is on the user detail page, the
    information and sports tabs will be dynamic (toggleable via javascript), however the change password tab will link
    directly to the existing change password page (non-dynamic tab). When on the change password page, clicking the
    information or sports tabs will link directly to the user detail page and pre-select the correct tab.

    TLDR; When on the user detail page, the info and sports tabs will by dynamic (toggleable via JS). The change
    password tab will statically link to the change password page. When on the change password page, all tabs will
    statically link to the correct page, including any necessary query params (i.e. the tab query param).

    :param request: Request object.
    :param user_obj: The user of the profile currently being viewed.
    :param include_user_obj: Whether to add a `user_obj` context var. The user detail view already does this, so there's
        no need to add it. The change password page needs this context var so the user_detail_base template works as
        expected.
    :return: Context variables necessary for templates inheriting from `user_detail_base.html`.
    """
    # This is a little better than checking the request path, so we don't have to deal with query params.
    dynamic = request.resolver_match.view_name not in ['account_change_password', 'users:update']
    user_detail_url = reverse('users:detail', kwargs={'pk': user_obj.pk})
    info_tab_url = url_with_query_string(user_detail_url, tab=INFO_TAB_KEY)
    sports_tab_url = url_with_query_string(user_detail_url, tab=SPORTS_TAB_KEY)

    context = {
        'info_tab_key': INFO_TAB_KEY,
        'sports_tab_key': SPORTS_TAB_KEY,
        'change_password_tab_key': CHANGE_PASSWORD_TAB_KEY,
        # For dynamic tabs, the anchor tag's href just needs to be the id of the tab panel.
        'info_tab_link': INFO_TAB_KEY if dynamic else info_tab_url,
        'sports_tab_link': SPORTS_TAB_KEY if dynamic else sports_tab_url,
        'change_password_link': reverse('account_change_password'),
        'dynamic': dynamic
    }
    if include_user_obj:
        context.update({'user_obj': user_obj})
    return context
