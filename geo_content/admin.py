"""
Admin configuration for Geo Content Module
"""

from django.contrib import admin
from django.utils.html import format_html
from .models import ContentBlock, RegionSwitchLog


@admin.register(ContentBlock)
class ContentBlockAdmin(admin.ModelAdmin):
    """
    Admin interface for ContentBlock with side-by-side Nigeria/Global editing.
    """

    list_display = [
        'key',
        'name',
        'is_active',
        'has_nigeria_content',
        'has_global_content',
        'updated_at',
    ]
    list_filter = ['is_active', 'created_at', 'updated_at']
    search_fields = ['key', 'name', 'nigeria_text', 'global_text']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('General', {
            'fields': ('key', 'name', 'is_active')
        }),
        ('Nigeria Content 🇳🇬', {
            'fields': ('nigeria_text', 'nigeria_image', 'nigeria_json'),
            'classes': ('collapse',),
            'description': 'Content shown to users from Nigeria'
        }),
        ('Global Content 🌍', {
            'fields': ('global_text', 'global_image', 'global_json'),
            'classes': ('collapse',),
            'description': 'Content shown to users outside Nigeria'
        }),
        ('Currency Settings', {
            'fields': (
                'nigeria_currency_code',
                'nigeria_currency_symbol',
                'global_currency_code',
                'global_currency_symbol',
            ),
            'classes': ('collapse',),
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    def has_nigeria_content(self, obj):
        """Display checkmark if Nigeria content exists."""
        has_content = bool(obj.nigeria_text or obj.nigeria_image or obj.nigeria_json)
        return format_html(
            '<span style="color: {};">{}</span>',
            '#11874b' if has_content else '#dc3545',
            '✓' if has_content else '✗'
        )
    has_nigeria_content.short_description = 'NG Content'

    def has_global_content(self, obj):
        """Display checkmark if Global content exists."""
        has_content = bool(obj.global_text or obj.global_image or obj.global_json)
        return format_html(
            '<span style="color: {};">{}</span>',
            '#11874b' if has_content else '#dc3545',
            '✓' if has_content else '✗'
        )
    has_global_content.short_description = 'Global Content'

    actions = ['activate_selected', 'deactivate_selected', 'clear_cache']

    def activate_selected(self, request, queryset):
        """Bulk activate content blocks."""
        queryset.update(is_active=True)
        self.message_user(request, f"{queryset.count()} content blocks activated.")
    activate_selected.short_description = "Activate selected blocks"

    def deactivate_selected(self, request, queryset):
        """Bulk deactivate content blocks."""
        queryset.update(is_active=False)
        self.message_user(request, f"{queryset.count()} content blocks deactivated.")
    deactivate_selected.short_description = "Deactivate selected blocks"

    def clear_cache(self, request, queryset):
        """Clear cache for selected blocks."""
        for block in queryset:
            block.clear_cache()
        self.message_user(request, f"Cache cleared for {queryset.count()} blocks.")
    clear_cache.short_description = "Clear cache for selected"


@admin.register(RegionSwitchLog)
class RegionSwitchLogAdmin(admin.ModelAdmin):
    """
    Read-only admin for region switch logs.
    """

    list_display = [
        'timestamp',
        'selected_region',
        'detected_country',
        'ip_address',
        'user',
    ]
    list_filter = ['selected_region', 'detected_country', 'timestamp']
    readonly_fields = [
        'ip_address',
        'detected_country',
        'selected_region',
        'user_agent',
        'timestamp',
        'user',
    ]
    search_fields = ['ip_address', 'user_agent', 'user__username']
    date_hierarchy = 'timestamp'

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        """Allow deletion for cleanup, but not editing."""
        return True
