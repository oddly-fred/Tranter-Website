"""
Models for Geo Content Module
Handles dynamic content blocks with Nigeria vs Global variants.
"""

import json
from django.db import models
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.conf import settings


class ContentBlock(models.Model):
    """
    Dynamic content block supporting Nigeria vs Global content variants.

    Usage:
        block = ContentBlock.objects.get(key='hero_section')
        content = block.get_content(request)  # Returns Nigeria or Global based on request
    """

    REGION_NIGERIA = 'NG'
    REGION_GLOBAL = 'GLOBAL'
    REGION_CHOICES = [
        (REGION_NIGERIA, 'Nigeria'),
        (REGION_GLOBAL, 'Global'),
    ]

    # Primary identifier
    key = models.SlugField(
        max_length=100,
        unique=True,
        db_index=True,
        help_text="Unique identifier for this content block (e.g., 'hero_section', 'pricing_banner')"
    )

    # Display name for admin
    name = models.CharField(
        max_length=200,
        help_text="Human-readable name for this content block"
    )

    # Nigeria content variants
    nigeria_text = models.TextField(
        blank=True,
        help_text="Text content for Nigerian users"
    )
    nigeria_image = models.ImageField(
        upload_to='content/nigeria/',
        blank=True,
        null=True,
        help_text="Image for Nigerian users"
    )
    nigeria_json = models.JSONField(
        blank=True,
        null=True,
        help_text="Structured data for Nigerian users (e.g., pricing, features)"
    )

    # Global content variants
    global_text = models.TextField(
        blank=True,
        help_text="Text content for global (non-Nigerian) users"
    )
    global_image = models.ImageField(
        upload_to='content/global/',
        blank=True,
        null=True,
        help_text="Image for global users"
    )
    global_json = models.JSONField(
        blank=True,
        null=True,
        help_text="Structured data for global users (e.g., pricing, features)"
    )

    # Currency fields (bonus feature)
    nigeria_currency_code = models.CharField(
        max_length=3,
        default='NGN',
        help_text="Currency code for Nigeria (e.g., NGN)"
    )
    nigeria_currency_symbol = models.CharField(
        max_length=10,
        default='₦',
        help_text="Currency symbol for Nigeria"
    )
    global_currency_code = models.CharField(
        max_length=3,
        default='USD',
        help_text="Currency code for Global (e.g., USD)"
    )
    global_currency_symbol = models.CharField(
        max_length=10,
        default='$',
        help_text="Currency symbol for Global"
    )

    # Metadata
    is_active = models.BooleanField(
        default=True,
        db_index=True,
        help_text="Only active blocks are returned by get_content()"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['key']
        verbose_name = 'Content Block'
        verbose_name_plural = 'Content Blocks'
        indexes = [
            models.Index(fields=['key', 'is_active']),
        ]

    def __str__(self):
        return f"{self.name} ({self.key})"

    def clean(self):
        """Validate that at least one region has content."""
        has_nigeria = bool(self.nigeria_text or self.nigeria_image or self.nigeria_json)
        has_global = bool(self.global_text or self.global_image or self.global_json)

        if not has_nigeria and not has_global:
            raise ValidationError(
                "At least one region (Nigeria or Global) must have content."
            )

    def save(self, *args, **kwargs):
        """Clear cache on save."""
        super().save(*args, **kwargs)
        self.clear_cache()

    def delete(self, *args, **kwargs):
        """Clear cache on delete."""
        self.clear_cache()
        super().delete(*args, **kwargs)

    def clear_cache(self):
        """Clear the cache for this content block."""
        cache.delete(f'content_block:{self.key}')
        cache.delete(f'content_block:{self.key}:nigeria')
        cache.delete(f'content_block:{self.key}:global')

    def get_content(self, is_nigeria=True):
        """
        Get content for the specified region.

        Args:
            is_nigeria: If True, return Nigeria content; else Global

        Returns:
            dict with text, image_url, json_data, currency_code, currency_symbol
        """
        cache_key = f'content_block:{self.key}:{"nigeria" if is_nigeria else "global"}'
        cached = cache.get(cache_key)

        if cached:
            return cached

        if is_nigeria:
            result = {
                'text': self.nigeria_text,
                'image': self.nigeria_image.url if self.nigeria_image else None,
                'json': self.nigeria_json,
                'currency_code': self.nigeria_currency_code,
                'currency_symbol': self.nigeria_currency_symbol,
            }
        else:
            result = {
                'text': self.global_text,
                'image': self.global_image.url if self.global_image else None,
                'json': self.global_json,
                'currency_code': self.global_currency_code,
                'currency_symbol': self.global_currency_symbol,
            }

        # Cache for 1 hour
        cache.set(cache_key, result, 3600)
        return result

    @classmethod
    def get_by_key(cls, key):
        """
        Get active content block by key with caching.

        Args:
            key: The content block key

        Returns:
            ContentBlock instance or None
        """
        cache_key = f'content_block:{key}'
        cached = cache.get(cache_key)

        if cached:
            return cached

        try:
            block = cls.objects.get(key=key, is_active=True)
            cache.set(cache_key, block, 3600)
            return block
        except cls.DoesNotExist:
            return None


class RegionSwitchLog(models.Model):
    """
    Log region switches for analytics.
    Optional: Track user region preferences.
    """

    REGION_CHOICES = [
        ('NG', 'Nigeria'),
        ('GLOBAL', 'Global'),
    ]

    ip_address = models.GenericIPAddressField(null=True, blank=True)
    detected_country = models.CharField(max_length=2, blank=True)
    selected_region = models.CharField(max_length=10, choices=REGION_CHOICES)
    user_agent = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    # Optional: Link to user if authenticated
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Region Switch Log'
        verbose_name_plural = 'Region Switch Logs'

    def __str__(self):
        return f"{self.selected_region} from {self.detected_country} at {self.timestamp}"
