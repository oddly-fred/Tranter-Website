from django.urls import path
from . import views

urlpatterns = [
    path('', views.integrations, name='integrations'),
]