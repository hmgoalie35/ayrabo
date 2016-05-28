from django.views.generic import FormView
from .forms import EditAccountForm
from django.contrib.auth.mixins import LoginRequiredMixin


class EditAccountView(LoginRequiredMixin, FormView):
    form_class = EditAccountForm
    template_name = 'account/edit_account.html'
