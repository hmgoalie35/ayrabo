from django.conf.urls import url

from . import views


app_name = 'players'
urlpatterns = [
    url(r'^$', views.PlayersListAPIView.as_view(), name='list'),
]
