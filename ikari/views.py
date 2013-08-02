import logging

from django.views.generic import TemplateView

from . import settings

logger = logging.getLogger(__name__)
logger.addHandler(settings.null_handler)


class DomainErrorView(TemplateView):
    template_name = "domains/error.html"
