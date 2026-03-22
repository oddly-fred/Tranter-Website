"""
Template tags and filters for Geo Content Module
"""

from django import template
from django.utils.safestring import mark_safe

from ..utils import get_content, get_pricing

register = template.Library()


@register.simple_tag(takes_context=True)
def geo_content(context, key):
    """
    Template tag to load geo content by key.

    Usage:
        {% load geo_extras %}
        {% geo_content "hero_section" as hero %}
        {{ hero.text }}

    Args:
        key: Content block key

    Returns:
        Content dict with text, image, json, etc.
    """
    request = context.get('request')
    return get_content(key, request)


@register.simple_tag(takes_context=True)
def geo_pricing(context, key):
    """
    Template tag to load pricing with currency.

    Usage:
        {% geo_pricing "pricing_basic" as price %}
        {{ price.formatted_price }}

    Returns:
        Dict with amount, currency_code, currency_symbol, formatted_price
    """
    request = context.get('request')
    return get_pricing(key, request)


@register.filter
def currency_format(amount, symbol="₦"):
    """
    Format a number as currency.

    Usage:
        {{ price|currency_format:"₦" }}
        {{ price|currency_format:"$" }}
    """
    try:
        amount = float(amount)
        if symbol == '₦' or symbol == 'NGN':
            return mark_safe(f"₦{amount:,.0f}")
        else:
            return mark_safe(f"${amount:,.2f}")
    except (ValueError, TypeError):
        return amount


@register.simple_tag(takes_context=True)
def region_class(context, nigeria_class='', global_class=''):
    """
    Output different CSS classes based on region.

    Usage:
        <div class="{% region_class 'nigeria-style' 'global-style' %}">

    Returns:
        nigeria_class if is_nigeria, else global_class
    """
    is_nigeria = context.get('is_nigeria', True)
    return nigeria_class if is_nigeria else global_class


@register.simple_tag(takes_context=True)
def region_text(context, nigeria_text='', global_text=''):
    """
    Output different text based on region.

    Usage:
        <h1>{% region_text "Welcome Nigeria" "Welcome Global" %}</h1>

    Returns:
        nigeria_text if is_nigeria, else global_text
    """
    is_nigeria = context.get('is_nigeria', True)
    return mark_safe(nigeria_text if is_nigeria else global_text)


@register.filter
def get_item(dictionary, key):
    """
    Get an item from a dictionary.

    Usage:
        {{ my_dict|get_item:"key" }}
    """
    if dictionary:
        return dictionary.get(key)
    return None


@register.inclusion_tag('geo_content/partials/region_switcher.html', takes_context=True)
def region_switcher(context, button_class=''):
    """
    Render the region switcher button.

    Usage:
        {% load geo_extras %}
        {% region_switcher button_class="btn btn-primary" %}
    """
    return {
        'request': context.get('request'),
        'is_nigeria': context.get('is_nigeria', True),
        'region': context.get('region', 'NG'),
        'alternate_region': context.get('alternate_region', 'GLOBAL'),
        'alternate_region_name': context.get('alternate_region_name', 'Global'),
        'alternate_region_flag': context.get('alternate_region_flag', '🌍'),
        'button_class': button_class,
    }
