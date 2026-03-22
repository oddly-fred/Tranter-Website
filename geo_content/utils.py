"""
Utility functions for Geo Content Module
"""

import logging
from typing import Optional, Dict, Any
from django.core.cache import cache
from django.http import HttpRequest

from .models import ContentBlock

logger = logging.getLogger(__name__)


def get_content(key: str, request: Optional[HttpRequest] = None) -> Dict[str, Any]:
    """
    Get content for a specific key, automatically selecting Nigeria or Global variant.

    Args:
        key: The content block key (e.g., 'hero_section', 'pricing_banner')
        request: Django request object (optional, for region detection)

    Returns:
        Dict containing:
            - text: The text content
            - image: URL to the image (or None)
            - json: Structured data (or None)
            - currency_code: Currency code (e.g., 'NGN', 'USD')
            - currency_symbol: Currency symbol (e.g., '₦', '$')
            - found: Boolean indicating if content was found

    Usage:
        # In views:
        content = get_content('hero_section', request)

        # In templates:
        {{ content.text }}
        {% if content.image %}<img src="{{ content.image }}" />{% endif %}
    """
    # Determine region from request
    is_nigeria = True  # Default

    if request:
        # Check session override first
        session_region = request.session.get('region')
        if session_region:
            is_nigeria = (session_region == 'NG')
        else:
            # Use middleware-detected value
            is_nigeria = getattr(request, 'is_nigeria', True)

    # Build cache key
    region = 'nigeria' if is_nigeria else 'global'
    cache_key = f'geo_content:{key}:{region}'

    # Try cache first
    cached = cache.get(cache_key)
    if cached:
        return cached

    # Fetch from database
    block = ContentBlock.get_by_key(key)

    if not block:
        logger.warning(f"ContentBlock not found: {key}")
        result = {
            'text': '',
            'image': None,
            'json': None,
            'currency_code': 'NGN' if is_nigeria else 'USD',
            'currency_symbol': '₦' if is_nigeria else '$',
            'found': False,
        }
        cache.set(cache_key, result, 300)  # Cache miss for 5 minutes
        return result

    # Get content for the appropriate region
    content = block.get_content(is_nigeria=is_nigeria)

    result = {
        'text': content.get('text', ''),
        'image': content.get('image'),
        'json': content.get('json'),
        'currency_code': content.get('currency_code', 'NGN' if is_nigeria else 'USD'),
        'currency_symbol': content.get('currency_symbol', '₦' if is_nigeria else '$'),
        'found': True,
        'key': key,
    }

    # Cache for 1 hour
    cache.set(cache_key, result, 3600)
    return result


def get_content_or_default(key: str, request: Optional[HttpRequest] = None, default: str = '') -> str:
    """
    Get text content with a default fallback.

    Args:
        key: Content block key
        request: Django request
        default: Default text if not found

    Returns:
        Text content or default
    """
    content = get_content(key, request)
    return content.get('text') or default


def get_content_image(key: str, request: Optional[HttpRequest] = None) -> Optional[str]:
    """
    Get image URL for a content block.

    Args:
        key: Content block key
        request: Django request

    Returns:
        Image URL or None
    """
    content = get_content(key, request)
    return content.get('image')


def get_content_json(key: str, request: Optional[HttpRequest] = None) -> Optional[Dict]:
    """
    Get JSON data for a content block.

    Args:
        key: Content block key
        request: Django request

    Returns:
        JSON data dict or None
    """
    content = get_content(key, request)
    return content.get('json')


def get_pricing(key: str, request: Optional[HttpRequest] = None) -> Dict[str, Any]:
    """
    Get pricing information with currency.

    Args:
        key: Content block key (should contain pricing in JSON)
        request: Django request

    Returns:
        Dict with amount, currency_code, currency_symbol, formatted_price
    """
    content = get_content(key, request)
    json_data = content.get('json') or {}

    amount = json_data.get('amount', 0)
    currency_code = content.get('currency_code', 'NGN')
    currency_symbol = content.get('currency_symbol', '₦')

    # Format price
    if currency_code == 'NGN':
        formatted = f"{currency_symbol}{amount:,.0f}"
    else:
        formatted = f"{currency_symbol}{amount:,.2f}"

    return {
        'amount': amount,
        'currency_code': currency_code,
        'currency_symbol': currency_symbol,
        'formatted_price': formatted,
        'period': json_data.get('period', ''),  # e.g., '/month', '/year'
    }


def invalidate_content_cache(key: Optional[str] = None):
    """
    Invalidate content cache.

    Args:
        key: Specific content key to invalidate, or None to invalidate all
    """
    if key:
        cache.delete(f'geo_content:{key}:nigeria')
        cache.delete(f'geo_content:{key}:global')
        logger.info(f"Cache invalidated for content: {key}")
    else:
        # This is inefficient for large caches, better to use cache versioning
        # or specific cache keys. For now, we'll just log.
        logger.info("Full content cache invalidation requested")


def get_region_from_request(request: HttpRequest) -> str:
    """
    Get the current region from request.

    Args:
        request: Django request

    Returns:
        'NG' or 'GLOBAL'
    """
    # Check session first
    session_region = request.session.get('region')
    if session_region in ['NG', 'GLOBAL']:
        return session_region

    # Fall back to middleware value
    return getattr(request, 'region', 'NG')


def is_nigeria_request(request: HttpRequest) -> bool:
    """
    Check if current request is for Nigeria region.

    Args:
        request: Django request

    Returns:
        True if Nigeria region
    """
    return get_region_from_request(request) == 'NG'
