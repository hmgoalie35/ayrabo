from django.conf.urls import url

from . import views


app_name = 'games'
urlpatterns = [
    url(r'^create/$', views.GameCreateView.as_view(), name='create'),
    url(r'^(?P<pk>\d+)/update/$', views.GameUpdateView.as_view(), name='update'),
]
