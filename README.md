# Configular

Support hierarchical loading of application settings from a number of sources.

This is useful for libraries where you want to allow an including application to
provide configuration to your code from sources such as django settings,
constance, and environment values. Also supports additional custom sources. 

Supports optional retrieveal of secrets with values like `%%example_key%%`. If
no secrets managers are configured, and a value matching the format is
presented, a warning will be logged.

Common hierarchy of lookups, first defined will be used:

1. constance
2. settings.py
3. os.environ
4. Settings['key']

Any value found that is surrounded by `%%` will be processed by the configured
`secrets_managers`.

Settings values are assumed to be dynamic, Settings objects use callables to
retrieve the values at run time. This means specifically that changes in the
Constance admin will apply to any look ups made after the values are saved.

Secrets (at least in the `CredstashManager`) are assumed to be immutable. A
`functools.lru_cache` is used around the lookup for cost and performance. If
you have rotated the credentials (or need to reset the cache in tests) you can
call `flush_secret_cache` on your `CredstashManager` instance to reset the
`lru_cache`. This means a value of `%%secret%%` will look up the secured value
one time and cache it in memory until `flush_secret_cache` is called.

## Usage

```python
from configular import Settings
from configular.constance_loader import ConstanceLoader
from configular.credstash_manager import CredstashManager
from configular.django_loader import DjangoLoader
from configular.environ_loader import EnvironLoader

CM = CredstashManager()

loader_settings = Settings(
    {
        'A_SETTING': 'DEFAULT'
    },
    'TEST_PREFIX',
    loaders=[ConstanceLoader, DjangoLoader, EnvironLoader],
    secrets_managers=[CM],
)
```

To update the `loaders` and `secrets_managers` in a settings instance, call
`reconfigure`.

```python
from configular.credstash_manager import CredstashManager
from configular.django_loader import DjangoLoader
from configular.environ_loader import EnvironLoader

from myapp.conf import myapp_settings

myapp_settings.reconfigure(
    loaders=[DjangoLoader, EnvironLoader],
    secrets_managers=[CM],
)
```

### Configuration

Django settings must be defined in a dict named with the defined prefix

```python
TEST_PREFIX = {'A_SETTING': 'NEW_VALUE'}
```

[Constance](https://github.com/jazzband/django-constance) settings must be named
with the prefix leading followed by an underscore, e.g.

```python
CONSTANCE_CONFIG = {
    'TEST_PREFIX_A_SETTING': (True, 'A fine setting'),
}
```

A sublcass of `django.core.exceptions.ImproperlyConfigured` is provided that can be
used to enforce configuration during app startup.

```python
from configular.exceptions import ImproperlyConfigured

if loader_settings.MY_APP_VERSION not in ('2.25', '2.27'):
    raise ImproperlyConfigured(f'MY_APP_VERSION={MY_APP_VERSION} not supported')
```

or with a decorator for checking validation

```python
from configular.decorators import validate_setting

@validate_setting(
    settings=loader_settings,
    key='MY_APP_VERSION',
    validate_func=lambda my_app_version: my_app_version in ('2.25', '2.27'),
)
def func()
    ...
```

Constance settings take precedence over defined django settings. Trying to access
a setting that is not defined in your Settings object will raise `AttributeError`.

## Running tests locally

Ensure `tox` is installed. e.g. `pip install -g tox`

```
docker-compose up -d --build  # Tests require a running react server
tox
```
