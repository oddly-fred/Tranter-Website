"""
Context Processors for Geo Content Module
Makes region information available in all templates.
"""

from django.conf import settings


def geo_context(request):
    """
    Add geo/region information to template context.

    Available in all templates:
        - is_nigeria: Boolean
        - region: 'NG' or 'GLOBAL'
        - country: ISO country code
        - region_switch_url: URL to switch regions
        - alternate_region: The opposite region (for switch button text)
        - alternate_region_name: Human-readable region name
        - alternate_region_flag: Emoji flag for the alternate region

    Usage in templates:
        {% if is_nigeria %}
            <p>Welcome, Nigerian user!</p>
        {% else %}
            <p>Welcome, international user!</p>
        {% endif %}
    """
    context = {
        'is_nigeria': getattr(request, 'is_nigeria', True),
        'region': getattr(request, 'region', 'NG'),
        'country': getattr(request, 'country', 'NG'),
    }

    # Add switch region info for the UI
    if context['is_nigeria']:
        context['alternate_region'] = 'GLOBAL'
        context['alternate_region_name'] = 'Global'
        context['alternate_region_flag'] = '🌍'
        context['current_region_flag'] = '🇳🇬'
        context['current_region_name'] = 'Nigeria'
    else:
        context['alternate_region'] = 'NG'
        context['alternate_region_name'] = 'Nigeria'
        context['alternate_region_flag'] = '🇳🇬'
        context['current_region_flag'] = '🌍'
        context['current_region_name'] = 'Global'

    # URL for region switch endpoint
    context['region_switch_url'] = '/set-region/'

    # Currency info
    if context['is_nigeria']:
        context['currency_code'] = 'NGN'
        context['currency_symbol'] = '₦'
    else:
        context['currency_code'] = 'USD'
        context['currency_symbol'] = '$'

    return context


def geo_settings(request):
    """
    Add geo-related settings to context.
    """
    return {
        'GEOIP_ENABLED': getattr(settings, 'GEOIP_ENABLED', True),
        'GEO_DEBUG_HEADERS': getattr(settings, 'GEO_DEBUG_HEADERS', False),
    }


