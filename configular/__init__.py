import logging
import re
from importlib.metadata import PackageNotFoundError, version
from typing import List

from .base_secret_manager import BaseSecretManager

try:
    __version__ = version("configular")
except PackageNotFoundError:
    # package is not installed
    __version__ = "Unknown"
    pass


logger = logging.getLogger(__name__)

SECRET_KEY_RE = re.compile(r"(%%[^$]*%%)")

warn_about_constance = True
warn_about_django = True


class Settings:
    def __init__(
        self,
        defaults: dict,
        prefix: str,
        loaders: List[type] = None,
        secrets_managers: List[BaseSecretManager] = None,
    ):
        self.defaults = defaults
        self.prefix = prefix

        self.reconfigure(
            loaders=loaders or [],
            secrets_managers=secrets_managers or [],
        )

    def reconfigure(
        self,
        *,
        loaders: List[type] = None,
        secrets_managers: List[BaseSecretManager] = None,
    ):
        """Update `loaders` and/or `secrets_managers`, and reset lookups."""

        if loaders is not None:
            self.loaders = loaders

        if secrets_managers is not None:
            self.secrets_managers = secrets_managers

        self._lookups = {}
        self._init = False

    def __getattr__(self, name):
        if not self._init:
            self._setup(self.defaults, self.prefix)

        if name in self._lookups:
            return self._lookups[name]()

        raise AttributeError(f"No setting {name}")

    def __dir__(self):
        return list(self.defaults)

    def _setup(self, defaults, prefix):
        if self._init:
            return

        for key, default in defaults.items():

            for LoaderClass in self.loaders:
                # Find the first loader that supports the key
                loader = LoaderClass(prefix, key)
                if loader.has_key():  # noqa: W601
                    break
            else:
                loader = None

            if loader is not None:
                self._lookups[key] = SecretScanner(
                    loader.get_value, self.secrets_managers
                )
            else:
                # No loader found -> use the Settings default value
                self._lookups[key] = SecretScanner(
                    # Build a closure for current value of default
                    (lambda d: lambda: d)(default),
                    self.secrets_managers,
                )

        self._init = True


class SecretScanner:
    def __init__(self, value_func, secrets_managers=None):
        self.value_func = value_func
        self.secrets_managers = secrets_managers or []

    def __call__(self):
        value = self.value_func()

        if not self.secrets_managers:
            try:
                if SECRET_KEY_RE.match(value):
                    logger.warning(
                        f"Managed secret style value found, but no managers configured. {value}"
                    )
            except TypeError:
                pass
            return value

        try:
            secret_value = SECRET_KEY_RE.sub(
                lambda m: self.get_secret(m.group().replace("%", "")),
                value,
            )
        except TypeError:
            # Value wasn't suitable for regex'ing
            return value

        if secret_value == "":
            logger.warning(f"Managed secret empty or not found in any manager. {value}")
            return value
        return secret_value

    def get_secret(self, key):
        """return value from first matching secrets_manager or '' if non-existent."""
        for sm in self.secrets_managers:
            val = sm.get_secret(key)
            if val is not None:
                return val
        return ""
