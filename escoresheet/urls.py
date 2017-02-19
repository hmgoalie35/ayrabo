from django.conf import settings
from django.conf.urls import url, include
from django.contrib import admin

from home.views import HomePageView, AboutUsView, ContactUsView
from teams.views import BulkUploadTeamsView

urlpatterns = [
    url(r'^admin/teams/team/bulk-upload-teams', BulkUploadTeamsView.as_view(), name='bulk_upload_teams'),
    url(r'^admin/', admin.site.urls),
    url(r'^$', HomePageView.as_view(), name='home'),
    url(r'^about-us$', AboutUsView.as_view(), name='about_us'),
    url(r'^contact-us$', ContactUsView.as_view(), name='contact_us'),

    # This allows me to override allauth views, and add in custom views under account/
    url(r'^account/', include('accounts.urls')),
    url(r'^account/', include('allauth.urls')),
    url(r'^', include('sports.urls')),
    url(r'^', include('teams.urls')),
    # Adding namespace of `api` will cause drf login/logout/obtain token endpoints to fail because they need to
    # only be under the rest_framework namespace.
    url(r'^api/', include('api.urls')),
    url(r'^managers/', include('managers.urls', namespace='managers')),

]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns += [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ]
