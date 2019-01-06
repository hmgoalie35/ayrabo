from django.conf.urls import include, url

from . import views


roster_urls = [
    url(r'^rosters/$', views.GameRostersRetrieveUpdateAPIView.as_view(), name='retrieve-update'),
]

urlpatterns = [
    url(r'^(?P<game_pk>\d+)/', include(roster_urls, namespace='rosters')),
    url(r'^$', views.GameListAPIView.as_view(), name='list'),
]
