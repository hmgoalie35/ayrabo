from django.conf.urls import url, include
from rest_framework.authtoken.views import obtain_auth_token
from . import views

urlpatterns = [
    url(r'^$', views.APIHomeView.as_view(), name='api_home'),

    url('^auth/', include('rest_framework.urls', namespace='rest_framework')),
    url('^token/obtain/$', obtain_auth_token, name='obtain_api_token'),
    url('^token/revoke/$', views.RevokeAuthTokenView.as_view(), name='revoke_api_token'),

    url(r'^v1/', include('api.v1.urls', namespace='v1')),

]
