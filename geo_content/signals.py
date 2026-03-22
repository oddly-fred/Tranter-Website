"""
Signals for Geo Content Module
"""

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache

from .models import ContentBlock


@receiver(post_save, sender=ContentBlock)
def clear_content_cache_on_save(sender, instance, **kwargs):
    """Clear cache when content block is saved."""
    instance.clear_cache()


@receiver(post_delete, sender=ContentBlock)
def clear_content_cache_on_delete(sender, instance, **kwargs):
    """Clear cache when content block is deleted."""
    instance.clear_cache()
