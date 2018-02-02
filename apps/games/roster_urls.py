from django.conf.urls import url, include

from . import views

roster_urls = [
    url(r'^rosters/update/$', views.GameRostersUpdateView.as_view(), name='update'),
]

urlpatterns = [
    url(r'^(?P<pk>\d+)/', include(roster_urls, namespace='rosters')),
]
