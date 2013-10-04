import logging

from django.views.generic import TemplateView, FormView
from django.utils.translation import ugettext_lazy as _

from .conf import settings
from .utils import null_handler

logger = logging.getLogger(__name__)
logger.addHandler(null_handler)


class DomainErrorView(TemplateView):
    template_name = "ikari/error.html"


class SiteHomeView(TemplateView):
    template_name="ikari/site.html"

    def get_context_data(self, **kwargs):
        return {
            "Site": self.request.site
        }


class SiteUpdateView(FormView):
    template_name="ikari/site-config.html"


