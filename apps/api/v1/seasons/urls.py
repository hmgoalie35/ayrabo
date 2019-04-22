from django.conf.urls import url

from .views import SeasonRostersListAPIView


season_roster_urls = [
    url(r'^$', SeasonRostersListAPIView.as_view(), name='list'),
]
