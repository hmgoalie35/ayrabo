from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^(?P<coach_pk>\d+)/deactivate', views.DeactivateCoachApiView.as_view(), name='deactivate'),
]
