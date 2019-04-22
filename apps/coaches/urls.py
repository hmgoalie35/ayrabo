from django.conf.urls import url

from . import views


app_name = 'coaches'
urlpatterns = [
    url(r'^(?P<coach_pk>\d+)/update/$', views.CoachesUpdateView.as_view(), name='update'),
]
