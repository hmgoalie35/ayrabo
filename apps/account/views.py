from django.views.generic import FormView, View
from .forms import EditAccountForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http.response import Http404


class EditAccountView(LoginRequiredMixin, FormView):
    form_class = EditAccountForm
    template_name = 'account/edit_account.html'


class EmailView(View):
    """
    Override django all auth's default behavior
    No user should have more than one email address, so this view is not necessary
    """
    def get(self, *args, **kwargs):
        raise Http404

    def post(self, *args, **kwargs):
        raise Http404
