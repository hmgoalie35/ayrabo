from django.conf.urls import url, include

urlpatterns = [
    url(r'^(?P<team_pk>\d+)/', include('seasons.urls')),
    url(r'^(?P<team_pk>\d+)/games/', include('games.urls', namespace='games')),
]
