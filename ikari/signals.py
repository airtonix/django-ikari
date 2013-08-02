import logging

from django.dispatch import Signal

from . import settings

logger = logging.getLogger(__name__)
logger.addHandler(settings.null_handler)

# Called by middleware on every request; If any receiver returns a
# HttpResponse instance, this instance will be returned from the
# request.
domain_request = Signal()
