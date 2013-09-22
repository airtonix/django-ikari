import logging

from django.dispatch import Signal

from .conf import settings, null_handler


logger = logging.getLogger(__name__)
logger.addHandler(null_handler)

# Called by middleware on every request; If any receiver returns a
# HttpResponse instance, this instance will be returned from the
# request.
domain_request = Signal()
