from django.urls import reverse_lazy

from common.views import CsvBulkUploadView
from locations.models import Location


class BulkUploadLocationsView(CsvBulkUploadView):
    success_url = reverse_lazy('bulk_upload_locations')
    model = Location
    fields = ['name', 'street', 'street_number', 'city', 'state', 'zip_code', 'phone_number', 'website']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['model_cls'] = 'Location'
        context['url'] = reverse_lazy('admin:locations_location_changelist')
        return context
