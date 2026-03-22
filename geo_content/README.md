# Geo Content Module for Django

A production-ready Django module for geo-based content rendering (Nigeria vs Global users).

## Features

- **IP-based Geo Detection**: Automatically detects user country using GeoIP2
- **Manual Region Switching**: Users can manually switch between Nigeria and Global regions
- **Dynamic Content CMS**: ContentBlock model for managing Nigeria vs Global content variants
- **Template Integration**: Context processors and template tags for easy template usage
- **Caching**: Built-in caching for optimal performance
- **Admin Interface**: Customized Django admin for managing content blocks
- **Analytics**: Optional logging of region switches
- **Currency Support**: Built-in currency handling (₦ vs $)

## Installation

### 1. Install Dependencies

```bash
# Install GeoIP2 dependencies
pip install geoip2

# For production caching (recommended)
pip install django-redis
```

### 2. Download GeoIP2 Database

```bash
# Create directory for GeoIP databases
mkdir geoip
cd geoip

# Download from MaxMind (requires free account)
# https://dev.maxmind.com/geoip/geolite2-free-geolocation-data
# Download: GeoLite2-Country.mmdb
```

### 3. Configure Django Settings

Add to `settings.py`:

```python
INSTALLED_APPS = [
    'django.contrib.gis',
    'geo_content',
    # ... other apps
]

MIDDLEWARE = [
    'geo_content.middleware.GeoDetectionMiddleware',
    # ... other middleware
]

TEMPLATES = [{
    'OPTIONS': {
        'context_processors': [
            'geo_content.context_processors.geo_context',
            # ... other processors
        ],
    },
}]

# GeoIP Configuration
GEOIP_PATH = BASE_DIR / 'geoip'
GEO_DEFAULT_COUNTRY = 'NG'
GEOIP_ENABLED = True
```

### 4. Run Migrations

```bash
python manage.py makemigrations geo_content
python manage.py migrate
```

### 5. Include URLs

In your main `urls.py`:

```python
from django.urls import path, include

urlpatterns = [
    path('', include('geo_content.urls')),
    # ... other urls
]
```

## Usage

### Creating Content Blocks

Via Django Admin:
1. Go to `/admin/geo_content/contentblock/`
2. Create a new content block with:
   - **Key**: Unique identifier (e.g., `hero_section`)
   - **Nigeria Content**: Text, images, JSON for Nigerian users
   - **Global Content**: Text, images, JSON for global users

Via Code:

```python
from geo_content.models import ContentBlock

block = ContentBlock.objects.create(
    key='pricing_banner',
    name='Pricing Banner',
    nigeria_text='Starting at ₦5,000/month',
    global_text='Starting at $50/month',
    nigeria_json={'price': 5000, 'period': '/month'},
    global_json={'price': 50, 'period': '/month'},
)
```

### In Views

```python
from geo_content.utils import get_content, get_pricing

def homepage(request):
    context = {
        'hero': get_content('hero_section', request),
        'pricing': get_pricing('basic_plan', request),
    }
    return render(request, 'home.html', context)
```

### In Templates

**Method 1: Using Context Variables**

```html
{% if is_nigeria %}
    <h1>Welcome to Tranter IT Nigeria!</h1>
{% else %}
    <h1>Welcome to Tranter IT Global!</h1>
{% endif %}

<p>Currency: {{ currency_symbol }}</p>
```

**Method 2: Using Content Blocks**

```html
<!-- Load content from view context -->
{{ hero.text }}
<img src="{{ hero.image }}" alt="Hero">

<!-- Pricing with currency -->
<p>Price: {{ pricing.formatted_price }}</p>
```

**Method 3: Using Template Tags**

```html
{% load geo_extras %}

{% geo_content "hero_section" as hero %}
{{ hero.text }}

{% geo_pricing "basic_plan" as price %}
{{ price.formatted_price }}

<!-- Region switcher -->
{% region_switcher button_class="btn btn-primary" %}
```

**Method 4: Conditional CSS Classes**

```html
<div class="{% if is_nigeria %}ng-theme{% else %}global-theme{% endif %}">
    Content here
</div>
```

### Region Switcher UI

Include the region switcher in your base template:

```html
{% include "geo_content/partials/region_switcher.html" %}
```

Or use the template tag:

```html
{% load geo_extras %}
{% region_switcher %}
```

This creates a button that:
- Shows "Switch to Global 🌍" for Nigerian users
- Shows "Switch to Nigeria 🇳🇬" for Global users

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/set-region/` | GET/POST | Switch region (redirects back) |
| `/api/set-region/` | POST | JSON API for region switch |
| `/api/current-region/` | GET | Get current region info |

**Example: Switch via AJAX**

```javascript
fetch('/api/set-region/', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCsrfToken(),
    },
    body: JSON.stringify({ region: 'GLOBAL' })
})
.then(r => r.json())
.then(data => {
    if (data.success) {
        window.location.reload();
    }
});
```

## Content Block JSON Structure

For structured content like pricing tables:

```json
{
    "plans": [
        {
            "name": "Basic",
            "price": 5000,
            "period": "/month",
            "features": ["Feature 1", "Feature 2"],
            "cta_text": "Get Started",
            "cta_url": "/signup/basic/",
            "featured": false
        },
        {
            "name": "Pro",
            "price": 15000,
            "period": "/month",
            "features": ["Feature 1", "Feature 2", "Feature 3"],
            "cta_text": "Get Started",
            "cta_url": "/signup/pro/",
            "featured": true
        }
    ]
}
```

## Testing

```bash
# Run tests
python manage.py test geo_content

# Test with specific IP (in settings.py)
GEOIP_TEST_IP = '8.8.8.8'  # Simulates US user
GEOIP_TEST_IP = '102.88.0.0'  # Simulates Nigeria user
```

## Performance Tips

1. **Enable Caching**: Use Redis for production caching
2. **Cache Static Content**: Content blocks are cached for 1 hour by default
3. **Use CDN**: For images, use a CDN with geo-based serving
4. **Lazy Loading**: Load geo-specific content via AJAX for non-critical sections

## Security Considerations

- Region input is validated (only `NG` or `GLOBAL` allowed)
- Session-based storage prevents URL tampering
- IP detection gracefully falls back to default
- Admin interface is protected by Django's auth

## File Structure

```
geo_content/
├── __init__.py
├── apps.py
├── models.py          # ContentBlock, RegionSwitchLog
├── middleware.py      # GeoDetectionMiddleware
├── context_processors.py
├── utils.py           # get_content, get_pricing helpers
├── views.py           # Region switch views
├── urls.py
├── admin.py
├── signals.py
├── tests.py
├── templates/
│   └── geo_content/
│       ├── home.html           # Example homepage
│       └── partials/
│           └── region_switcher.html
└── templatetags/
    ├── __init__.py
    └── geo_extras.py  # Template tags
```

## License

MIT License - Tranter IT Platform
