import logging

from django.contrib.auth.decorators import login_required
from django.views.generic import View
from django.utils.decorators import method_decorator

from . import models
from . import settings


logger = logging.getLogger(__name__)
logger.addHandler(settings.null_handler)


class DomainViewMixin(object):
    model = models.Domain


class ProtectedView(View):

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ProtectedView, self).dispatch(*args, **kwargs)
