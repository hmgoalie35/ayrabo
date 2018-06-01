from django.conf import settings
from django.views.generic import TemplateView


class HomePageView(TemplateView):
    def get_template_names(self):
        return ['home/authenticated_home.html'] if self.request.user.is_authenticated else [
            'home/anonymous_home.html']


class AboutUsView(TemplateView):
    template_name = 'home/about_us.html'


class ContactUsView(TemplateView):
    template_name = 'home/contact_us.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['support_contact'] = {
            'name': 'Harris Pittinsky',
            'email': settings.SUPPORT_EMAIL,
        }
        return context
