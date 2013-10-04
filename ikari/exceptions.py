class SiteErrorException(Exception):
    pass


class SiteErrorInactive(SiteErrorException):
    pass


class SiteErrorIsPrivate(SiteErrorException):
    pass


class SiteErrorDoesNotExist(SiteErrorException):
    pass


class SiteErrorUnknown(SiteErrorException):
    pass
