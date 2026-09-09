"""
Account URL routes for HRHub Pro.
"""

from django.urls import path

from .views import role_redirect_view


urlpatterns = [
    path("redirect/", role_redirect_view, name="role_redirect"),
]