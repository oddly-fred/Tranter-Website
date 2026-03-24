from django.contrib import admin
from .models import ZohoProduct, DemoRequest

@admin.register(ZohoProduct)
class ZohoProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'region', 'is_featured')
    prepopulated_fields = {"slug": ("name",)}

@admin.register(DemoRequest)
class DemoRequestAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'email', 'product', 'created_at')


