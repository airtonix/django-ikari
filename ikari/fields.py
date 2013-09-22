# http://www.djangosnippets.org/snippets/636/
import os
import uuid
import logging

from django import forms
from django.db import models
from django.utils.translation import ugettext as _
from django.utils.safestring import SafeUnicode
from django.core.urlresolvers import reverse, reverse_lazy

from .conf import settings, null_handler


logger = logging.getLogger(__name__)
logger.addHandler(null_handler)


class SubdomainInput(forms.TextInput):

    def render(self, *args, **kwargs):
        self.attrs = {"style": "width: 10em; display:inline-block;"}
        return SafeUnicode(
            super(SubdomainInput, self).render(*args, **kwargs)
            + app_settings.SUBDOMAIN_ROOT)


class UUIDField(models.CharField):
    # http://djangosnippets.org/snippets/1262/

    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = kwargs.get('max_length', 64)
        kwargs['blank'] = True
        models.CharField.__init__(self, *args, **kwargs)

    def pre_save(self, model_instance, add):
        if add:
            value = str(uuid.uuid4())
            setattr(model_instance, self.attname, value)
            return value
        else:
            return super(models.CharField, self).pre_save(model_instance, add)
