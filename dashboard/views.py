import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST
from django.db.models import Q, Count, Sum
from django.contrib import messages

from datetime import timedelta
from django.db import models

from .models import (
    Task, Project, Notification, ActivityFeed,
    RewardPoints, Course, AIActionLog, UserProfile,
    CourseEnrollment, Lesson, LessonProgress,
    Signal, SignalMute, SignalTemplate, QuizCategory,
    DailyQuiz, QuizQuestion, QuizChoice, QuizAttempt,
    QuizAnswer, QuizStreak)

from .forms import LoginForm, RegisterForm, TaskForm
from .services import AIService


# ============ HELPER ============
def get_profile(user):
    """Safely get or create user profile."""
    try:
        return user.profile
    except UserProfile.DoesNotExist:
        return UserProfile.objects.create(
            user=user,
            role='admin' if user.is_superuser else 'staff'
        )


# ============ AUTH VIEWS ============
class CustomLoginView(LoginView):
    form_class = LoginForm
    template_name = 'dashboard/login.html'
    redirect_authenticated_user = True


def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard:index')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create profile immediately
            UserProfile.objects.get_or_create(
                user=user,
                defaults={'role': 'staff'}
            )
            login(request, user)
            return redirect('dashboard:index')
    else:
        form = RegisterForm()
    return render(request, 'dashboard/register.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('dashboard:login')


# ============ DASHBOARD VIEW ============
@login_required
def index(request):
    user = request.user
    profile = get_profile(user)

    # Get tasks based on role
    if profile.is_manager:
        tasks = Task.objects.all()
    else:
        tasks = Task.objects.filter(Q(assigned_to=user) | Q(created_by=user))

    # Stats
    stats = {
        'total': tasks.count(),
        'pending': tasks.filter(status='pending').count(),
        'in_progress': tasks.filter(status='in_progress').count(),
        'done': tasks.filter(status='done').count(),
    }

    # Recent items
    recent_tasks = tasks.order_by('-created_at')[:5]
    notifications = Notification.objects.filter(user=user, is_read=False)[:5]
    activities = ActivityFeed.objects.filter(user=user)[:10]
    points = RewardPoints.get_user_total(user)

    # Leaderboard
    from django.contrib.auth.models import User as AuthUser
    all_users = AuthUser.objects.filter(is_active=True)
    leaderboard = []
    for u in all_users:
        u_profile = get_profile(u)
        total = RewardPoints.get_user_total(u)
        leaderboard.append({
            'user': u,
            'full_name': u_profile.full_name,
            'points': total
        })
    leaderboard.sort(key=lambda x: x['points'], reverse=True)
    leaderboard = leaderboard[:5]

    context = {
        'stats': stats,
        'recent_tasks': recent_tasks,
        'notifications': notifications,
        'activities': activities,
        'points': points,
        'leaderboard': leaderboard,
        'task_form': TaskForm(),
        'profile': profile,
    }
    return render(request, 'dashboard/index.html', context)


# ============ TASK VIEWS ============
@login_required
def task_list(request):
    user = request.user
    profile = get_profile(user)

    if profile.is_manager:
        tasks = Task.objects.all()
    else:
        tasks = Task.objects.filter(Q(assigned_to=user) | Q(created_by=user))

    # Filters
    status = request.GET.get('status')
    priority = request.GET.get('priority')

    if status:
        tasks = tasks.filter(status=status)
    if priority:
        tasks = tasks.filter(priority=priority)

    tasks = tasks.order_by('-created_at')

    context = {'tasks': tasks, 'form': TaskForm()}

    if request.headers.get('HX-Request'):
        return render(request, 'dashboard/partials/task_list.html', context)
    return render(request, 'dashboard/task_list.html', context)


@login_required
def task_detail(request, pk):
    task = get_object_or_404(Task, pk=pk)
    return render(request, 'dashboard/task_detail.html', {'task': task})


@login_required
def task_create(request):
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.created_by = request.user
            task.save()
            messages.success(request, f'✅ Task "{task.title}" created successfully!')
            
            # If using HTMX modal, close and refresh
            if request.headers.get('HX-Request'):
                return HttpResponse(status=204, headers={'HX-Trigger': 'taskCreated'})
            
            return redirect('dashboard:task_list')
        else:
            # If form is invalid and it's HTMX, return the form with errors
            if request.headers.get('HX-Request'):
                return render(request, 'dashboard/task_form_partial.html', {'form': form})
    else:
        form = TaskForm()
        
    return render(request, 'dashboard/task_form.html', {'form': form})




@login_required
@require_POST
def task_update_status(request, pk):
    task = get_object_or_404(Task, pk=pk)
    new_status = request.POST.get('status')

    if new_status in dict(Task.STATUS_CHOICES):
        old_status = task.status
        task.status = new_status
        task.save()

        # Award points on completion
        if new_status == 'done' and old_status != 'done':
            target_user = task.assigned_to or task.created_by
            RewardPoints.award_points(
                target_user, 10, f'Completed: {task.title}'
            )
            ActivityFeed.objects.create(
                user=target_user,
                action_type='task_completed',
                description=f'Completed: {task.title}',
                related_object_id=task.id
            )

    if request.headers.get('HX-Request'):
        return render(request, 'dashboard/partials/task_card.html', {'task': task})
    return JsonResponse({'success': True})


@login_required
@require_POST
def task_delete(request, pk):
    task = get_object_or_404(Task, pk=pk)
    task.delete()

    if request.headers.get('HX-Request'):
        return HttpResponse(status=204)
    return redirect('dashboard:task_list')


# ============ AI VIEWS ============
@login_required
@require_POST
def ai_process(request):
    try:
        data = json.loads(request.body)
        prompt = data.get('prompt', '').strip()

        if not prompt:
            return JsonResponse({
                'success': False,
                'message': 'Please enter a message'
            })

        ai = AIService(request.user)
        result = ai.process_prompt(prompt)

        return JsonResponse(result)
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})


