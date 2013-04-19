import logging

from django.contrib import admin
from django import forms

from . import settings
from . import models

logger = logging.getLogger(__name__)
logger.addHandler(settings.null_handler)

class DomainForm(forms.ModelForm):
    class Meta:
        model = models.Domain

    def clean_domain(self):
        domain = self.cleaned_data['domain']
        if domain == '':
            domain = None
        return domain


class DomainAdmin(admin.ModelAdmin):

    form = DomainForm

    def anchored_on(instance):
        return u"{thing} ({thing_type})".format(
            thing=instance.anchored_on,
            thing_type=instance.anchored_on.__class__.__name__
        )

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
        groups = {}
        ambigous_items = []

        for domain in queryset:
            group = groups.get(domain.anchored_on, [])
            group.append(domain)

        for key, value in groups.iteritems():
            if len(value) > 1:
                ambigous_items = ambigous_items + value
            else:
                domain = value[0]
                domain.anchored_on.anchored_domains.update(is_primary=False)
                domain.is_primary = True
                domain.save()

    set_domain_as_primary.short_description = 'Make the selected items the primary domain for their anchored objects.'
    list_display = (anchored_on, domain, 'is_public', 'is_active', 'is_primary', )
    actions = [verify_domain, disable_domain, enable_domain, set_domain_as_primary]


admin.site.register(models.Domain, DomainAdmin)
