from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('contact/', views.contact, name='contact'),
    path('consultation/submit/', views.consultation_submit, name='consultation_submit'),
    path('service/<slug:slug>/', views.service_detail, name='service_detail'),
    path('manage-engine/', views.manage_engine, name='manage_engine'),
    path('services/', views.services, name='services'),
    path('book-demo/', views.book_demo, name='book_demo'),
    path('zoho-solutions/', views.zoho_solutions, name='zoho_solutions'),
    path('sector/<slug:slug>/', views.sector_detail, name='sector_detail'),
    # Events
    path('events/', views.events, name='events'),
    path('events/<slug:slug>/', views.event_detail, name='event_detail'),
    # Insights
    path('insights/', views.insights, name='insights'),
    path('insights/<slug:slug>/', views.insight_detail, name='insight_detail'),
    # Additional pages
    path('who-we-are/', views.who_we_are, name='who_we_are'),
    path('how-we-work/', views.how_we_work, name='how_we_work'),
    path('global-reach/', views.global_reach, name='global_reach'),
    path('sectors/', views.sectors, name='sectors'),
    path('careers/', views.careers, name='careers'),
    path('global-offices/', views.global_offices, name='global_offices'),
    path('partner/', views.partner, name='partner'),
    path('support/', views.support, name='support'),
    path('privacy/', views.privacy, name='privacy'),
    path('terms/', views.terms, name='terms'),
    path('iso-certs/', views.iso_certs, name='iso_certs'),
]