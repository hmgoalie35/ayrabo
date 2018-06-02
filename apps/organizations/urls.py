from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^(?P<pk>\d+)/$', views.OrganizationDetailView.as_view(), name='detail'),
]
