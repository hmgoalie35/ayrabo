from django.conf.urls import url
from django.urls import include


app_name = 'v1'
urlpatterns = [
    url(r'^sports/', include('api.v1.sports.urls')),
    url(r'^teams/', include('api.v1.teams.urls')),
]
