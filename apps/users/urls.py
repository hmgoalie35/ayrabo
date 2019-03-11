from django.conf.urls import url

from .views import UserDetailView, UserUpdateView


urlpatterns = [
    url(r'^(?P<pk>\d+)/$', UserDetailView.as_view(), name='detail'),
    url(r'^update/$', UserUpdateView.as_view(), name='update'),
]
