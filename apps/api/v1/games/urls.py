from django.conf.urls import url
from django.urls import include

from . import views


roster_urls = [
    url(r'^rosters/$', views.GameRostersRetrieveUpdateAPIView.as_view(), name='retrieve-update'),
]

app_name = 'games'
urlpatterns = [
    url(r'^(?P<game_pk>\d+)/', include((roster_urls, 'rosters'))),
]
