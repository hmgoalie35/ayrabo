from django.conf.urls import url
from django.urls import include

from . import views


app_name = 'sports'
urlpatterns = [
    url(r'^register/$', views.SportRegistrationCreateView.as_view(), name='register'),
    url(r'^(?P<slug>[-\w]+)/dashboard/$', views.SportDashboardView.as_view(), name='dashboard'),
    url(r'^(?P<slug>[-\w]+)/games/', include('games.roster_urls')),
    url(r'^(?P<slug>[-\w]+)/players/', include('players.urls')),
    url(r'^(?P<slug>[-\w]+)/coaches/', include('coaches.urls')),
]
