import logging

logger = logging.getLogger(__name__)


class BaseSecretManager:
    def __init__(self, ignore_errors=False, fail_on_error=True):
        self.ignore_errors = ignore_errors
        self.fail_on_error = fail_on_error

    def get_secret(self, key):
        """Return the secret value if found or None."""
        try:
            return self.do_get_secret(key)
        except Exception:
            if not self.ignore_errors:
                logger.exception(f"Secret lookup failed in {self.__class__}")
            if self.fail_on_error:
                raise
            return None

    def do_get_secret(self, key):
        raise NotImplementedError
