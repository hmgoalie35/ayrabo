from django.conf.urls import include, url

from . import views


season_urls = [
    url(r'^$', views.LeagueDetailScheduleView.as_view(), name='schedule'),
    url(r'^divisions/$', views.LeagueDetailDivisionsView.as_view(), name='divisions'),
]

urlpatterns = [
    url(r'^(?P<slug>[-\w]+)/$', views.LeagueDetailScheduleView.as_view(), name='schedule'),
    url(r'^(?P<slug>[-\w]+)/divisions/$', views.LeagueDetailDivisionsView.as_view(), name='divisions'),
    url(r'^(?P<slug>[-\w]+)/seasons/(?P<season_pk>\d+)/', include(season_urls, namespace='seasons')),
]
