from django.conf.urls import url
from .views import CreateUserProfileView

urlpatterns = [
    url(r'^create/$', CreateUserProfileView.as_view(), name='create_userprofile'),
]
