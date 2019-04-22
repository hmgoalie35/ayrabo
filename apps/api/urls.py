from django.conf.urls import url
from django.urls import include
from rest_framework.authtoken.views import obtain_auth_token

from . import views


urlpatterns = [
    url('^auth/', include('rest_framework.urls')),
    url('^token/obtain/$', obtain_auth_token, name='obtain_api_token'),
    url('^token/revoke/$', views.RevokeAuthTokenView.as_view(), name='revoke_api_token'),

    url(r'^v1/', include('api.v1.urls')),
]
