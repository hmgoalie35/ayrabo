from django.conf.urls import include, url

from seasons.urls import season_urls
from . import views


urlpatterns = [
    url(r'^(?P<slug>[-\w]+)/$', views.LeagueDetailScheduleView.as_view(), name='schedule'),
    url(r'^(?P<slug>[-\w]+)/divisions/$', views.LeagueDetailDivisionsView.as_view(), name='divisions'),
    url(r'^(?P<slug>[-\w]+)/seasons/', include(season_urls, namespace='seasons')),
]
