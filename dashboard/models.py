from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.core.validators import FileExtensionValidator


# ============ USER PROFILE ============
class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('manager', 'Manager'),
        ('editor', 'Editor'),
        ('staff', 'Staff'),
        ('intern', 'Intern'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='staff')
    department = models.CharField(max_length=100, blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.role}"

    @property
    def is_admin_user(self):
        return self.role == 'admin' or self.user.is_superuser

    @property
    def is_manager(self):
        return self.role in ['admin', 'manager'] or self.user.is_superuser

    @property
    def is_editor(self):
        return self.role in ['admin', 'manager', 'editor'] or self.user.is_superuser

    @property
    def full_name(self):
        name = f"{self.user.first_name} {self.user.last_name}".strip()
        return name if name else self.user.username


@receiver(post_save, sender=User)
def create_or_update_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.get_or_create(
            user=instance,
            defaults={'role': 'admin' if instance.is_superuser else 'staff'}
        )


# ============ PROJECT ============
class Project(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    color = models.CharField(max_length=7, default='#048042')
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_projects')
    members = models.ManyToManyField(User, related_name='projects', blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


# ============ TASK ============
class Task(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('review', 'In Review'),
        ('done', 'Done'),
    ]
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]

    title = models.CharField(max_length=300)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    project = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True, blank=True, related_name='tasks')
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_tasks')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_tasks')
    due_date = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    ai_generated = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    @property
    def is_overdue(self):
        if self.due_date and self.status != 'done':
            return timezone.now() > self.due_date
        return False

    def save(self, *args, **kwargs):
        if self.status == 'done' and not self.completed_at:
            self.completed_at = timezone.now()
        elif self.status != 'done':
            self.completed_at = None
        super().save(*args, **kwargs)


# ============ SUBTASK ============
class SubTask(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='subtasks')
    title = models.CharField(max_length=200)
    is_completed = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title


# ============ AI ACTION LOG ============
class AIActionLog(models.Model):
    ACTION_TYPES = [
        ('task_create', 'Task Creation'),
        ('task_suggest', 'Task Suggestion'),
        ('summary', 'Activity Summary'),
        ('email_draft', 'Email Draft'),
        ('general', 'General Query'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ai_actions')
    action_type = models.CharField(max_length=30, choices=ACTION_TYPES)
    input_text = models.TextField()
    output_text = models.TextField()
    success = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.action_type}"


# ============ ENHANCED NOTIFICATION SYSTEM ============
class Notification(models.Model):
    TYPE_CHOICES = [
        ('task_assigned', 'Task Assigned'),
        ('task_completed', 'Task Completed'),
        ('task_due_soon', 'Task Due Soon'),
        ('task_overdue', 'Task Overdue'),
        ('comment_added', 'Comment Added'),
        ('ai_action', 'AI Action'),
        ('course_assigned', 'Course Assigned'),
        ('lesson_completed', 'Lesson Completed'),
        ('badge_earned', 'Badge Earned'),
        ('signal_received', 'Signal Received'),  # New
        ('mention', 'Mentioned You'),  # New
        ('system', 'System'),
    ]

    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('normal', 'Normal'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=30, choices=TYPE_CHOICES, default='system')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='normal')
    title = models.CharField(max_length=200)
    message = models.TextField()
    
    # Status
    is_read = models.BooleanField(default=False)
    is_archived = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    
    # Related objects
    related_object_type = models.CharField(max_length=50, blank=True)
    related_object_id = models.PositiveIntegerField(null=True, blank=True)
    action_url = models.CharField(max_length=500, blank=True)
    
    # Additional data
    metadata = models.JSONField(default=dict, blank=True)  # For extra context
    
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)  # For temporary notifications

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_read', 'created_at']),
            models.Index(fields=['notification_type']),
            models.Index(fields=['priority']),
        ]

    def __str__(self):
        return f"{self.notification_type}: {self.title}"

    @property
    def icon(self):
        icons = {
            'task_assigned': '📋',
            'task_completed': '✅',
            'task_due_soon': '⏰',
            'task_overdue': '🚨',
            'comment_added': '💬',
            'ai_action': '🤖',
            'course_assigned': '📚',
            'lesson_completed': '🎓',
            'badge_earned': '🏆',
            'signal_received': '📡',
            'mention': '👤',
            'system': 'ℹ️',
        }
        return icons.get(self.notification_type, 'ℹ️')

    @property
    def color_class(self):
        """Return CSS class based on notification type and priority"""
        if self.priority == 'urgent':
            return 'notif-urgent'
        elif self.priority == 'high':
            return 'notif-high'
        elif self.notification_type == 'task_completed':
            return 'notif-success'
        elif self.notification_type in ['task_overdue', 'task_due_soon']:
            return 'notif-warning'
        return 'notif-normal'

    def mark_as_read(self):
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save()

    def get_action_url(self):
        """Get or generate action URL"""
        if self.action_url:
            return self.action_url
        
        if self.related_object_type == 'task' and self.related_object_id:
            return f'/dashboard/tasks/{self.related_object_id}/'
        elif self.related_object_type == 'course' and self.related_object_id:
            return f'/dashboard/courses/{self.related_object_id}/'
        
        return '#'