@login_required
def ai_history(request):
    logs = AIActionLog.objects.filter(user=request.user)[:20]
    return render(request, 'dashboard/ai_history.html', {'logs': logs})


# ============ NOTIFICATION VIEWS ============
@login_required
def notification_list(request):
    """Enhanced notification list view"""
    user = request.user
    
    # Get all notifications
    notifications = Notification.objects.filter(user=user).exclude(is_archived=True)
    
    # Stats
    unread_count = notifications.filter(is_read=False).count()
    task_notif_count = notifications.filter(
        notification_type__in=['task_assigned', 'task_completed', 'task_due_soon', 'task_overdue']
    ).count()
    ai_notif_count = notifications.filter(notification_type='ai_action').count()
    learning_notif_count = notifications.filter(
        notification_type__in=['course_assigned', 'lesson_completed']
    ).count()
    
    # Pagination (optional)
    from django.core.paginator import Paginator
    paginator = Paginator(notifications, 50)
    page = request.GET.get('page', 1)
    notifications = paginator.get_page(page)
    
    context = {
        'notifications': notifications,
        'unread_count': unread_count,
        'task_notif_count': task_notif_count,
        'ai_notif_count': ai_notif_count,
        'learning_notif_count': learning_notif_count,
    }
    
    return render(request, 'dashboard/notifications.html', context)


@login_required
@require_POST
def notification_mark_read(request, pk):
    """Mark single notification as read"""
    notification = get_object_or_404(Notification, pk=pk, user=request.user)
    notification.mark_as_read()
    
    if request.headers.get('HX-Request'):
        return HttpResponse(status=204)
    
    return JsonResponse({'success': True})


@login_required
@require_POST
def notification_mark_all_read(request):
    """Mark all notifications as read"""
    Notification.objects.filter(
        user=request.user,
        is_read=False
    ).update(is_read=True, read_at=timezone.now())
    
    if request.headers.get('HX-Request'):
        return HttpResponse(
            status=204,
            headers={'HX-Trigger': 'notificationsUpdated'}
        )
    
    return JsonResponse({'success': True})


