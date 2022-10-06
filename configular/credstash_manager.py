from functools import lru_cache

import credstash
from credstash import ItemNotFound

from .base_secret_manager import BaseSecretManager


class CredstashManager(BaseSecretManager):
    @lru_cache(maxsize=None)
    def do_get_secret(self, key):
        try:
            return credstash.getSecret(key)
        except ItemNotFound:
            return None

    def flush_secret_cache(self):
        self.do_get_secret.cache_clear()
