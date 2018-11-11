from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views import generic

from common.views import CsvBulkUploadView
from locations.models import Location


class LocationDetailView(LoginRequiredMixin, generic.DetailView):
    template_name = 'locations/location_detail.html'
    queryset = Location.objects.all()
    context_object_name = 'location'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        location = self.object
        context['address'] = '{} {}, {}, {} {}'.format(location.street_number, location.street, location.city,
                                                       location.state, location.zip_code)
        context['GOOGLE_MAPS_API_KEY'] = settings.GOOGLE_MAPS_API_KEY
        # Don't render the iframe for automated tests so we don't use up our quote just for automated tests. In the
        # future the quota shouldn't matter and behave tests should really check the map gets rendered.
        context['RUNNING_AUTOMATED_TESTS'] = settings.RUNNING_AUTOMATED_TESTS
        return context


class BulkUploadLocationsView(CsvBulkUploadView):
    success_url = reverse_lazy('bulk_upload_locations')
    model = Location
    fields = ('name', 'street', 'street_number', 'city', 'state', 'zip_code', 'phone_number', 'website')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['model_cls'] = 'Location'
        context['url'] = reverse_lazy('admin:locations_location_changelist')
        return context
