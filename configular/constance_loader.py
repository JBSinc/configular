import logging

from constance import config as constance_config
from django.conf import settings  # noqa: F401
from django.db.utils import ProgrammingError

try:
    import pytest
except ImportError:
    pytest = object()

from .base_loader import BaseLoader

logger = logging.getLogger(__name__)
warn_about_constance = True


class ConstanceLoader(BaseLoader):
    def has_key(self):
        # If the key is in constance, the default from defaults cannot be reached
        constance_has_key = False

        if not getattr(pytest, "_in_test", False):
            try:
                constance_has_key = hasattr(constance_config, self.flat_key)
            except ProgrammingError:
                global warn_about_constance
                if warn_about_constance:
                    logger.warning(
                        "Settings loaded before the database is initialized. "
                        "Constance values will not be available."
                    )

                warn_about_constance = False
        return constance_has_key

    def get_value(self):
        return getattr(constance_config, self.flat_key)
