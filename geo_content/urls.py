"""
URL Configuration for Geo Content Module
"""

from django.urls import path
from . import views

app_name = 'geo_content'

urlpatterns = [
    # API endpoints
    path('api/set-region/', views.api_set_region, name='api_set_region'),
    path('api/current-region/', views.get_current_region, name='current_region'),
]
