from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^create/$', views.CreateCoachesView.as_view(), name='create'),
    url(r'^(?P<coach_pk>\d+)/update/$', views.UpdateCoachView.as_view(), name='update'),
]
