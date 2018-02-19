from django.conf.urls import url

from .views import SeasonRostersListAPIView

urlpatterns = [
    url(r'^$', SeasonRostersListAPIView.as_view(), name='list'),
]
