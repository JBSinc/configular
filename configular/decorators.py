from functools import wraps

from .exceptions import ImproperlyConfigured


class validate_setting(object):
    """Raise `ImproperlyConfigured if `config[key]` does not pass `validate_func`."""

    def __init__(self, config, key, validate_func):
        self.config = config
        self.key = key
        self.validate_func = validate_func

    def __call__(self, f):
        @wraps(f)
        def wrapped_f(*args, **kwargs):
            value = getattr(self.config, self.key)
            if not (self.validate_func(value)):
                raise ImproperlyConfigured(f"{self.key}={value} not supported.")
            return f(*args, **kwargs)

        return wrapped_f
