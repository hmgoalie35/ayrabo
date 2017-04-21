from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^(?P<referee_pk>\d+)/deactivate', views.DeactivateRefereeApiView.as_view(), name='deactivate'),
]
