from django.contrib import admin

from . import models


class DomainAdmin(admin.ModelAdmin):
    pass
admin.site.register(models.Domain, DomainAdmin)
