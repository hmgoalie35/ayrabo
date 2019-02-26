from allauth.account import views
from allauth.account.models import EmailAddress
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import View

from users.tabs import CHANGE_PASSWORD_TAB_KEY
from users.utils import get_user_detail_view_context


class NewConfirmationEmailView(View):
    """
    A view that when POSTed to generates a new confirmation email for the given email address.
    """

    def post(self, *args, **kwargs):
        email = self.request.POST.get('email', None)
        request_path = self.request.POST.get('request_path', None)

        if request_path is None or request_path.strip() == '':
            return redirect('/')

        if email is None or email.strip() == '':
            messages.error(self.request, 'You must specify an email address.')
            return redirect(request_path)

        qs = EmailAddress.objects.filter(email=email).distinct()

        if qs.exists() and not qs.first().verified:
            email_obj = qs.first()
            email_obj.send_confirmation(self.request)
            messages.info(self.request, 'A new confirmation email has been sent to {}.'.format(email))
            return redirect(reverse('account_email_verification_sent'))
        else:
            messages.error(self.request,
                           '{} is not a valid e-mail address or has already been confirmed.'.format(email))
            return redirect(request_path)


class PasswordChangeView(LoginRequiredMixin, views.PasswordChangeView):
    def get_success_url(self):
        return reverse('users:detail', kwargs={'pk': self.request.user.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'active_tab': CHANGE_PASSWORD_TAB_KEY
        })
        context.update(get_user_detail_view_context(self.request, self.request.user, include_user_obj=True))
        return context
