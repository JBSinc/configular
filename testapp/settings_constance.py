import os

from settings import (  # noqa: F401
    INSTALLED_APPS,
    SECRET_KEY,
    THE_SECRET_KEY,
    THE_SECRET_VALUE,
)

INSTALLED_APPS = INSTALLED_APPS + (
    # Constance blows up in django21 without the admin installed
    "django.contrib.admin",
    "django.contrib.contenttypes",
    "constance",
)

THE_ANSWER = 42

CONSTANCE_CONFIG = {
    "TEST_PREFIX_THE_ANSWER": (
        THE_ANSWER,
        "Answer to the Ultimate Question of Life, " "The Universe, and Everything",
    ),
    "TEST_PREFIX_THE_SECRET": (f"%%{THE_SECRET_KEY}%%", "It's dangerous to go alone"),
}

CONSTANCE_REDIS_CONNECTION = {
    "host": os.environ.get("REDIS_HOST", "localhost"),
    "port": 6379,
    "db": 0,
}

CONSTANCE_REDIS_PREFIX = os.environ.get("TOX_ENV_NAME", "not_tox")
