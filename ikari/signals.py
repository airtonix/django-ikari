from django.dispatch import Signal

# Called by middleware on every request; If any receiver returns a
# HttpResponse instance, this instance will be returned from the
# request.
domain_request = Signal()

