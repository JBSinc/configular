import pytest
import redis

try:
    from credstash import ItemNotFound
except ImportError:
    # If credstash isn't installed we can't fake it's Exceptions
    ItemNotFound = Exception

from django.conf import settings


class FakeCredstash:
    def __init__(self, vals={}):
        self.stash = vals

    def putSecret(self, key, val):
        self.stash[key] = val

    def getSecret(self, key):
        try:
            return self.stash[key]
        except KeyError:
            raise ItemNotFound


@pytest.fixture(scope="session")
def redis_conn():
    return redis.Redis(host=settings.CONSTANCE_REDIS_CONNECTION["host"])


@pytest.fixture
def redisdb(redis_conn):
    yield redis_conn
    redis_conn.flushdb()


@pytest.fixture
def credstash(mocker, settings):
    # Ensure credstash is fresh on each test
    fake_credstash = mocker.patch(
        "configular.credstash_manager.credstash",
        FakeCredstash({settings.THE_SECRET_KEY: settings.THE_SECRET_VALUE}),
    )
    yield fake_credstash


@pytest.fixture
def no_credstash(mocker):
    mocker.patch(
        "configular.credstash_manager.credstash",
        None,
    )
    yield
