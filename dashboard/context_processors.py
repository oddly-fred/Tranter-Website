"""
Context processors for dashboard-wide data.
"""

from .models import Signal, Notification


def dashboard_context(request):
    """Add dashboard-wide context data."""
    context = {}
    
    if request.user.is_authenticated:
        # Unread signals count
        context['unread_signals_count'] = Signal.objects.filter(
            recipient=request.user,
            is_read=False
        ).count()
        
        # Unread notifications count
        context['unread_notifications_count'] = Notification.objects.filter(
            user=request.user,
            is_read=False
        ).count()
    
    return context