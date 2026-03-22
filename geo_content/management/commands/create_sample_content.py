"""
Management command to create sample content blocks for testing.

Usage:
    python manage.py create_sample_content
"""

from django.core.management.base import BaseCommand
from geo_content.models import ContentBlock


class Command(BaseCommand):
    help = 'Create sample content blocks for Nigeria and Global regions'

    def handle(self, *args, **options):
        self.stdout.write('Creating sample content blocks...')

        # Hero Section
        hero, created = ContentBlock.objects.get_or_create(
            key='hero_section',
            defaults={
                'name': 'Homepage Hero Section',
                'nigeria_text': 'Powering<br><span style="color:#11874b">Intelligent</span><br><span style="opacity:.7">Infrastructure.</span>',
                'global_text': 'Powering<br><span style="color:#11874b">Intelligent</span><br><span style="opacity:.7">Infrastructure.</span>',
                'nigeria_json': {
                    'headline': 'Powering Intelligent Infrastructure',
                    'subheadline': 'Built for Nigerian enterprises',
                    'cta_text': 'Talk to an Expert',
                    'cta_url': '/contact/',
                },
                'global_json': {
                    'headline': 'Powering Intelligent Infrastructure',
                    'subheadline': 'Built for global enterprises',
                    'cta_text': 'Talk to an Expert',
                    'cta_url': '/contact/',
                },
                'is_active': True,
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created: {hero.name}'))
        else:
            self.stdout.write(f'Already exists: {hero.name}')

        # CTA Banner
        cta, created = ContentBlock.objects.get_or_create(
            key='cta_banner',
            defaults={
                'name': 'CTA Banner',
                'nigeria_text': 'Ready to power your next phase of growth?',
                'global_text': 'Ready to power your next phase of growth?',
                'nigeria_json': {
                    'eyebrow': 'Let\'s get started in Nigeria',
                    'button_text': 'Book a Free Consultation',
                },
                'global_json': {
                    'eyebrow': 'Let\'s get started',
                    'button_text': 'Book a Free Consultation',
                },
                'is_active': True,
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created: {cta.name}'))
        else:
            self.stdout.write(f'Already exists: {cta.name}')

        # Trust Strip
        trust, created = ContentBlock.objects.get_or_create(
            key='trust_strip',
            defaults={
                'name': 'Trust Strip',
                'nigeria_text': 'Trusted by Nigeria\'s leading enterprises',
                'global_text': 'Trusted by global industry leaders',
                'is_active': True,
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created: {trust.name}'))
        else:
            self.stdout.write(f'Already exists: {trust.name}')

        # Pricing Banner (example with pricing data)
        pricing, created = ContentBlock.objects.get_or_create(
            key='pricing_banner',
            defaults={
                'name': 'Pricing Banner',
                'nigeria_text': 'Flexible pricing for Nigerian businesses',
                'global_text': 'Flexible pricing for global businesses',
                'nigeria_json': {
                    'plans': [
                        {
                            'name': 'Starter',
                            'price': 50000,
                            'period': '/month',
                            'features': ['IT Support', 'Email Security', 'Basic Monitoring'],
                            'cta_text': 'Get Started',
                            'cta_url': '/contact/',
                            'featured': False,
                        },
                        {
                            'name': 'Business',
                            'price': 150000,
                            'period': '/month',
                            'features': ['Everything in Starter', '24/7 Support', 'Advanced Security', 'Cloud Backup'],
                            'cta_text': 'Get Started',
                            'cta_url': '/contact/',
                            'featured': True,
                        },
                    ]
                },
                'global_json': {
                    'plans': [
                        {
                            'name': 'Starter',
                            'price': 500,
                            'period': '/month',
                            'features': ['IT Support', 'Email Security', 'Basic Monitoring'],
                            'cta_text': 'Get Started',
                            'cta_url': '/contact/',
                            'featured': False,
                        },
                        {
                            'name': 'Business',
                            'price': 1500,
                            'period': '/month',
                            'features': ['Everything in Starter', '24/7 Support', 'Advanced Security', 'Cloud Backup'],
                            'cta_text': 'Get Started',
                            'cta_url': '/contact/',
                            'featured': True,
                        },
                    ]
                },
                'nigeria_currency_code': 'NGN',
                'nigeria_currency_symbol': '₦',
                'global_currency_code': 'USD',
                'global_currency_symbol': '$',
                'is_active': True,
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created: {pricing.name}'))
        else:
            self.stdout.write(f'Already exists: {pricing.name}')

        self.stdout.write(self.style.SUCCESS('\nSample content blocks created successfully!'))
        self.stdout.write('You can now view and edit them in the Django Admin.')
