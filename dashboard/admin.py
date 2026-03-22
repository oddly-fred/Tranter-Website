from django.contrib import admin
from django.contrib.auth.models import User
from .models import (
    UserProfile, Project, Task, SubTask, AIActionLog,
    Notification, ActivityFeed, RewardPoints,
    CourseCategory, Instructor, Course, CourseEnrollment,
    Lesson, LessonProgress, Signal, SignalMute, SignalTemplate,
    QuizCategory, DailyQuiz, QuizQuestion,
    QuizChoice, QuizAttempt, QuizAnswer, QuizStreak
)



# ============ USER PROFILE ============
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'role', 'department', '__str__']
    list_filter = ['role']
    search_fields = ['user__username', 'user__email', 'department']


# Unregister default User admin and keep it simple
try:
    admin.site.unregister(User)
except admin.sites.NotRegistered:
    pass


# ============ PROJECTS ============
@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'owner', 'is_active', 'created_at']
    list_filter = ['is_active']
    search_fields = ['name', 'description']
    filter_horizontal = ['members']


# ============ TASKS ============
@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'status', 'priority', 'assigned_to', 'created_by', 'due_date', 'ai_generated']
    list_filter = ['status', 'priority', 'ai_generated', 'created_at']
    search_fields = ['title', 'description']
    readonly_fields = ['created_by', 'created_at', 'updated_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'status', 'priority')
        }),
        ('Assignment', {
            'fields': ('project', 'assigned_to', 'created_by')
        }),
        ('Dates', {
            'fields': ('due_date', 'completed_at', 'created_at', 'updated_at')
        }),
        ('AI', {
            'fields': ('ai_generated',)
        }),
    )


@admin.register(SubTask)
class SubTaskAdmin(admin.ModelAdmin):
    list_display = ['task', 'title', 'is_completed', 'order']
    list_filter = ['is_completed']
    search_fields = ['title']


# ============ AI ============
@admin.register(AIActionLog)
class AIActionLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'action_type', 'success', 'created_at']
    list_filter = ['action_type', 'success', 'created_at']
    search_fields = ['user__username', 'input_text', 'output_text']
    readonly_fields = ['user', 'action_type', 'input_text', 'output_text', 'success', 'created_at']
    date_hierarchy = 'created_at'


# ============ NOTIFICATIONS ============
@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'title', 'notification_type', 'is_read', 'created_at']
    list_filter = ['notification_type', 'is_read', 'created_at']
    search_fields = ['user__username', 'title', 'message']
    readonly_fields = ['created_at']


# ============ ENGAGEMENT ============
@admin.register(ActivityFeed)
class ActivityFeedAdmin(admin.ModelAdmin):
    list_display = ['user', 'action_type', 'description', 'created_at']
    list_filter = ['action_type', 'created_at']
    search_fields = ['user__username', 'description']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'


@admin.register(RewardPoints)
class RewardPointsAdmin(admin.ModelAdmin):
    list_display = ['user', 'points', 'reason', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'reason']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'


# ============ LEARNING SYSTEM ============

@admin.register(CourseCategory)
class CourseCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'icon', 'order', 'is_active']
    list_editable = ['order', 'is_active']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']


@admin.register(Instructor)
class InstructorAdmin(admin.ModelAdmin):
    list_display = ['user', 'title']
    search_fields = ['user__username', 'user__email', 'title']


