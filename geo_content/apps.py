from django.apps import AppConfig


class GeoContentConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'geo_content'
    verbose_name = 'Geo Content'

    def ready(self):
        """Import signals when app is ready."""
        import geo_content.signals  # noqa
