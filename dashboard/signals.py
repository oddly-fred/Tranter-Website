"""
Signals for automatic activity tracking and notifications.
"""

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone

from .models import Task, LessonProgress, ActivityFeed, Notification, RewardPoints


# ============ TASK SIGNALS ============

@receiver(pre_save, sender=Task)
def task_pre_save(sender, instance, **kwargs):
    """Capture old status before save."""
    if instance.pk:
        try:
            old_instance = Task.objects.get(pk=instance.pk)
            instance._old_status = old_instance.status
            instance._old_assigned_to = old_instance.assigned_to
        except Task.DoesNotExist:
            instance._old_status = None
            instance._old_assigned_to = None
    else:
        instance._old_status = None
        instance._old_assigned_to = None


@receiver(post_save, sender=Task)
def task_post_save(sender, instance, created, **kwargs):
    """Handle task post-save events."""
    
    if created:
        # ✅ Create activity feed entry
        ActivityFeed.objects.create(
            user=instance.created_by,
            action_type='task_created',
            description=f'Created task: {instance.title}',
            related_object_id=instance.pk
        )
        
        # Create notification for assigned user
        if instance.assigned_to and instance.assigned_to != instance.created_by:
            Notification.objects.create(
                user=instance.assigned_to,
                notification_type='task_assigned',
                title='New Task Assigned',
                message=f'You have been assigned to: {instance.title}',
                related_object_id=instance.pk
            )
    
    else:
        old_status = getattr(instance, '_old_status', None)
        
        # Status changed to done
        if old_status != 'done' and instance.status == 'done':
            # ✅ Create activity feed entry
            ActivityFeed.objects.create(
                user=instance.assigned_to or instance.created_by,
                action_type='task_completed',
                description=f'Completed: {instance.title}',
                related_object_id=instance.pk
            )
            
            # Award points
            target_user = instance.assigned_to or instance.created_by
            RewardPoints.award_points(
                user=target_user,
                points=10,
                reason=f'Completed task: {instance.title}'
            )


# ============ LESSON PROGRESS SIGNALS ============

@receiver(post_save, sender=LessonProgress)
def lesson_progress_post_save(sender, instance, created, **kwargs):
    """Handle lesson completion."""
    
    # Only trigger if just marked as completed
    if instance.is_completed and instance.completed_at:
        # Check if we already created an activity for this
        existing = ActivityFeed.objects.filter(
            user=instance.user,
            action_type='lesson_completed',
            related_object_id=instance.lesson.pk
        ).exists()
        
        if not existing:
            # Create activity feed entry
            ActivityFeed.objects.create(
                user=instance.user,
                action_type='lesson_completed',
                description=f'Completed lesson: {instance.lesson.title}',
                related_object_id=instance.lesson.pk
            )
            
            # Award points (if not already awarded)
            RewardPoints.award_points(
                user=instance.user,
                points=5,
                reason=f'Completed lesson: {instance.lesson.title}'
            )