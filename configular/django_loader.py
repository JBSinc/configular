import logging

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from .base_loader import BaseLoader

logger = logging.getLogger(__name__)
warn_about_django = True


class DjangoLoader(BaseLoader):
    def __init__(self, prefix, key):
        super().__init__(prefix, key)

        self.django_settings = {}
        try:
            self.django_settings = getattr(settings, prefix, {})
        except ImproperlyConfigured:
            global warn_about_django
            if warn_about_django:
                logger.warning(
                    "Django loaded, but settings module not specified. "
                    "Will not use Django settings."
                )

            warn_about_django = False

    def has_key(self):
        return self.key in self.django_settings

    def get_value(self):
        return self.django_settings[self.key]
