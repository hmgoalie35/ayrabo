from django.conf.urls import url

from . import views


app_name = 'organizations'
urlpatterns = [
    url(r'^(?P<pk>\d+)/$', views.OrganizationDetailView.as_view(), name='detail'),
]
