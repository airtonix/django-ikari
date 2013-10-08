from django.template.response import TemplateResponse


class TemplateErrorResponseNotFound(TemplateResponse):
    status_code = 404


class TemplateErrorResponseForbidden(TemplateResponse):
    status_code = 403


class TemplateErrorResponseBadRequest(TemplateResponse):
    status_code = 400
