from django.db import models

class ZohoProduct(models.Model):
    REGION_CHOICES = [
        ('global', 'Global'),
        ('nigeria', 'Nigeria'),
        ('both', 'Both'),
    ]

    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)

    short_desc = models.TextField()
    full_desc = models.TextField()

    icon = models.CharField(max_length=50, blank=True)

    region = models.CharField(max_length=10, choices=REGION_CHOICES, default='both')

    is_featured = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class DemoRequest(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField()
    company = models.CharField(max_length=100)
    product = models.ForeignKey(ZohoProduct, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} - {self.product}"