import os

from .base_loader import BaseLoader


class EnvironLoader(BaseLoader):
    def has_key(self):
        return self.flat_key in os.environ

    def get_value(self):
        return os.environ[self.flat_key]
