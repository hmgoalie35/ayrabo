from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^(?P<scorekeeper_pk>\d+)/deactivate', views.DeactivateScorekeeperApiView.as_view(), name='deactivate'),
]
