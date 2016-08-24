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
    url(r'^profile/', include('userprofiles.urls', namespace='profile')),
    url(r'^sport/', include('sports.urls', namespace='sport')),
    url(r'^api/', include('api.urls')),
]
