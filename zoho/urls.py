from django.urls import path
from . import views

app_name = 'zoho'

urlpatterns = [
    path('', views.zoho_home, name='zoho_home'),                  # Zoho home page
    path('<slug:slug>/', views.product_detail, name='product_detail'),
    
]