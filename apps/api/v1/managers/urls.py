from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^(?P<manager_pk>\d+)/deactivate/$', views.DeactivateManagerApiView.as_view(), name='deactivate'),
]
