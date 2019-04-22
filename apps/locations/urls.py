from django.conf.urls import url

from . import views


app_name = 'locations'
urlpatterns = [
    url(r'^(?P<slug>[-\w]+)/$', views.LocationDetailView.as_view(), name='detail'),
]
