from django.core.management.base import BaseCommand
from zoho.models import ZohoProduct


class Command(BaseCommand):
    help = 'Seed Zoho products into database'

    def handle(self, *args, **kwargs):

        products = [
            # 🌍 GLOBAL PRODUCTS (ONLY 4)
            {
                "name": "Zoho CRM",
                "slug": "crm",
                "short_desc": "Customer relationship management platform",
                "full_desc": "Manage leads, automate sales, and grow your customer relationships with Zoho CRM.",
                "region": "global"
            },
            {
                "name": "Zoho Books",
                "slug": "books",
                "short_desc": "Smart accounting software",
                "full_desc": "Handle invoicing, expenses, and financial reporting with Zoho Books.",
                "region": "global"
            },
            {
                "name": "Zoho Workplace",
                "slug": "workplace",
                "short_desc": "Email and collaboration suite",
                "full_desc": "Email, chat, documents, and collaboration tools for modern teams.",
                "region": "global"
            },
            {
                "name": "Zoho Desk",
                "slug": "desk",
                "short_desc": "Customer support platform",
                "full_desc": "Deliver great customer service with Zoho Desk ticketing and automation.",
                "region": "global"
            },

            # 🇳🇬 NIGERIA (FULL ECOSYSTEM)
            {
                "name": "Zoho People",
                "slug": "people",
                "short_desc": "HR management system",
                "full_desc": "Manage employee data, attendance, and HR processes.",
                "region": "nigeria"
            },
            {
                "name": "Zoho Inventory",
                "slug": "inventory",
                "short_desc": "Inventory & order management",
                "full_desc": "Track inventory, manage orders, and streamline logistics.",
                "region": "nigeria"
            },
            {
                "name": "Zoho Creator",
                "slug": "creator",
                "short_desc": "Custom app builder",
                "full_desc": "Build custom business applications without heavy coding.",
                "region": "nigeria"
            },
            {
                "name": "Zoho Projects",
                "slug": "projects",
                "short_desc": "Project management tool",
                "full_desc": "Plan, track, and collaborate on projects efficiently.",
                "region": "nigeria"
            },
            {
                "name": "Zoho Analytics",
                "slug": "analytics",
                "short_desc": "Business intelligence & reporting",
                "full_desc": "Turn your data into insights with dashboards and reports.",
                "region": "nigeria"
            },
        ]

        created_count = 0

        for product in products:
            obj, created = ZohoProduct.objects.get_or_create(
                slug=product["slug"],
                defaults=product
            )

            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f"Created: {product['name']}"))
            else:
                self.stdout.write(self.style.WARNING(f"Already exists: {product['name']}"))

        self.stdout.write(self.style.SUCCESS(f"\n✅ Done. {created_count} new products added."))