@login_required
@require_POST
def notification_delete(request, pk):
    """Delete/archive a notification"""
    notification = get_object_or_404(Notification, pk=pk, user=request.user)
    notification.is_archived = True
    notification.save()
    
    if request.headers.get('HX-Request'):
        return HttpResponse(status=204)
    
    return JsonResponse({'success': True})


# ============ LEARNING VIEWS ============
@login_required
def course_list(request):
    user = request.user
    profile = get_profile(user)
    
    # Get accessible courses
    if profile.is_manager:
        courses = Course.objects.filter(is_published=True)
    else:
        from django.db.models import Q
        courses = Course.objects.filter(
            Q(assigned_to=user) | Q(is_required=True),
            is_published=True
        ).distinct()
    
    # Add progress and enrollment data
    courses_data = []
    for c in courses:
        # Get or create enrollment
        enrollment, _ = CourseEnrollment.objects.get_or_create(
            user=user,
            course=c
        )
        
        courses_data.append({
            'course': c,
            'progress': c.get_user_progress(user),
            'enrollment': enrollment,
        })
    
    return render(request, 'dashboard/courses.html', {
        'courses': courses_data
    })


@login_required
def course_detail(request, pk):
    course = get_object_or_404(Course, pk=pk, is_published=True)
    user = request.user
    profile = get_profile(user)
    
    # Check access
    if not course.can_user_access(user) and not profile.is_manager:
        messages.error(request, "You don't have access to this course.")
        return redirect('dashboard:courses')
    
    # Get or create enrollment
    enrollment, created = CourseEnrollment.objects.get_or_create(
        user=user,
        course=course
    )
    
    # For external courses
    if course.content_type == 'external_link':
        return render(request, 'dashboard/course_external.html', {
            'course': course,
            'enrollment': enrollment,
        })
    
    # For internal/hybrid courses
    lessons = course.lessons.all()
    lessons_with_progress = []
    for lesson in lessons:
        progress, _ = LessonProgress.objects.get_or_create(user=user, lesson=lesson)
        lessons_with_progress.append({
            'lesson': lesson,
            'progress': progress
        })
    
    overall_progress = course.get_user_progress(user)
    
    context = {
        'course': course,
        'lessons': lessons_with_progress,
        'progress': overall_progress,
        'enrollment': enrollment,
    }
    
    return render(request, 'dashboard/course_detail.html', context)

# ============ ENGAGEMENT VIEWS ============
@login_required
def leaderboard(request):
    from django.contrib.auth.models import User
    from django.db.models import Count, Sum

    users = User.objects.filter(is_active=True)
    leaderboard_data = []

    for u in users:
        u_profile = get_profile(u)
        points = RewardPoints.get_user_total(u)
        tasks_completed = Task.objects.filter(
            assigned_to=u,
            status='done'
        ).count()
        
        leaderboard_data.append({
            'user': u,
            'full_name': u_profile.full_name,
            'points': points,
            'role': u_profile.get_role_display(),
            'tasks_completed': tasks_completed,
        })

    # Sort by points descending
    leaderboard_data.sort(key=lambda x: x['points'], reverse=True)
    
    # Calculate stats
    total_points = sum(item['points'] for item in leaderboard_data)
    your_points = RewardPoints.get_user_total(request.user)
    your_rank = next(
        (i + 1 for i, item in enumerate(leaderboard_data) if item['user'].id == request.user.id),
        None
    )

    return render(request, 'dashboard/leaderboard.html', {
        'leaderboard': leaderboard_data,
        'total_points': total_points,
        'your_points': your_points,
        'your_rank': your_rank,
    })


