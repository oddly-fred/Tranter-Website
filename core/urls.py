from django.urls import path
from . import views
 
urlpatterns = [
    path('',                            views.home,           name='home'),
    path('who-we-are/',                 views.who_we_are,     name='who_we_are'),
    path('what-we-do/',                 views.what_we_do,     name='what_we_do'),
    path('what-we-do/<slug:slug>/',     views.service_detail, name='service_detail'),
    path('events/',                     views.events,         name='events'),
    path('events/<slug:slug>/',         views.event_detail,   name='event_detail'),
    path('insights/',                   views.insights,       name='insights'),
    path('insights/<slug:slug>/',       views.insight_detail, name='insight_detail'),
    path('contact/',                    views.contact,        name='contact'),
    path('set-region/',                 views.set_region,     name='set_region'),
    path("book-demo-popup/", views.book_demo_popup, name="book_demo_popup"),
    
]
