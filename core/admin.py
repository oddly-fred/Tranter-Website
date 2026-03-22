from django.contrib import admin
from django.utils.html import format_html
from .models import Event, EventCategory, EventGalleryImage, EventSpeaker, EventTestimonial, InsightCategory, Insight, InsightTag

class EventGalleryInline(admin.TabularInline):
    model   = EventGalleryImage
    extra   = 3
    fields  = ['image', 'caption', 'size', 'order']


class EventSpeakerInline(admin.TabularInline):
    model  = EventSpeaker
    extra  = 2
    fields = ['name', 'role', 'photo', 'order']


class EventTestimonialInline(admin.TabularInline):
    model  = EventTestimonial
    extra  = 1
    fields = ['name', 'role', 'quote', 'rating', 'is_featured']


@admin.register(EventCategory)
class EventCategoryAdmin(admin.ModelAdmin):
    list_display  = ['name', 'icon', 'color', 'order']
    list_editable = ['order', 'color']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display  = [
        'title', 'event_type', 'status', 'date',
        'is_featured', 'is_online', 'access', 'is_active'
    ]
    list_editable = ['status', 'is_featured', 'is_active']
    list_filter   = ['status', 'event_type', 'access', 'is_online', 'is_featured']
    search_fields = ['title', 'description', 'location']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['created_at', 'updated_at', 'cover_preview', 'banner_preview']
    ordering = ['-date']

    inlines = [EventSpeakerInline, EventGalleryInline, EventTestimonialInline]

    fieldsets = [
        ('Event Details', {
            'fields': [
                'title', 'slug', 'tagline', 'category',
                'event_type', 'description', 'status', 'access'
            ]
        }),
        ('Date & Location', {
            'fields': [
                'date', 'end_date', 'location',
                'is_online', 'timezone_label'
            ]
        }),
        ('Media', {
            'fields': [
                'cover_image', 'cover_preview',
                'banner_image', 'banner_preview',
                'video_recap'
            ]
        }),
        ('Registration', {
            'fields': [
                'registration_url', 'is_free',
                'price_ng', 'price_global'
            ]
        }),
        ('Event Stats (fill after event)', {
            'fields': [
                'attendees_count', 'partners_count',
                'speakers_count', 'sessions_count'
            ],
            'classes': ['collapse']
        }),
        ('Visibility', {
            'fields': ['is_featured', 'is_active']
        }),
        ('SEO', {
            'fields': ['meta_title', 'meta_description'],
            'classes': ['collapse']
        }),
        ('Timestamps', {
            'fields': ['created_at', 'updated_at'],
            'classes': ['collapse']
        }),
    ]

    def cover_preview(self, obj):
        if obj.cover_image:
            return format_html(
                '<img src="{}" style="max-height:100px;border-radius:6px;">',
                obj.cover_image.url
            )
        return 'No image'
    cover_preview.short_description = 'Cover Preview'

    def banner_preview(self, obj):
        if obj.banner_image:
            return format_html(
                '<img src="{}" style="max-height:80px;border-radius:6px;max-width:320px;">',
                obj.banner_image.url
            )
        return 'No banner'
    banner_preview.short_description = 'Banner Preview'


@admin.register(EventTestimonial)
class EventTestimonialAdmin(admin.ModelAdmin):
    list_display  = ['name', 'role', 'rating', 'is_featured', 'event']
    list_editable = ['is_featured', 'rating']
    list_filter   = ['is_featured', 'rating']





# ── 2. ADD TO core/admin.py ──────────────────────────────────────────────

 
@admin.register(InsightCategory)
class InsightCategoryAdmin(admin.ModelAdmin):
    list_display  = ['name', 'icon', 'color', 'order']
    list_editable = ['order', 'color']
    prepopulated_fields = {'slug': ('name',)}
 
@admin.register(InsightTag)
class InsightTagAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
 
@admin.register(Insight)
class InsightAdmin(admin.ModelAdmin):
    list_display  = ['title', 'insight_type', 'category', 'audience',
                     'is_featured', 'is_sponsored', 'is_published', 'published_at']
    list_editable = ['is_featured', 'is_sponsored', 'is_published']
    list_filter   = ['insight_type', 'audience', 'is_featured',
                     'is_sponsored', 'is_premium', 'is_archived']
    search_fields = ['title', 'excerpt', 'body']
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ['tags']
    fieldsets = [
        ('Content', {
            'fields': ['title', 'slug', 'category', 'tags', 'insight_type',
                       'audience', 'excerpt', 'body', 'cover_image',
                       'video_url', 'read_time']
        }),
        ('Author', {
            'fields': ['author_name', 'author_role', 'author_photo']
        }),
        ('Attachments', {
            'fields': ['pdf_file', 'pdf_label']
        }),
        ('Flags', {
            'fields': ['is_featured', 'is_sponsored', 'is_premium',
                       'is_published', 'is_archived', 'published_at']
        }),
        ('SEO', {
            'fields': ['meta_title', 'meta_description'],
            'classes': ['collapse']
        }),
    ]
 