@login_required
def activity_feed(request):
    from django.utils import timezone
    from datetime import timedelta
    from django.db.models import Count

    # Get all activities (ordered by newest)
    activities = ActivityFeed.objects.all().select_related('user', 'user__profile')[:50]
    
    # Today's stats
    today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
    today_activities = ActivityFeed.objects.filter(created_at__gte=today_start)
    
    today_stats = {
        'tasks_completed': today_activities.filter(action_type='task_completed').count(),
        'tasks_created': today_activities.filter(action_type='task_created').count(),
        'lessons_completed': today_activities.filter(action_type='lesson_completed').count(),
        'active_users': today_activities.values('user').distinct().count(),
    }
    
    # Top performers this week
    week_ago = timezone.now() - timedelta(days=7)
    from django.contrib.auth.models import User
    
    users = User.objects.filter(is_active=True)
    top_performers = []
    
    for u in users:
        profile = get_profile(u)
        week_points = RewardPoints.objects.filter(
            user=u,
            created_at__gte=week_ago
        ).aggregate(total=Sum('points'))['total'] or 0
        
        if week_points > 0:
            top_performers.append({
                'user': u,
                'full_name': profile.full_name,
                'points': week_points,
            })
    
    top_performers.sort(key=lambda x: x['points'], reverse=True)
    top_performers = top_performers[:5]
    
    context = {
        'activities': activities,
        'today_stats': today_stats,
        'top_performers': top_performers,
    }
    
    return render(request, 'dashboard/activity_feed.html', context)


def login_view(request):
    """Email-only login view"""
    if request.user.is_authenticated:
        return redirect('dashboard:index')

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = form.cleaned_data['user']
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            messages.success(request, f'Welcome back, {user.first_name or user.email}!')
            return redirect('dashboard:index')
    else:
        form = LoginForm()

    return render(request, 'dashboard/login.html', {'form': form})


