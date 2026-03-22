"""
URL Configuration for Geo Content Module
"""

from django.urls import path
from . import views

app_name = 'geo_content'

urlpatterns = [
    # Region switch endpoint (GET/POST)
    path('set-region/', views.set_region, name='set_region'),

    # API endpoints
    path('api/set-region/', views.api_set_region, name='api_set_region'),
    path('api/current-region/', views.get_current_region, name='current_region'),

    # Example homepage
    path('', views.homepage, name='homepage'),
]
