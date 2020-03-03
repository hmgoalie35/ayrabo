from django.conf import settings
from django.conf.urls import url
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from common.views import HealthCheckView
from games.views import BulkUploadHockeyGamesView
from home.views import AboutUsView, ContactUsView, HomePageView
from locations.views import BulkUploadLocationsView
from teams.views import BulkUploadTeamsView


project_name = 'ayrabo'
admin.site.site_header = project_name
admin.site.site_title = project_name

urlpatterns = [
    url(r'^admin/teams/bulk-upload$', BulkUploadTeamsView.as_view(), name='bulk_upload_teams'),
    url(r'^admin/locations/bulk-upload$', BulkUploadLocationsView.as_view(), name='bulk_upload_locations'),
    url(r'^admin/hockey-games/bulk-upload$', BulkUploadHockeyGamesView.as_view(), name='bulk_upload_hockeygames'),
    url(r'^admin/', admin.site.urls),

    url(r'^$', HomePageView.as_view(), name='home'),
    url(r'^about-us/$', AboutUsView.as_view(), name='about_us'),
    url(r'^contact-us/$', ContactUsView.as_view(), name='contact_us'),
    path('health-check/', HealthCheckView.as_view(), name='health-check'),
    url(r'^account/', include('accounts.urls')),  # Use our custom allauth views
    url(r'^account/', include('allauth.urls')),
    url(r'^api/', include('api.urls')),  # Don't add an `api` namespace here, drf login/logout views will break
    url(r'^leagues/', include('leagues.urls')),
    url(r'^locations/', include('locations.urls')),
    url(r'^organizations/', include('organizations.urls')),
    url(r'^sports/', include('sports.urls')),
    url(r'^teams/', include('teams.urls')),
    url(r'^users/', include('users.urls')),
]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns += [url(r'^__debug__/', include(debug_toolbar.urls)), ] + static(settings.MEDIA_URL,
                                                                                 document_root=settings.MEDIA_ROOT)
