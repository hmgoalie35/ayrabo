from django.conf.urls import url, include

urlpatterns = [
    url(r'^teams/(?P<team_pk>\d+)/', include('seasons.urls', namespace='teams')),
]
