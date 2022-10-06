import logging

logger = logging.getLogger(__name__)

try:
    from django.core.exceptions import ImproperlyConfigured as ImproperlyConfiguredBase
except ImportError:
    logger.warning("django.core not found, ImproperlyConfigured subclasses Exception")
    ImproperlyConfiguredBase = Exception


class ImproperlyConfigured(ImproperlyConfiguredBase):
    pass
