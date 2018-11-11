from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^(?P<player_pk>\d+)/update/$', views.PlayerUpdateView.as_view(), name='update'),
]
