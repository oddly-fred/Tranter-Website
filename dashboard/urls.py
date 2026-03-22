from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    # Auth - Use function-based views
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    
    # Dashboard
    path('', views.index, name='index'),


    # Projects (NEW)
    path('projects/', views.project_list, name='project_list'),
    path('projects/create/', views.project_create, name='project_create'),
    path('projects/<int:pk>/', views.project_detail, name='project_detail'),
    path('projects/<int:pk>/edit/', views.project_edit, name='project_edit'),
    path('projects/<int:pk>/delete/', views.project_delete, name='project_delete'),


    
    # Tasks
    path('tasks/', views.task_list, name='task_list'),
    path('tasks/create/', views.task_create, name='task_create'),
    path('tasks/<int:pk>/', views.task_detail, name='task_detail'),
    path('tasks/<int:pk>/status/', views.task_update_status, name='task_status'),
    path('tasks/<int:pk>/delete/', views.task_delete, name='task_delete'),
    
    # AI
    path('ai/process/', views.ai_process, name='ai_process'),
    path('ai/history/', views.ai_history, name='ai_history'),
    
    # Notifications
    path('notifications/', views.notification_list, name='notifications'),
    path('notifications/<int:pk>/read/', views.notification_mark_read, name='notification_read'),
    path('notifications/read-all/', views.notification_mark_all_read, name='notification_read_all'),
    
    # Learning
    path('courses/', views.course_list, name='courses'),
    
    # Engagement
    path('leaderboard/', views.leaderboard, name='leaderboard'),
    path('activity/', views.activity_feed, name='activity'),

    
    # Signals
    path('signals/', views.signal_inbox, name='signal_inbox'),
    path('signals/sent/', views.signal_sent, name='signal_sent'),
    path('signals/send/', views.signal_send, name='signal_send'),
    path('signals/<int:pk>/', views.signal_detail, name='signal_detail'),
    path('signals/<int:pk>/respond/', views.signal_respond, name='signal_respond'),
    path('signals/<int:pk>/read/', views.signal_mark_read, name='signal_mark_read'),
    path('signals/mute/<int:user_id>/', views.signal_mute_user, name='signal_mute_user'),
    path('signals/templates/', views.signal_templates, name='signal_templates'),


    # Quiz System
    path('quiz/', views.quiz_home, name='quiz_home'),
    path('quiz/<int:pk>/', views.quiz_detail, name='quiz_detail'),
    path('quiz/<int:pk>/submit/', views.quiz_submit, name='quiz_submit'),
    path('quiz/result/<int:pk>/', views.quiz_result, name='quiz_result'),
]