import logging

from django.dispatch import Signal

from .conf import settings
from .utils import null_handler


logger = logging.getLogger(__name__)
logger.addHandler(null_handler)

# Called by middleware on every request; If any receiver returns a
# HttpResponse instance, this instance will be returned from the
# request.
site_request = Signal(providing_args=['site', 'request'])
site_created = Signal(providing_args=['site', ])
site_updated = Signal(providing_args=['site', ])
site_deleted = Signal(providing_args=['site', ])
