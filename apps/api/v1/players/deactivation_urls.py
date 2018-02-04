from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^(?P<player_pk>\d+)/deactivate/$', views.DeactivatePlayerApiView.as_view(), name='deactivate'),
]
