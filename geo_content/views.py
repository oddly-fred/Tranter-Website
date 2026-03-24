"""
Views for Geo Content Module
"""

import logging
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseRedirect
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
from django.contrib import messages
from django.conf import settings

from .models import ContentBlock, RegionSwitchLog
from .utils import get_content, get_region_from_request, is_nigeria_request

logger = logging.getLogger(__name__)


class GeoTemplateView(TemplateView):
    """
    Enhanced TemplateView that automatically loads geo content.

    Usage:
        class HomeView(GeoTemplateView):
            template_name = 'home.html'
            content_keys = ['hero_section', 'features_section', 'pricing_banner']

    The content will be available in template context as 'geo_content'.
    """

    content_keys = []  # List of ContentBlock keys to load

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Load all requested content blocks
        geo_content = {}
        for key in self.content_keys:
            geo_content[key] = get_content(key, self.request)

        context['geo_content'] = geo_content
        return context


@require_http_methods(["GET", "POST"])
def set_region(request):
    """
    View to manually switch between Nigeria and Global regions.

    Accepts:
        - GET: ?region=NG or ?region=GLOBAL
        - POST: region=NG or region=GLOBAL

    Stores selection in session and redirects back.

    URL: /set-region/
    """
    VALID_REGIONS = ['NG', 'GLOBAL']

    # Get region from request
    if request.method == 'POST':
        region = request.POST.get('region', '').upper()
        next_url = request.POST.get('next', request.META.get('HTTP_REFERER', '/'))
    else:
        region = request.GET.get('region', '').upper()
        next_url = request.GET.get('next', request.META.get('HTTP_REFERER', '/'))

    # Validate region
    if region not in VALID_REGIONS:
        logger.warning(f"Invalid region requested: {region}")
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'error': f"Invalid region. Must be one of: {', '.join(VALID_REGIONS)}"
            }, status=400)
        messages.error(request, "Invalid region selected.")
        return HttpResponseRedirect(next_url)

    # Store in session
    old_region = request.session.get('region')
    request.session['region'] = region

    # Log the switch
    try:
        RegionSwitchLog.objects.create(
            ip_address=getattr(request, 'ip_address', None),
            detected_country=getattr(request, 'country', ''),
            selected_region=region,
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            user=request.user if request.user.is_authenticated else None,
        )
    except Exception as e:
        logger.error(f"Failed to log region switch: {e}")

    logger.info(f"Region switched from {old_region} to {region} for IP {getattr(request, 'ip_address', 'unknown')}")

    # Response based on request type
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'region': region,
            'is_nigeria': region == 'NG',
            'message': f"Region set to {'Nigeria' if region == 'NG' else 'Global'}"
        })

    # Add success message
    region_name = 'Nigeria 🇳🇬' if region == 'NG' else 'Global 🌍'
    messages.success(request, f"Region switched to {region_name}")

    return HttpResponseRedirect(next_url)


@csrf_exempt
@require_http_methods(["POST"])
def api_set_region(request):
    """
    API endpoint for setting region (for AJAX/fetch requests).

    Accepts JSON or form data:
        { "region": "NG" } or { "region": "GLOBAL" }

    Returns JSON:
        { "success": true, "region": "NG", "is_nigeria": true }
    """
    import json

    VALID_REGIONS = ['NG', 'GLOBAL']

    # Parse request body
    try:
        if request.content_type == 'application/json':
            data = json.loads(request.body)
        else:
            data = request.POST
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON'
        }, status=400)

    region = data.get('region', '').upper()

    if region not in VALID_REGIONS:
        return JsonResponse({
            'success': False,
            'error': f"Invalid region. Must be one of: {', '.join(VALID_REGIONS)}"
        }, status=400)

    # Store in session
    request.session['region'] = region

    # Log the switch
    try:
        RegionSwitchLog.objects.create(
            ip_address=getattr(request, 'ip_address', None),
            detected_country=getattr(request, 'country', ''),
            selected_region=region,
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            user=request.user if request.user.is_authenticated else None,
        )
    except Exception as e:
        logger.error(f"Failed to log region switch: {e}")

    return JsonResponse({
        'success': True,
        'region': region,
        'is_nigeria': region == 'NG',
        'message': f"Region set to {'Nigeria' if region == 'NG' else 'Global'}"
    })


def get_current_region(request):
    """
    API endpoint to get current region info.

    Returns:
        {
            "region": "NG",
            "is_nigeria": true,
            "country": "NG",
            "session_override": false
        }
    """
    session_region = request.session.get('region')
    detected_region = getattr(request, 'region', 'NG')

    return JsonResponse({
        'region': detected_region,
        'is_nigeria': detected_region == 'NG',
        'country': getattr(request, 'country', 'NG'),
        'session_override': session_region is not None,
        'session_region': session_region,
    })