class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 1
    fields = ['order', 'title', 'content_type', 'duration_minutes', 'is_preview']
    ordering = ['order']


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'content_type', 'difficulty', 'is_published', 'is_featured', 'lesson_count', 'total_enrollments', 'created_at']
    list_filter = ['is_published', 'is_featured', 'difficulty', 'content_type', 'category', 'created_at']
    search_fields = ['title', 'description', 'short_description']
    filter_horizontal = ['assigned_to', 'prerequisites']
    prepopulated_fields = {'slug': ('title',)}
    inlines = [LessonInline]
    readonly_fields = ['created_at', 'updated_at', 'published_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'short_description', 'description', 'thumbnail', 'intro_video_url')
        }),
        ('Content Type', {
            'fields': ('content_type', 'external_course_url', 'platform_name'),
            'description': 'Choose how this course content is delivered'
        }),
        ('Organization', {
            'fields': ('category', 'instructor', 'difficulty', 'language', 'estimated_hours', 'tags', 'skills_learned')
        }),
        ('Access Control', {
            'fields': ('created_by', 'is_published', 'is_featured', 'is_required', 'assigned_to', 'prerequisites')
        }),
        ('Premium Features', {
            'fields': ('has_certificate', 'certificate_template'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'published_at'),
            'classes': ('collapse',)
        }),
    )

    def save_model(self, request, obj, form, change):
        if not change:  # If creating new object
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(CourseEnrollment)
class CourseEnrollmentAdmin(admin.ModelAdmin):
    list_display = ['user', 'course', 'enrolled_at', 'is_completed', 'rating', 'certificate_issued']
    list_filter = ['is_completed', 'certificate_issued', 'rating', 'enrolled_at']
    search_fields = ['user__username', 'course__title']
    readonly_fields = ['enrolled_at', 'started_at', 'completed_at', 'last_accessed']
    date_hierarchy = 'enrolled_at'
    
    fieldsets = (
        ('Enrollment Info', {
            'fields': ('user', 'course', 'enrolled_at')
        }),
        ('Progress', {
            'fields': ('started_at', 'completed_at', 'is_completed', 'time_spent_minutes', 'last_accessed')
        }),
        ('Certificate', {
            'fields': ('certificate_issued', 'certificate_url')
        }),
        ('Feedback', {
            'fields': ('rating', 'review')
        }),
    )


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ['title', 'course', 'content_type', 'order', 'duration_minutes', 'is_preview']
    list_filter = ['content_type', 'course', 'is_preview', 'created_at']
    search_fields = ['title', 'content']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('course', 'title', 'slug', 'order')
        }),
        ('Content', {
            'fields': ('content_type', 'content', 'video_url', 'video_file', 'downloadable_file', 'external_resource_url')
        }),
        ('Settings', {
            'fields': ('duration_minutes', 'is_preview')
        }),
        ('Additional', {
            'fields': ('notes', 'transcript'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(LessonProgress)
class LessonProgressAdmin(admin.ModelAdmin):
    list_display = ['user', 'lesson', 'is_completed', 'time_spent_minutes', 'bookmarked', 'completed_at']
    list_filter = ['is_completed', 'bookmarked', 'completed_at']
    search_fields = ['user__username', 'lesson__title']
    readonly_fields = ['created_at', 'updated_at', 'completed_at']
    
    fieldsets = (
        ('Basic', {
            'fields': ('user', 'lesson', 'is_completed', 'completed_at')
        }),
        ('Engagement', {
            'fields': ('time_spent_minutes', 'last_position_seconds', 'view_count', 'bookmarked')
        }),
        ('Notes', {
            'fields': ('user_notes',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )





@admin.register(Signal)
class SignalAdmin(admin.ModelAdmin):
    list_display = ['sender', 'recipient', 'signal_type', 'urgency', 'subject', 'is_read', 'is_responded', 'created_at']
    list_filter = ['signal_type', 'urgency', 'is_read', 'is_responded', 'created_at']
    search_fields = ['subject', 'message', 'sender__email', 'recipient__email']
    readonly_fields = ['created_at', 'updated_at', 'read_at', 'responded_at']


@admin.register(SignalMute)
class SignalMuteAdmin(admin.ModelAdmin):
    list_display = ['user', 'muted_user', 'muted_until', 'created_at']
    list_filter = ['created_at']


@admin.register(SignalTemplate)
class SignalTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'signal_type', 'default_urgency', 'is_active', 'created_by']
    list_filter = ['signal_type', 'is_active']





@admin.register(QuizCategory)
class QuizCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'icon', 'is_active']


class QuizChoiceInline(admin.TabularInline):
    model = QuizChoice
    extra = 4
    fields = ['choice_text', 'is_correct', 'order']


class QuizQuestionInline(admin.TabularInline):
    model = QuizQuestion
    extra = 3
    fields = ['question_text', 'question_type', 'points', 'order']


@admin.register(DailyQuiz)
class DailyQuizAdmin(admin.ModelAdmin):
    list_display = ['title', 'date', 'status', 'question_count', 'total_attempts', 'ai_generated']
    list_filter = ['status', 'ai_generated', 'date']
    search_fields = ['title', 'description']
    inlines = [QuizQuestionInline]
    list_editable = ['status']

    fieldsets = (
        ('Basic Info', {
            'fields': ('title', 'description', 'date', 'status', 'category')
        }),
        ('Settings', {
            'fields': ('time_limit_minutes', 'points_reward', 'bonus_points_first', 'passing_score')
        }),
    )

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(QuizQuestion)
class QuizQuestionAdmin(admin.ModelAdmin):
    list_display = ['question_text', 'quiz', 'question_type', 'points', 'order']
    list_filter = ['question_type', 'quiz']
    inlines = [QuizChoiceInline]


@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = ['user', 'quiz', 'score', 'passed', 'points_earned', 'started_at']
    list_filter = ['passed', 'started_at']
    readonly_fields = ['started_at', 'completed_at', 'time_taken_seconds']


@admin.register(QuizStreak)
class QuizStreakAdmin(admin.ModelAdmin):
    list_display = ['user', 'current_streak', 'longest_streak', 'total_quizzes_completed']