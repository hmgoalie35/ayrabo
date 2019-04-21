from django.conf.urls import url
from django.urls import include


app_name = 'sports'
urlpatterns = [
    url(r'^(?P<pk>\d+)/games/', include('api.v1.games.urls')),
]
