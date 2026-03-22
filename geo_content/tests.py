"""
Tests for Geo Content Module
"""

from django.test import TestCase, RequestFactory, override_settings
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.auth.models import AnonymousUser
from django.core.cache import cache

from .models import ContentBlock, RegionSwitchLog
from .middleware import GeoDetectionMiddleware
from .utils import get_content, get_region_from_request, is_nigeria_request
from .views import set_region


class ContentBlockModelTest(TestCase):
    """Tests for ContentBlock model."""

    def setUp(self):
        """Set up test data."""
        cache.clear()
        self.block = ContentBlock.objects.create(
            key='test_block',
            name='Test Block',
            nigeria_text='Nigeria Content',
            global_text='Global Content',
            nigeria_json={'price': 1000, 'currency': 'NGN'},
            global_json={'price': 50, 'currency': 'USD'},
        )

    def tearDown(self):
        """Clean up cache."""
        cache.clear()

    def test_get_content_nigeria(self):
        """Test getting Nigeria content."""
        content = self.block.get_content(is_nigeria=True)
        self.assertEqual(content['text'], 'Nigeria Content')
        self.assertEqual(content['currency_code'], 'NGN')
        self.assertEqual(content['currency_symbol'], '₦')

    def test_get_content_global(self):
        """Test getting Global content."""
        content = self.block.get_content(is_nigeria=False)
        self.assertEqual(content['text'], 'Global Content')
        self.assertEqual(content['currency_code'], 'USD')
        self.assertEqual(content['currency_symbol'], '$')

    def test_get_by_key_caching(self):
        """Test that get_by_key caches results."""
        # First call should hit database
        block1 = ContentBlock.get_by_key('test_block')
        self.assertIsNotNone(block1)

        # Second call should hit cache
        block2 = ContentBlock.get_by_key('test_block')
        self.assertEqual(block1, block2)

    def test_get_by_key_inactive(self):
        """Test that inactive blocks are not returned."""
        self.block.is_active = False
        self.block.save()

        result = ContentBlock.get_by_key('test_block')
        self.assertIsNone(result)


class GeoDetectionMiddlewareTest(TestCase):
    """Tests for GeoDetectionMiddleware."""

    def setUp(self):
        """Set up request factory."""
        self.factory = RequestFactory()
        self.middleware = GeoDetectionMiddleware(lambda req: None)

    def _add_session(self, request):
        """Add session to request."""
        middleware = SessionMiddleware(lambda req: None)
        middleware.process_request(request)
        request.session.save()
        return request

    def test_default_region(self):
        """Test default region is Nigeria."""
        request = self.factory.get('/')
        request = self._add_session(request)
        request.user = AnonymousUser()

        self.middleware.process_request(request)

        self.assertEqual(request.region, 'NG')
        self.assertTrue(request.is_nigeria)
        self.assertEqual(request.country, 'NG')

    def test_session_override(self):
        """Test session override takes priority."""
        request = self.factory.get('/')
        request = self._add_session(request)
        request.session['region'] = 'GLOBAL'
        request.user = AnonymousUser()

        self.middleware.process_request(request)

        self.assertEqual(request.region, 'GLOBAL')
        self.assertFalse(request.is_nigeria)

    def test_session_override_ng(self):
        """Test session override to Nigeria."""
        request = self.factory.get('/')
        request = self._add_session(request)
        request.session['region'] = 'NG'
        request.user = AnonymousUser()

        self.middleware.process_request(request)

        self.assertEqual(request.region, 'NG')
        self.assertTrue(request.is_nigeria)


class UtilsTest(TestCase):
    """Tests for utility functions."""

    def setUp(self):
        """Set up test data."""
        cache.clear()
        self.factory = RequestFactory()

        self.block = ContentBlock.objects.create(
            key='hero_section',
            name='Hero',
            nigeria_text='Welcome Nigeria',
            global_text='Welcome Global',
        )

    def tearDown(self):
        """Clean up cache."""
        cache.clear()

    def _create_request(self, region=None):
        """Create a request with optional region in session."""
        request = self.factory.get('/')
        middleware = SessionMiddleware(lambda req: None)
        middleware.process_request(request)
        if region:
            request.session['region'] = region
        request.session.save()
        request.user = AnonymousUser()
        return request

    def test_get_content_nigeria(self):
        """Test get_content returns Nigeria content."""
        request = self._create_request(region='NG')
        content = get_content('hero_section', request)

        self.assertTrue(content['found'])
        self.assertEqual(content['text'], 'Welcome Nigeria')

    def test_get_content_global(self):
        """Test get_content returns Global content."""
        request = self._create_request(region='GLOBAL')
        content = get_content('hero_section', request)

        self.assertTrue(content['found'])
        self.assertEqual(content['text'], 'Welcome Global')

    def test_get_content_not_found(self):
        """Test get_content handles missing blocks."""
        request = self._create_request()
        content = get_content('nonexistent', request)

        self.assertFalse(content['found'])
        self.assertEqual(content['text'], '')

    def test_get_region_from_request(self):
        """Test get_region_from_request."""
        request = self._create_request(region='GLOBAL')
        self.assertEqual(get_region_from_request(request), 'GLOBAL')

    def test_is_nigeria_request(self):
        """Test is_nigeria_request."""
        request = self._create_request(region='NG')
        self.assertTrue(is_nigeria_request(request))

        request = self._create_request(region='GLOBAL')
        self.assertFalse(is_nigeria_request(request))


class SetRegionViewTest(TestCase):
    """Tests for set_region view."""

    def setUp(self):
        """Set up test data."""
        self.factory = RequestFactory()

    def _create_request(self, method='GET', data=None):
        """Create a request with session."""
        if method == 'POST':
            request = self.factory.post('/set-region/', data)
        else:
            request = self.factory.get('/set-region/', data)

        middleware = SessionMiddleware(lambda req: None)
        middleware.process_request(request)
        request.session.save()
        request.user = AnonymousUser()

        return request

    def test_set_region_get(self):
        """Test setting region via GET."""
        request = self._create_request('GET', {'region': 'GLOBAL'})
        response = set_region(request)

        self.assertEqual(response.status_code, 302)  # Redirect
        self.assertEqual(request.session['region'], 'GLOBAL')

    def test_set_region_post(self):
        """Test setting region via POST."""
        request = self._create_request('POST', {'region': 'NG'})
        response = set_region(request)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(request.session['region'], 'NG')

    def test_set_region_invalid(self):
        """Test invalid region is rejected."""
        request = self._create_request('GET', {'region': 'INVALID'})
        response = set_region(request)

        self.assertEqual(response.status_code, 302)  # Redirects with error
        # Region should not be set
        self.assertNotIn('region', request.session)

    def test_set_region_ajax(self):
        """Test AJAX request returns JSON."""
        request = self._create_request('GET', {'region': 'GLOBAL'})
        request.META['HTTP_X_REQUESTED_WITH'] = 'XMLHttpRequest'

        response = set_region(request)

        self.assertEqual(response.status_code, 200)
        import json
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        self.assertEqual(data['region'], 'GLOBAL')


class RegionSwitchLogTest(TestCase):
    """Tests for RegionSwitchLog model."""

    def test_create_log(self):
        """Test creating a region switch log."""
        log = RegionSwitchLog.objects.create(
            ip_address='192.168.1.1',
            detected_country='US',
            selected_region='GLOBAL',
            user_agent='Test Agent',
        )

        self.assertEqual(log.selected_region, 'GLOBAL')
        self.assertEqual(log.detected_country, 'US')