def register_view(request):
    """Email-only registration view"""
    if request.user.is_authenticated:
        return redirect('dashboard:index')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()

            # Create user profile
            from .models import UserProfile
            UserProfile.objects.get_or_create(
                user=user,
                defaults={'role': 'staff'}
            )

            # Log user in
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            messages.success(request, 'Account created successfully!')
            return redirect('dashboard:index')
    else:
        form = RegisterForm()

    return render(request, 'dashboard/register.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('dashboard:login')








# ============ PROJECT VIEWS ============

@login_required
def project_list(request):
    """List all projects"""
    user = request.user
    profile = get_profile(user)
    
    if profile.is_manager:
        projects = Project.objects.filter(is_active=True)
    else:
        projects = Project.objects.filter(
            Q(owner=user) | Q(members=user),
            is_active=True
        ).distinct()
    
    # Add stats for each project
    projects_data = []
    for project in projects:
        total_tasks = project.tasks.count()
        completed_tasks = project.tasks.filter(status='done').count()
        progress = int((completed_tasks / total_tasks * 100)) if total_tasks > 0 else 0
        
        projects_data.append({
            'project': project,
            'total_tasks': total_tasks,
            'completed_tasks': completed_tasks,
            'progress': progress,
        })
    
    context = {
        'projects': projects_data,
    }
    
    return render(request, 'dashboard/project_list.html', context)


@login_required
def project_create(request):
    """Create a new project"""
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description', '')
        color = request.POST.get('color', '#048042')
        
        if name:
            project = Project.objects.create(
                name=name,
                description=description,
                color=color,
                owner=request.user
            )
            
            messages.success(request, f'✅ Project "{project.name}" created successfully!')
            
            if request.headers.get('HX-Request'):
                return HttpResponse(status=204, headers={'HX-Trigger': 'projectCreated'})
            
            return redirect('dashboard:project_detail', pk=project.pk)
        else:
            messages.error(request, '❌ Project name is required.')
    
    return render(request, 'dashboard/project_form.html')


@login_required
def project_detail(request, pk):
    """Project detail with tasks"""
    user = request.user
    profile = get_profile(user)
    
    if profile.is_manager:
        project = get_object_or_404(Project, pk=pk)
    else:
        project = get_object_or_404(
            Project,
            Q(owner=user) | Q(members=user),
            pk=pk
        )
    
    # Get tasks for this project
    tasks = project.tasks.all().order_by('-created_at')
    
    # Stats
    total_tasks = tasks.count()
    completed_tasks = tasks.filter(status='done').count()
    pending_tasks = tasks.filter(status='pending').count()
    in_progress_tasks = tasks.filter(status='in_progress').count()
    progress = int((completed_tasks / total_tasks * 100)) if total_tasks > 0 else 0
    
    context = {
        'project': project,
        'tasks': tasks,
        'stats': {
            'total': total_tasks,
            'completed': completed_tasks,
            'pending': pending_tasks,
            'in_progress': in_progress_tasks,
            'progress': progress,
        }
    }
    
    return render(request, 'dashboard/project_detail.html', context)


@login_required
def project_edit(request, pk):
    """Edit project"""
    project = get_object_or_404(Project, pk=pk, owner=request.user)
    
    if request.method == 'POST':
        project.name = request.POST.get('name', project.name)
        project.description = request.POST.get('description', project.description)
        project.color = request.POST.get('color', project.color)
        project.save()
        
        messages.success(request, f'✅ Project "{project.name}" updated!')
        return redirect('dashboard:project_detail', pk=project.pk)
    
    return render(request, 'dashboard/project_form.html', {'project': project})


@login_required
@require_POST
def project_delete(request, pk):
    """Delete/archive project"""
    project = get_object_or_404(Project, pk=pk, owner=request.user)
    project.is_active = False
    project.save()
    
    messages.success(request, f'Project "{project.name}" archived.')
    return redirect('dashboard:project_list')




# ============ SIGNAL SYSTEM - COMPLETE IMPLEMENTATION ============

@login_required
def signal_inbox(request):
    """Signal inbox - view all received signals"""
    user = request.user
    
    # Get received signals
    signals = Signal.objects.filter(recipient=user).select_related(
        'sender', 
        'sender__profile',
        'related_task', 
        'related_project'
    )
    
    # Filter by status
    filter_type = request.GET.get('filter', 'all')
    if filter_type == 'unread':
        signals = signals.filter(is_read=False)
    elif filter_type == 'urgent':
        signals = signals.filter(urgency='urgent')
    elif filter_type == 'pending':
        signals = signals.filter(is_responded=False)
    
    # Stats
    total_signals = Signal.objects.filter(recipient=user).count()
    unread_count = Signal.objects.filter(recipient=user, is_read=False).count()
    urgent_count = Signal.objects.filter(recipient=user, urgency='urgent', is_read=False).count()
    pending_response_count = Signal.objects.filter(recipient=user, is_responded=False, is_read=True).count()
    
    # Pagination
    from django.core.paginator import Paginator
    paginator = Paginator(signals, 20)
    page = request.GET.get('page', 1)
    signals = paginator.get_page(page)
    
    context = {
        'signals': signals,
        'stats': {
            'total': total_signals,
            'unread': unread_count,
            'urgent': urgent_count,
            'pending': pending_response_count,
        },
        'filter_type': filter_type,
    }
    
    return render(request, 'dashboard/signal_inbox.html', context)


@login_required
def signal_sent(request):
    """View sent signals"""
    user = request.user
    
    signals = Signal.objects.filter(sender=user).select_related(
        'recipient',
        'recipient__profile',
        'related_task', 
        'related_project'
    )
    
    # Stats
    sent_count = signals.count()
    responded_count = signals.filter(is_responded=True).count()
    read_count = signals.filter(is_read=True).count()
    
    from django.core.paginator import Paginator
    paginator = Paginator(signals, 20)
    page = request.GET.get('page', 1)
    signals = paginator.get_page(page)
    
    context = {
        'signals': signals,
        'stats': {
            'sent': sent_count,
            'responded': responded_count,
            'read': read_count,
        }
    }
    
    return render(request, 'dashboard/signal_sent.html', context)


@login_required
def signal_send(request):
    """Send a new signal"""
    if request.method == 'POST':
        recipient_id = request.POST.get('recipient')
        signal_type = request.POST.get('signal_type')
        urgency = request.POST.get('urgency', 'normal')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        task_id = request.POST.get('related_task')
        project_id = request.POST.get('related_project')
        
        try:
            recipient = User.objects.get(id=recipient_id)
            
            # Check cooldown
            can_send, msg = Signal.can_send_another(request.user, recipient)
            if not can_send:
                messages.error(request, f'⏳ {msg}')
                if request.headers.get('HX-Request'):
                    return HttpResponse(f'<div class="alert alert-error">{msg}</div>')
                return redirect('dashboard:signal_send')
            
            # Check if recipient has muted sender
            is_muted = SignalMute.objects.filter(
                user=recipient,
                muted_user=request.user
            ).filter(
                models.Q(muted_until__isnull=True) | models.Q(muted_until__gt=timezone.now())
            ).exists()
            
            if is_muted:
                messages.warning(request, '🔇 This user has muted your signals.')
                return redirect('dashboard:signal_inbox')
            
            # Create signal
            signal = Signal.objects.create(
                sender=request.user,
                recipient=recipient,
                signal_type=signal_type,
                urgency=urgency,
                subject=subject,
                message=message,
                related_task_id=task_id if task_id else None,
                related_project_id=project_id if project_id else None,
            )
            
            # Create notification
            Notification.objects.create(
                user=recipient,
                notification_type='signal_received',
                priority=urgency,
                title=f'📡 Signal from {request.user.profile.full_name}',
                message=subject,
                related_object_type='signal',
                related_object_id=signal.id,
                action_url=f'/dashboard/signals/{signal.id}/'
            )
            
            # Award points to sender
            RewardPoints.award_points(
                user=request.user,
                points=3,
                reason=f'Sent signal to {recipient.profile.full_name}'
            )
            
            # Log activity
            ActivityFeed.objects.create(
                user=request.user,
                action_type='signal_sent',
                description=f'Sent signal to {recipient.profile.full_name}: {subject}',
                related_object_id=signal.id
            )
            
            messages.success(request, f'✅ Signal sent to {recipient.profile.full_name}!')
            
            if request.headers.get('HX-Request'):
                return HttpResponse(status=204, headers={'HX-Trigger': 'signalSent'})
            
            return redirect('dashboard:signal_sent')
            
        except User.DoesNotExist:
            messages.error(request, '❌ Recipient not found.')
            return redirect('dashboard:signal_inbox')
        except Exception as e:
            messages.error(request, f'❌ Error: {str(e)}')
            return redirect('dashboard:signal_send')
    
    # GET request - show form
    users = User.objects.filter(is_active=True).exclude(id=request.user.id)
    tasks = Task.objects.filter(
        Q(assigned_to=request.user) | Q(created_by=request.user)
    ).filter(status__in=['pending', 'in_progress'])[:20]
    
    projects = Project.objects.filter(
        Q(owner=request.user) | Q(members=request.user)
    ).distinct()[:20]
    
    context = {
        'users': users,
        'tasks': tasks,
        'projects': projects,
        'signal_types': Signal.SIGNAL_TYPES,
        'urgency_levels': Signal.URGENCY_LEVELS,
    }
    
    return render(request, 'dashboard/signal_send.html', context)


@login_required
def signal_detail(request, pk):
    """View signal detail"""
    signal = get_object_or_404(
        Signal.objects.select_related('sender', 'recipient', 'related_task', 'related_project'),
        Q(sender=request.user) | Q(recipient=request.user),
        pk=pk
    )
    
    # Mark as read if recipient
    if signal.recipient == request.user and not signal.is_read:
        signal.mark_as_read()
    
    context = {
        'signal': signal,
    }
    
    return render(request, 'dashboard/signal_detail.html', context)


@login_required
@require_POST
def signal_respond(request, pk):
    """Respond to a signal"""
    signal = get_object_or_404(Signal, pk=pk, recipient=request.user)
    
    response_text = request.POST.get('response', '').strip()
    reaction = request.POST.get('reaction', '')
    
    if response_text:
        signal.mark_as_responded(response_text)
        
        # Notify sender
        Notification.objects.create(
            user=signal.sender,
            notification_type='signal_received',
            title=f'Response from {request.user.profile.full_name}',
            message=f'Responded to: {signal.subject}',
            related_object_type='signal',
            related_object_id=signal.id,
        )
        
        messages.success(request, '✅ Response sent!')
    
    if reaction:
        signal.reaction = reaction
        signal.save()
        messages.success(request, '✅ Reaction added!')
    
    if request.headers.get('HX-Request'):
        return render(request, 'dashboard/partials/signal_detail.html', {'signal': signal})
    
    return redirect('dashboard:signal_detail', pk=pk)


@login_required
@require_POST
def signal_mark_read(request, pk):
    """Mark signal as read"""
    signal = get_object_or_404(Signal, pk=pk, recipient=request.user)
    signal.mark_as_read()
    
    if request.headers.get('HX-Request'):
        return HttpResponse(status=204)
    
    return JsonResponse({'success': True})


@login_required
@require_POST
def signal_mute_user(request, user_id):
    """Mute signals from a specific user"""
    muted_user = get_object_or_404(User, id=user_id)
    
    if muted_user == request.user:
        messages.error(request, '❌ You cannot mute yourself.')
        return redirect('dashboard:signal_inbox')
    
    duration_hours = int(request.POST.get('duration', 24))
    muted_until = timezone.now() + timedelta(hours=duration_hours)
    
    SignalMute.objects.update_or_create(
        user=request.user,
        muted_user=muted_user,
        defaults={'muted_until': muted_until}
    )
    
    messages.success(request, f'🔇 Muted signals from {muted_user.profile.full_name} for {duration_hours} hours')
    return redirect('dashboard:signal_inbox')


@login_required
def signal_templates(request):
    """Manage signal templates"""
    profile = get_profile(request.user)
    
    # Get templates
    if profile.is_manager:
        templates = SignalTemplate.objects.filter(is_active=True)
    else:
        templates = SignalTemplate.objects.filter(
            Q(created_by=request.user) | Q(created_by__profile__role='admin'),
            is_active=True
        )
    
    context = {
        'templates': templates,
    }
    
    return render(request, 'dashboard/signal_templates.html', context)








    # ============ DAILY QUIZ SYSTEM ============

@login_required
def quiz_home(request):
    """Quiz home page"""
    from django.utils import timezone

    today = timezone.now().date()

    # Get today's quiz
    try:
        today_quiz = DailyQuiz.objects.get(date=today, status='active')
        user_attempted = today_quiz.user_has_attempted(request.user)
        user_attempt = today_quiz.get_user_attempt(request.user)
    except DailyQuiz.DoesNotExist:
        today_quiz = None
        user_attempted = False
        user_attempt = None

    # Get recent quizzes
    recent_quizzes = DailyQuiz.objects.filter(
        status='active'
    ).exclude(date=today).order_by('-date')[:5]

    # Get user streak
    streak, _ = QuizStreak.objects.get_or_create(user=request.user)

    # Get user quiz stats
    total_attempts = QuizAttempt.objects.filter(user=request.user).count()
    passed_attempts = QuizAttempt.objects.filter(user=request.user, passed=True).count()
    total_points = QuizAttempt.objects.filter(
        user=request.user
    ).aggregate(total=Sum('points_earned'))['total'] or 0

    # Leaderboard for quizzes
    from django.db.models import Count
    quiz_leaderboard = QuizAttempt.objects.filter(
        passed=True
    ).values(
        'user__id',
        'user__first_name',
        'user__last_name',
        'user__username'
    ).annotate(
        total_points=Sum('points_earned'),
        total_quizzes=Count('id')
    ).order_by('-total_points')[:5]

    context = {
        'today_quiz': today_quiz,
        'user_attempted': user_attempted,
        'user_attempt': user_attempt,
        'recent_quizzes': recent_quizzes,
        'streak': streak,
        'stats': {
            'total_attempts': total_attempts,
            'passed_attempts': passed_attempts,
            'total_points': total_points,
            'pass_rate': int((passed_attempts / total_attempts * 100)) if total_attempts > 0 else 0,
        },
        'quiz_leaderboard': quiz_leaderboard,
    }

    return render(request, 'dashboard/quiz_home.html', context)


@login_required
def quiz_detail(request, pk):
    """Quiz detail / start quiz"""
    quiz = get_object_or_404(DailyQuiz, pk=pk, status='active')

    # Check if already attempted
    existing_attempt = quiz.get_user_attempt(request.user)
    if existing_attempt and existing_attempt.is_completed:
        messages.info(request, '✅ You have already completed this quiz!')
        return redirect('dashboard:quiz_result', pk=existing_attempt.pk)

    questions = quiz.questions.prefetch_related('choices').all()

    context = {
        'quiz': quiz,
        'questions': questions,
        'time_limit': quiz.time_limit_minutes * 60,
    }

    return render(request, 'dashboard/quiz_detail.html', context)


@login_required
@require_POST
def quiz_submit(request, pk):
    """Submit quiz answers"""
    quiz = get_object_or_404(DailyQuiz, pk=pk, status='active')

    # Check if already attempted
    existing_attempt = quiz.get_user_attempt(request.user)
    if existing_attempt and existing_attempt.is_completed:
        messages.error(request, '❌ You have already completed this quiz!')
        return redirect('dashboard:quiz_result', pk=existing_attempt.pk)

    # Create or get attempt
    attempt, created = QuizAttempt.objects.get_or_create(
        user=request.user,
        quiz=quiz
    )

    # Calculate time taken
    time_taken = int((timezone.now() - attempt.started_at).total_seconds())
    attempt.time_taken_seconds = time_taken

    # Process answers
    questions = quiz.questions.prefetch_related('choices').all()
    total_points = 0
    correct_count = 0
    total_questions = questions.count()

    for question in questions:
        answer_key = f'question_{question.pk}'
        selected_choice_id = request.POST.get(answer_key)

        if selected_choice_id:
            try:
                selected_choice = QuizChoice.objects.get(
                    pk=selected_choice_id,
                    question=question
                )
                is_correct = selected_choice.is_correct
                points_earned = question.points if is_correct else 0

                if is_correct:
                    correct_count += 1
                    total_points += points_earned

                QuizAnswer.objects.create(
                    attempt=attempt,
                    question=question,
                    selected_choice=selected_choice,
                    is_correct=is_correct,
                    points_earned=points_earned
                )
            except QuizChoice.DoesNotExist:
                pass

    # Calculate score
    max_points = sum(q.points for q in questions)
    score = (total_points / max_points * 100) if max_points > 0 else 0
    passed = score >= quiz.passing_score

    # Check if first to complete
    is_first = not QuizAttempt.objects.filter(
        quiz=quiz,
        is_completed=True
    ).exclude(pk=attempt.pk).exists()

    # Award bonus for first place
    if is_first and passed:
        total_points += quiz.bonus_points_first

    # Award base points for passing
    if passed:
        total_points += quiz.points_reward

    attempt.score = score
    attempt.points_earned = total_points
    attempt.passed = passed
    attempt.is_completed = True
    attempt.completed_at = timezone.now()
    attempt.save()

    # Award reward points
    if total_points > 0:
        RewardPoints.award_points(
            user=request.user,
            points=total_points,
            reason=f'Quiz: {quiz.title} ({score:.0f}%)'
        )

    # Update streak
    streak, _ = QuizStreak.objects.get_or_create(user=request.user)
    streak.update_streak()

    # Log activity
    ActivityFeed.objects.create(
        user=request.user,
        action_type='task_completed',
        description=f'Completed quiz: {quiz.title} with {score:.0f}%',
        related_object_id=quiz.pk
    )

    # Create notification
    Notification.objects.create(
        user=request.user,
        notification_type='badge_earned',
        title='Quiz Completed! 🎉',
        message=f'You scored {score:.0f}% on "{quiz.title}" and earned {total_points} points!',
    )

    messages.success(request, f'✅ Quiz completed! You scored {score:.0f}%')
    return redirect('dashboard:quiz_result', pk=attempt.pk)


@login_required
def quiz_result(request, pk):
    """Quiz result page"""
    attempt = get_object_or_404(
        QuizAttempt.objects.select_related('quiz', 'user'),
        pk=pk,
        user=request.user
    )

    answers = attempt.answers.select_related(
        'question',
        'selected_choice',
        'question__correct_answer'
    ).prefetch_related('question__choices').all()

    # Quiz ranking
    ranking = QuizAttempt.objects.filter(
        quiz=attempt.quiz,
        is_completed=True,
        score__gte=attempt.score
    ).count()

    context = {
        'attempt': attempt,
        'answers': answers,
        'ranking': ranking,
    }

    return render(request, 'dashboard/quiz_result.html', context)