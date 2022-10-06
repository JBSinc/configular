import importlib
import sys

import pytest
from django.core.exceptions import ImproperlyConfigured as DjangoImproperlyConfigured

from configular import exceptions


class FailLoader:
    def __init__(self, modules):
        self.modules = modules

    def find_module(self, fullname, path=None):
        if fullname in self.modules:
            raise ImportError(f"Test import failure for {fullname}")


def test_improperlyconfigured_subclasses_django():
    with pytest.raises(exceptions.ImproperlyConfigured) as exc:
        raise exceptions.ImproperlyConfigured

    assert issubclass(exc.type, DjangoImproperlyConfigured)


def test_improperlyconfigured_without_django():
    fail_loader = FailLoader(["django.core.exceptions"])
    sys.meta_path.append(fail_loader)
    del sys.modules["django.core.exceptions"]
    importlib.reload(exceptions)

    with pytest.raises(exceptions.ImproperlyConfigured) as exc:
        raise exceptions.ImproperlyConfigured

    assert not issubclass(exc.type, DjangoImproperlyConfigured)
    assert issubclass(exc.type, Exception)

    sys.meta_path.remove(fail_loader)