class NotificationPreference(models.Model):
    """User notification preferences"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='notification_preferences')
    
    # Email notifications
    email_task_assigned = models.BooleanField(default=True)
    email_task_due_soon = models.BooleanField(default=True)
    email_mentions = models.BooleanField(default=True)
    email_daily_digest = models.BooleanField(default=False)
    
    # Push notifications (for future web push)
    push_enabled = models.BooleanField(default=True)
    push_task_assigned = models.BooleanField(default=True)
    push_signals = models.BooleanField(default=True)
    
    # In-app settings
    sound_enabled = models.BooleanField(default=True)
    desktop_notifications = models.BooleanField(default=True)
    
    # Quiet hours
    quiet_hours_enabled = models.BooleanField(default=False)
    quiet_hours_start = models.TimeField(null=True, blank=True)
    quiet_hours_end = models.TimeField(null=True, blank=True)
    
    # Frequency
    digest_frequency = models.CharField(
        max_length=20,
        choices=[
            ('none', 'Never'),
            ('daily', 'Daily'),
            ('weekly', 'Weekly'),
        ],
        default='none'
    )
    
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Preferences for {self.user.email}"


# Signal to create preferences for new users
@receiver(post_save, sender=User)
def create_notification_preferences(sender, instance, created, **kwargs):
    if created:
        NotificationPreference.objects.get_or_create(user=instance)


# ============ ACTIVITY FEED ============
class ActivityFeed(models.Model):
    ACTION_TYPES = [
        ('task_created', 'Task Created'),
        ('task_completed', 'Task Completed'),
        ('login', 'User Login'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activities')
    action_type = models.CharField(max_length=30, choices=ACTION_TYPES)
    description = models.CharField(max_length=255)
    related_object_id = models.PositiveIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.description


# ============ REWARD POINTS ============
class RewardPoints(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reward_points')
    points = models.IntegerField()
    reason = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} +{self.points}"

    @classmethod
    def award_points(cls, user, points, reason):
        return cls.objects.create(user=user, points=points, reason=reason)

    @classmethod
    def get_user_total(cls, user):
        total = cls.objects.filter(user=user).aggregate(total=models.Sum('points'))['total']
        return total or 0


# ============ LEARNING MODELS ============

# Course Category
class CourseCategory(models.Model):
    name = models.CharField(max_length=100)
    icon = models.CharField(max_length=10, default='📚')
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = "Course Categories"
        ordering = ['order', 'name']

    def __str__(self):
        return f"{self.icon} {self.name}"


# Instructor
class Instructor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='instructor_profile')
    bio = models.TextField(blank=True)
    title = models.CharField(max_length=200, blank=True)
    linkedin_url = models.URLField(blank=True)
    website = models.URLField(blank=True)
    avatar = models.ImageField(upload_to='instructors/', null=True, blank=True)

    def __str__(self):
        return self.user.get_full_name() or self.user.username


# Course
class Course(models.Model):
    CONTENT_TYPE_CHOICES = [
        ('internal', 'Internal Content'),
        ('external_link', 'External Link (Udemy, Coursera, etc.)'),
        ('hybrid', 'Hybrid (Mix of Both)'),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField()
    short_description = models.CharField(max_length=300, blank=True)
    thumbnail = models.ImageField(upload_to='course_thumbnails/', null=True, blank=True)
    intro_video_url = models.URLField(blank=True)

    content_type = models.CharField(max_length=20, choices=CONTENT_TYPE_CHOICES, default='internal')
    external_course_url = models.URLField(blank=True)
    platform_name = models.CharField(max_length=100, blank=True)

    category = models.ForeignKey(CourseCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='courses')
    instructor = models.ForeignKey(Instructor, on_delete=models.SET_NULL, null=True, blank=True, related_name='courses')

    difficulty = models.CharField(max_length=20, choices=[
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ], default='beginner')

    estimated_hours = models.DecimalField(max_digits=5, decimal_places=1, default=1.0)
    language = models.CharField(max_length=50, default='English')

    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_courses')
    assigned_to = models.ManyToManyField(User, related_name='assigned_courses', blank=True)
    is_published = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    is_required = models.BooleanField(default=False)

    has_certificate = models.BooleanField(default=False)
    certificate_template = models.FileField(upload_to='certificates/', null=True, blank=True)
    prerequisites = models.ManyToManyField('self', symmetrical=False, blank=True, related_name='unlocks')

    tags = models.JSONField(default=list, blank=True)
    skills_learned = models.JSONField(default=list, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils.text import slugify
            self.slug = slugify(self.title)
        if self.is_published and not self.published_at:
            self.published_at = timezone.now()
        super().save(*args, **kwargs)

    @property
    def lesson_count(self):
        return self.lessons.count()

    @property
    def total_enrollments(self):
        return CourseEnrollment.objects.filter(course=self).count()

    def get_user_progress(self, user):
        if self.content_type == 'external_link':
            try:
                enrollment = CourseEnrollment.objects.get(course=self, user=user)
                return 100 if enrollment.is_completed else 0
            except CourseEnrollment.DoesNotExist:
                return 0

        total = self.lesson_count
        if total == 0:
            return 0

        completed = LessonProgress.objects.filter(
            lesson__course=self, user=user, is_completed=True
        ).count()
        return int((completed / total) * 100)

    def can_user_access(self, user):
        if not self.is_published:
            return False
        if self.is_required:
            return True
        return user in self.assigned_to.all()


# Course Enrollment
class CourseEnrollment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='course_enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    enrolled_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    is_completed = models.BooleanField(default=False)
    certificate_issued = models.BooleanField(default=False)
    certificate_url = models.URLField(blank=True)
    last_accessed = models.DateTimeField(auto_now=True)
    time_spent_minutes = models.PositiveIntegerField(default=0)
    rating = models.PositiveIntegerField(null=True, blank=True, choices=[(i, i) for i in range(1, 6)])
    review = models.TextField(blank=True)

    class Meta:
        unique_together = ['user', 'course']
        ordering = ['-enrolled_at']

    def __str__(self):
        return f"{self.user.username} - {self.course.title}"

    def mark_started(self):
        if not self.started_at:
            self.started_at = timezone.now()
            self.save()

    def mark_completed(self):
        if not self.is_completed:
            self.is_completed = True
            self.completed_at = timezone.now()
            self.save()


# Lesson
class Lesson(models.Model):
    CONTENT_TYPE_CHOICES = [
        ('video', 'Video'),
        ('text', 'Text/Article'),
        ('quiz', 'Quiz'),
        ('exercise', 'Coding Exercise'),
        ('file', 'Downloadable File'),
        ('external', 'External Resource'),
    ]

    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=200)
    slug = models.SlugField(blank=True)
    content_type = models.CharField(max_length=20, choices=CONTENT_TYPE_CHOICES, default='text')
    content = models.TextField(blank=True)
    video_url = models.URLField(blank=True)
    video_file = models.FileField(upload_to='lesson_videos/', null=True, blank=True)
    downloadable_file = models.FileField(upload_to='lesson_files/', null=True, blank=True)
    external_resource_url = models.URLField(blank=True)
    duration_minutes = models.PositiveIntegerField(default=10)
    order = models.PositiveIntegerField(default=0)
    is_preview = models.BooleanField(default=False)
    notes = models.TextField(blank=True)
    transcript = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', 'created_at']
        unique_together = ['course', 'order']

    def __str__(self):
        return f"{self.course.title} - {self.title}"

    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils.text import slugify
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)


# Lesson Progress
class LessonProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='lesson_progress')
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='user_progress')
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    time_spent_minutes = models.PositiveIntegerField(default=0)
    last_position_seconds = models.PositiveIntegerField(default=0)
    view_count = models.PositiveIntegerField(default=0)
    user_notes = models.TextField(blank=True)
    bookmarked = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['user', 'lesson']

    def __str__(self):
        return f"{self.user.username} - {self.lesson.title}"

    def mark_complete(self):
        if not self.is_completed:
            self.is_completed = True
            self.completed_at = timezone.now()
            self.save()

            enrollment, _ = CourseEnrollment.objects.get_or_create(
                user=self.user,
                course=self.lesson.course
            )
            enrollment.mark_started()

            RewardPoints.award_points(self.user, 5, f'Completed lesson: {self.lesson.title}')




class Badge(models.Model):
    """Achievement badges"""
    name = models.CharField(max_length=100)
    description = models.TextField()
    icon = models.CharField(max_length=10, default='🏆')
    points_required = models.PositiveIntegerField(default=0)
    color = models.CharField(max_length=7, default='#048042')
    
    def __str__(self):
        return f"{self.icon} {self.name}"


class UserBadge(models.Model):
    """Track user badges"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='badges')
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE)
    earned_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'badge']




