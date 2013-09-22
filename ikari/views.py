import logging

from django.views.generic import TemplateView, FormView
from django.utils.translation import ugettext_lazy as _

from .conf import settings, null_handler

logger = logging.getLogger(__name__)
logger.addHandler(null_handler)


class DomainErrorView(TemplateView):
    template_name = "ikari/error.html"
    message = None

    def get_context_data(self, **kwargs):
        return kwargs.update({
            'message': self.message
            })

class SiteHomeView(TemplateView):
    template_name="ikari/site.html"


class SiteUpdateView(FormView):
    template_name="ikari/site-config.html"


