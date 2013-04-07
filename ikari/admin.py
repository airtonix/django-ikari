from django.contrib import admin

from . import models


class DomainAdmin(admin.ModelAdmin):
    list_display = ('anchored_on', 'domain', 'subdomain', 'is_public', 'is_active', 'is_primary', )
admin.site.register(models.Domain, DomainAdmin)