# ============ SIGNAL SYSTEM ============

class Signal(models.Model):
    """
    Intelligent notification system for team communication.
    Replaces ad-hoc messaging with structured, purposeful nudges.
    """
    
    SIGNAL_TYPES = [
        ('task_request', '📋 Task Request'),
        ('reminder', '⏰ Reminder'),
        ('priority', '🔥 Priority Alert'),
        ('attention', '👀 Needs Attention'),
        ('help_needed', '🆘 Help Needed'),
        ('question', '❓ Question'),
        ('update', '📢 Update'),
        ('acknowledgment', '✅ Acknowledgment'),
    ]
    
    URGENCY_LEVELS = [
        ('low', 'Low - When you have time'),
        ('normal', 'Normal - Today'),
        ('high', 'High - Next few hours'),
        ('urgent', 'Urgent - ASAP'),
    ]
    
    # Core fields
    sender = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='sent_signals'
    )
    recipient = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='received_signals'
    )
    signal_type = models.CharField(max_length=30, choices=SIGNAL_TYPES)
    urgency = models.CharField(max_length=10, choices=URGENCY_LEVELS, default='normal')
    
    # Content
    subject = models.CharField(max_length=200)
    message = models.TextField()
    
    # Context linking
    related_task = models.ForeignKey(
        'Task',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='signals'
    )
    related_project = models.ForeignKey(
        'Project',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='signals'
    )
    
    # Status tracking
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    is_responded = models.BooleanField(default=False)
    responded_at = models.DateTimeField(null=True, blank=True)
    response_text = models.TextField(blank=True)
    
    # Anti-spam
    is_muted = models.BooleanField(default=False)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    # Engagement tracking
    reaction = models.CharField(
        max_length=20,
        blank=True,
        choices=[
            ('👍', 'Thumbs Up'),
            ('👎', 'Thumbs Down'),
            ('❤️', 'Love'),
            ('🔥', 'Fire'),
            ('✅', 'Done'),
        ]
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient', 'is_read']),
            models.Index(fields=['sender', 'created_at']),
            models.Index(fields=['signal_type', 'urgency']),
        ]
    
    def __str__(self):
        return f"{self.get_signal_type_display()} from {self.sender} to {self.recipient}"
    
    @property
    def icon(self):
        """Get icon for signal type"""
        icons = {
            'task_request': '📋',
            'reminder': '⏰',
            'priority': '🔥',
            'attention': '👀',
            'help_needed': '🆘',
            'question': '❓',
            'update': '📢',
            'acknowledgment': '✅',
        }
        return icons.get(self.signal_type, '📡')
    
    @property
    def urgency_color(self):
        """Get color for urgency level"""
        colors = {
            'low': '#6b7280',
            'normal': '#3b82f6',
            'high': '#f59e0b',
            'urgent': '#ef4444',
        }
        return colors.get(self.urgency, '#3b82f6')
    
    def mark_as_read(self):
        """Mark signal as read"""
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save()
            
            # Award points to recipient for reading
            RewardPoints.award_points(
                user=self.recipient,
                points=1,
                reason=f'Read signal from {self.sender.get_full_name()}'
            )
    
    def mark_as_responded(self, response_text=''):
        """Mark signal as responded"""
        if not self.is_responded:
            self.is_responded = True
            self.responded_at = timezone.now()
            self.response_text = response_text
            self.save()
            
            # Award points to recipient for responding
            RewardPoints.award_points(
                user=self.recipient,
                points=5,
                reason=f'Responded to signal from {self.sender.get_full_name()}'
            )
            
            # Award points to sender for getting response
            RewardPoints.award_points(
                user=self.sender,
                points=2,
                reason=f'Signal answered by {self.recipient.get_full_name()}'
            )
    
    def can_send_another(sender, recipient):
        """Check if sender can send another signal to recipient (anti-spam)"""
        from datetime import timedelta
        
        cooldown_period = timedelta(minutes=5)
        last_signal = Signal.objects.filter(
            sender=sender,
            recipient=recipient
        ).first()
        
        if last_signal:
            time_since_last = timezone.now() - last_signal.created_at
            if time_since_last < cooldown_period:
                return False, f"Please wait {int((cooldown_period - time_since_last).seconds / 60)} minutes"
        
        return True, "OK"


