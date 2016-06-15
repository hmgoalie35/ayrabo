from django.views.generic import View
from django.contrib import messages
from django.shortcuts import redirect
from django.core.urlresolvers import reverse
from allauth.account.models import EmailAddress


class NewConfirmationEmailView(View):
    def post(self, *args, **kwargs):
        email = self.request.POST.get('email', None)
        request_path = self.request.POST.get('request_path', None)

        if request_path is None or request_path.strip() == '':
            return redirect('/')

        if email is None or email.strip() == '':
            messages.error(self.request, 'You must specify an email address')
            return redirect(request_path)

        qs = EmailAddress.objects.filter(email=email).distinct()

        if qs.exists() and not qs.first().verified:
            email_obj = qs.first()
            email_obj.send_confirmation(self.request)
            messages.info(self.request, 'A new confirmation email has been sent to {email}'.format(email=email))
            return redirect(reverse('account_email_verification_sent'))
        else:
            messages.error(self.request, '{email} is not a valid e-mail address or has already been confirmed'.format(email=email))
            return redirect(request_path)
