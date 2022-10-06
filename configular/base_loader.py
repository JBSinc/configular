class BaseLoader:
    def __init__(self, prefix, key):
        self.prefix = prefix
        self.key = key

    @property
    def flat_key(self):
        return f"{self.prefix}_{self.key}"

    def has_key(self):
        return False

    def get_value(self):
        raise NotImplementedError
