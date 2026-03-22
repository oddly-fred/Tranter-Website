"""
Geo Detection Middleware for Tranter IT Platform
Detects user location and attaches region info to request.
"""

import logging
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger(__name__)


class GeoDetectionMiddleware(MiddlewareMixin):
    """
    Middleware to detect user country and attach region information.

    Attaches:
        - request.country: ISO country code (e.g., 'NG', 'US')
        - request.is_nigeria: Boolean indicating if user is from Nigeria
        - request.region: 'NG' or 'GLOBAL' based on detection or session override

    Priority:
        1. Session override (if user manually selected region)
        2. IP-based GeoIP detection
        3. Default fallback (Nigeria)
    """

    DEFAULT_COUNTRY = 'NG'
    DEFAULT_REGION = 'NG'
    VALID_REGIONS = ['NG', 'GLOBAL']

    def __init__(self, get_response=None):
        super().__init__(get_response)
        self.geoip2 = None
        self._init_geoip()

    def _init_geoip(self):
        """Initialize GeoIP2 if available."""
        try:
            from django.contrib.gis.geoip2 import GeoIP2
            self.geoip2 = GeoIP2()
            logger.info("GeoIP2 initialized successfully")
        except Exception as e:
            logger.warning(f"GeoIP2 not available: {e}")
            self.geoip2 = None

    def _get_client_ip(self, request):
        """
        Extract client IP from request.
        Checks X-Forwarded-For header first (for proxies), then REMOTE_ADDR.
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            # X-Forwarded-For can contain multiple IPs, take the first one
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')

        # Handle localhost/development
        if ip in ['127.0.0.1', 'localhost', '::1', None]:
            # For development, you can set a test IP in settings
            ip = getattr(settings, 'GEOIP_TEST_IP', None)

        return ip

    def _detect_country(self, ip_address):
        """
        Detect country from IP using GeoIP2.
        Returns ISO country code or None if detection fails.
        """
        if not ip_address or not self.geoip2:
            return None

        try:
            country_code = self.geoip2.country_code(ip_address)
            return country_code
        except Exception as e:
            logger.debug(f"GeoIP detection failed for IP {ip_address}: {e}")
            return None

    def _get_country_from_headers(self, request):
        """
        Fallback: Try to get country from request headers.
        Some CDNs/proxies add country headers.
        """
        # Cloudflare
        cf_country = request.META.get('HTTP_CF_IPCOUNTRY')
        if cf_country:
            return cf_country

        # AWS CloudFront
        cloudfront_country = request.META.get('HTTP_CLOUDFRONT_VIEWER_COUNTRY')
        if cloudfront_country:
            return cloudfront_country

        # Custom header (for testing or custom proxies)
        custom_country = request.META.get('HTTP_X_COUNTRY_CODE')
        if custom_country:
            return custom_country

        return None

    def process_request(self, request):
        """
        Process incoming request and attach geo information.
        """
        # Initialize with defaults
        country = None
        is_nigeria = True  # Default to Nigeria
        region = self.DEFAULT_REGION

        # Step 1: Check for session override (highest priority)
        session_region = request.session.get('region')
        if session_region and session_region in self.VALID_REGIONS:
            region = session_region
            is_nigeria = (region == 'NG')
            # Try to get country from session too
            country = request.session.get('detected_country', self.DEFAULT_COUNTRY)

            logger.debug(f"Using session region: {region}")
        else:
            # Step 2: Detect from IP
            ip_address = self._get_client_ip(request)
            request.ip_address = ip_address  # Store for logging

            # Try GeoIP2 first
            country = self._detect_country(ip_address)

            # Fallback to headers
            if not country:
                country = self._get_country_from_headers(request)

            # Final fallback
            if not country:
                country = self.DEFAULT_COUNTRY
                logger.debug(f"Using default country: {country}")

            # Determine region from country
            is_nigeria = (country == 'NG')
            region = 'NG' if is_nigeria else 'GLOBAL'

            # Store detected values in session for reference
            request.session['detected_country'] = country
            request.session['auto_detected_region'] = region

            logger.debug(f"Detected country: {country}, region: {region}")

        # Attach to request
        request.country = country
        request.is_nigeria = is_nigeria
        request.region = region

        return None

    def process_response(self, request, response):
        """
        Add geo headers to response for debugging (optional).
        """
        # Add headers only in DEBUG mode or if explicitly enabled
        if getattr(settings, 'GEO_DEBUG_HEADERS', False):
            if hasattr(request, 'country'):
                response['X-Detected-Country'] = request.country
                response['X-Region'] = request.region

        return response


class RegionLoggingMiddleware(MiddlewareMixin):
    """
    Optional middleware to log region detection for analytics.
    """

    def process_request(self, request):
        """Log region info if user is switching."""
        if hasattr(request, 'region') and hasattr(request, 'country'):
            # Store in request for potential logging
            request.geo_detected = {
                'country': request.country,
                'region': request.region,
                'is_nigeria': request.is_nigeria,
            }
        return None
