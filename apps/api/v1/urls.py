from django.conf.urls import include, url

urlpatterns = [
    url(r'^sports/', include('api.v1.sports.urls', namespace='sports')),
    url(r'^teams/', include('api.v1.teams.urls', namespace='teams')),
]
