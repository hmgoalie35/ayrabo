from django.conf.urls import include, url

from . import views

urlpatterns = [
    url(r'^$', views.V1View.as_view(), name='v1_home'),
    url(r'^sports/', include('api.v1.sports.urls', namespace='sports')),
    url(r'^teams/', include('api.v1.teams.urls', namespace='teams')),
]