class SignalTemplate(models.Model):
    """Pre-defined signal templates for quick sending"""
    
    name = models.CharField(max_length=100)
    signal_type = models.CharField(max_length=30, choices=Signal.SIGNAL_TYPES)
    subject_template = models.CharField(max_length=200)
    message_template = models.TextField()
    default_urgency = models.CharField(max_length=10, choices=Signal.URGENCY_LEVELS)
    is_active = models.BooleanField(default=True)
    
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='created_signal_templates'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name


class SignalMute(models.Model):
    """User preferences for muting signals from specific users"""
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='signal_mutes'
    )
    muted_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='muted_by'
    )
    reason = models.CharField(max_length=200, blank=True)
    muted_until = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'muted_user']
    
    def __str__(self):
        return f"{self.user} muted {self.muted_user}"
    
    @property
    def is_active(self):
        """Check if mute is still active"""
        if self.muted_until:
            return timezone.now() < self.muted_until
        return True
    





    # ============ DAILY QUIZ SYSTEM ============

class QuizCategory(models.Model):
    """Quiz categories"""
    name = models.CharField(max_length=100)
    icon = models.CharField(max_length=10, default='🧠')
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = 'Quiz Categories'
        ordering = ['name']

    def __str__(self):
        return f"{self.icon} {self.name}"


