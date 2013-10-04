from ..conf import settings
from ..loader import load_class


IKARI_SITE_CLASS_PATH = getattr(settings, 'IKARI_SITE_MODEL', None) or 'ikari.models.defaults.Site'

Site = load_class(IKARI_SITE_CLASS_PATH, 'ikari')
