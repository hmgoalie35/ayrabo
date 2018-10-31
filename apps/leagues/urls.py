from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^(?P<slug>[-\w]+)/$', views.LeagueDetailView.as_view(), name='detail'),
]
