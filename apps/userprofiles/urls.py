from django.conf.urls import url
from .views import CreateUserProfileView, UpdateUserProfileView

urlpatterns = [
    url(r'^create/$', CreateUserProfileView.as_view(), name='create_userprofile'),
    url(r'^edit/$', UpdateUserProfileView.as_view(), name='update_userprofile'),
]
