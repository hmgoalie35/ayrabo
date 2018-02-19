from django.views.generic import TemplateView


class HomePageView(TemplateView):
    def get_template_names(self):
        return ['home/authenticated_home.html'] if self.request.user.is_authenticated else [
            'home/anonymous_home.html']


class AboutUsView(TemplateView):
    template_name = 'home/about_us.html'


class ContactUsView(TemplateView):
    template_name = 'home/contact_us.html'
