from django.conf.urls import url
from django.urls import include

from . import views


roster_urls = [
    url(r'^rosters/update/$', views.GameRostersUpdateView.as_view(), name='update'),
]

app_name = 'games'
urlpatterns = [
    url(r'^(?P<game_pk>\d+)/', include((roster_urls, 'rosters'))),
]
