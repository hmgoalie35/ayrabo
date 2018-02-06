from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.PlayersListAPIView.as_view(), name='list'),
]
