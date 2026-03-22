"""
Settings Configuration for Geo Content Module

Add these settings to your Django project's settings.py
"""

# ═══════════════════════════════════════════════════
# GEO CONTENT MODULE SETTINGS
# Add to your settings.py
# ═══════════════════════════════════════════════════

INSTALLED_APPS = [
    # ... your other apps
    'django.contrib.gis',  # Required for GeoIP2
    'geo_content',
]

MIDDLEWARE = [
    # ... your other middleware
    'geo_content.middleware.GeoDetectionMiddleware',
    # Optional: 'geo_content.middleware.RegionLoggingMiddleware',
]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # ... other settings
        'OPTIONS': {
            'context_processors': [
                # ... other context processors
                'geo_content.context_processors.geo_context',
                'geo_content.context_processors.geo_settings',
            ],
        },
    },
]

# ═══════════════════════════════════════════════════
# GEOIP2 Configuration (for IP-based detection)
# ═══════════════════════════════════════════════════

# Download GeoIP2 databases from MaxMind:
# https://dev.maxmind.com/geoip/geolite2-free-geolocation-data

GEOIP_PATH = BASE_DIR / 'geoip'  # Path to GeoIP2 database files

# Optional: Configure cache for GeoIP2
GEOIP_CACHE_TYPE = 'memory'  # or 'disk'

# Test IP for development (simulates a specific country)
GEOIP_TEST_IP = None  # e.g., '8.8.8.8' for US, '102.88.0.0' for Nigeria

# ═══════════════════════════════════════════════════
# Geo Content Module Settings
# ═══════════════════════════════════════════════════

# Enable/disable GeoIP detection
GEOIP_ENABLED = True

# Default country when detection fails
GEO_DEFAULT_COUNTRY = 'NG'

# Valid regions for manual switching
GEO_VALID_REGIONS = ['NG', 'GLOBAL']

# Add debug headers to responses (only for debugging)
GEO_DEBUG_HEADERS = False  # Set to True only in development

# Session key for region storage
GEO_SESSION_KEY = 'region'

# Cache timeout for content blocks (in seconds)
GEO_CONTENT_CACHE_TIMEOUT = 3600  # 1 hour

# ═══════════════════════════════════════════════════
# Caching Configuration (recommended)
# ═══════════════════════════════════════════════════

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        # For production, use Redis or Memcached:
        # 'BACKEND': 'django_redis.cache.RedisCache',
        # 'LOCATION': 'redis://127.0.0.1:6379/1',
    }
}

# ═══════════════════════════════════════════════════
# Media Files Configuration (for content images)
# ═══════════════════════════════════════════════════

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# ═══════════════════════════════════════════════════
# URL Configuration
# ═══════════════════════════════════════════════════

# In your main urls.py, add:
# from django.conf import settings
# from django.conf.urls.static import static
#
# urlpatterns = [
#     # ... your other urls
#     path('', include('geo_content.urls')),
# ]
#
# if settings.DEBUG:
#     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
