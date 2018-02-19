from django.conf.urls import url, include

from . import views

urlpatterns = [
    url(r'^$', views.V1View.as_view(), name='v1_home'),
    url(r'^', include('api.v1.sports.urls')),
    url(r'^teams/', include('api.v1.teams.urls', namespace='teams')),
]