class DailyQuiz(models.Model):
    """Daily quiz container"""

    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('expired', 'Expired'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    category = models.ForeignKey(
        QuizCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    date = models.DateField(unique=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')

    # Settings
    time_limit_minutes = models.PositiveIntegerField(default=10)
    points_reward = models.PositiveIntegerField(default=20)
    bonus_points_first = models.PositiveIntegerField(default=10)
    passing_score = models.PositiveIntegerField(default=70)

    # AI Generated
    ai_generated = models.BooleanField(default=False)

    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='created_quizzes'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']
        verbose_name_plural = 'Daily Quizzes'

    def __str__(self):
        return f"Quiz: {self.title} ({self.date})"

    @property
    def question_count(self):
        return self.questions.count()

    @property
    def total_attempts(self):
        return self.attempts.count()

    @property
    def is_today(self):
        from django.utils import timezone
        return self.date == timezone.now().date()

    def user_has_attempted(self, user):
        return self.attempts.filter(user=user).exists()

    def get_user_attempt(self, user):
        return self.attempts.filter(user=user).first()


class QuizQuestion(models.Model):
    """Quiz questions"""

    QUESTION_TYPES = [
        ('multiple_choice', 'Multiple Choice'),
        ('true_false', 'True / False'),
        ('text', 'Short Answer'),
    ]

    quiz = models.ForeignKey(
        DailyQuiz,
        on_delete=models.CASCADE,
        related_name='questions'
    )
    question_type = models.CharField(
        max_length=20,
        choices=QUESTION_TYPES,
        default='multiple_choice'
    )
    question_text = models.TextField()
    explanation = models.TextField(blank=True)
    points = models.PositiveIntegerField(default=10)
    order = models.PositiveIntegerField(default=0)
    image_url = models.URLField(blank=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.question_text[:80]

    @property
    def correct_answer(self):
        return self.choices.filter(is_correct=True).first()


class QuizChoice(models.Model):
    """Answer choices for quiz questions"""

    question = models.ForeignKey(
        QuizQuestion,
        on_delete=models.CASCADE,
        related_name='choices'
    )
    choice_text = models.CharField(max_length=300)
    is_correct = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.choice_text} ({'✓' if self.is_correct else '✗'})"


class QuizAttempt(models.Model):
    """User quiz attempts"""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='quiz_attempts'
    )
    quiz = models.ForeignKey(
        DailyQuiz,
        on_delete=models.CASCADE,
        related_name='attempts'
    )

    # Results
    score = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    points_earned = models.PositiveIntegerField(default=0)
    passed = models.BooleanField(default=False)
    is_completed = models.BooleanField(default=False)

    # Timing
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    time_taken_seconds = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        unique_together = ['user', 'quiz']
        ordering = ['-started_at']

    def __str__(self):
        return f"{self.user.username} - {self.quiz.title} ({self.score}%)"

    @property
    def time_taken_display(self):
        if self.time_taken_seconds:
            minutes = self.time_taken_seconds // 60
            seconds = self.time_taken_seconds % 60
            return f"{minutes}m {seconds}s"
        return "N/A"


class QuizAnswer(models.Model):
    """Individual question answers within an attempt"""

    attempt = models.ForeignKey(
        QuizAttempt,
        on_delete=models.CASCADE,
        related_name='answers'
    )
    question = models.ForeignKey(
        QuizQuestion,
        on_delete=models.CASCADE
    )
    selected_choice = models.ForeignKey(
        QuizChoice,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    text_answer = models.TextField(blank=True)
    is_correct = models.BooleanField(default=False)
    points_earned = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"Answer: {self.question.question_text[:40]}"


class QuizStreak(models.Model):
    """Track daily quiz streaks"""

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='quiz_streak'
    )
    current_streak = models.PositiveIntegerField(default=0)
    longest_streak = models.PositiveIntegerField(default=0)
    last_quiz_date = models.DateField(null=True, blank=True)
    total_quizzes_completed = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.user.username} - {self.current_streak} day streak"

    def update_streak(self):
        """Update streak after completing a quiz"""
        from django.utils import timezone
        today = timezone.now().date()
        yesterday = today - timedelta(days=1)

        if self.last_quiz_date == yesterday:
            self.current_streak += 1
        elif self.last_quiz_date == today:
            pass
        else:
            self.current_streak = 1

        if self.current_streak > self.longest_streak:
            self.longest_streak = self.current_streak

        self.last_quiz_date = today
        self.total_quizzes_completed += 1
        self.save()