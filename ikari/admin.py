import logging

from django.contrib import admin
from django import forms

from .conf import settings, null_handler
from . import models
from .loader import get_model, load_class


logger = logging.getLogger(__name__)
logger.addHandler(null_handler)
IkariSiteModel = get_model(*settings.IKARI_SITE_MODEL.split("."))

class SiteForm(forms.ModelForm):

    class Meta:
        model = IkariSiteModel

    def clean_domain(self):
        domain = self.cleaned_data.get('domain')
        if domain == '':
            domain = None
        return domain


class DomainAdmin(admin.ModelAdmin):

    form = SiteForm

    def domain(instance):
        if instance.subdomain:
            return u"{domain}{tld}".format(
                domain=instance.subdomain,
                tld=settings.SUBDOMAIN_ROOT
            )
        if instance.domain:
            return instance.domain

    def verify_domain(instance, request, queryset):
        for domain in queryset:
            logger.debug("attempting to verify domain:", domain)
    verify_domain.short_description = 'Query the domain txt record for the uuid.'

    def disable_domain(instance, request, queryset):
        for domain in queryset:
            domain.is_active = True
            domain.save()
    disable_domain.short_description = 'Enable the selected domains.'

    def enable_domain(instance, request, queryset):
        for domain in queryset:
            domain.is_active = True
            domain.save()
    enable_domain.short_description = 'Enable the selected domains.'

    def set_domain_as_primary(instance, request, queryset):
        queryset.update(is_primary=True)

    set_domain_as_primary.short_description = 'Make the selected items the primary domain for their anchored objects.'
    list_display = (domain, 'is_public', 'is_active', 'is_primary', )
    actions = [verify_domain, disable_domain,
               enable_domain, set_domain_as_primary]


admin.site.register(IkariSiteModel, DomainAdmin)
