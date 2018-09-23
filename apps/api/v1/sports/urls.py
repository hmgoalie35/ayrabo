from django.conf.urls import include, url

urlpatterns = [
    url(r'^(?P<pk>\d+)/games/', include('api.v1.games.roster_urls', namespace='games')),
]
