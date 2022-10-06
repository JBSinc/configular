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

Any value found that is surrounded by `%%` will be fetched from credstash (if installed).

## Usage

e.g.
```
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

### Configuration

Django settings must be defined in a dict named with the defined prefix

e.g.
```python
TEST_PREFIX = {'A_SETTING': 'NEW_VALUE'}
```

[Constance](https://github.com/jazzband/django-constance) settings must be named
with the prefix leading followed by an underscore, e.g.

e.g.
```python
CONSTANCE_CONFIG = {
    'TEST_PREFIX_A_SETTING': (True, 'A fine setting'),
}
```

A sublcass of `django.core.exceptions.ImproperlyConfigured` is provided that can be
used to enforce configuration during app startup.

e.g.
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
