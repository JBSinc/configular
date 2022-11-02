import os

import pytest
from django.core.management import call_command

from configular import Settings
from configular.constance_loader import ConstanceLoader
from configular.credstash_manager import CredstashManager
from configular.django_loader import DjangoLoader
from configular.environ_loader import EnvironLoader

CM = CredstashManager()

settings_kwargs = {
    "loaders": [ConstanceLoader, DjangoLoader, EnvironLoader],
    "secrets_managers": [CM],
}


def test_settings_load_without_constance(settings):
    # GIVEN config with all loaders
    loader_settings = Settings(
        {"THE_ANSWER": "DEFAULT"}, "TEST_PREFIX", **settings_kwargs
    )

    assert loader_settings.THE_ANSWER == settings.THE_ANSWER
    assert settings.THE_ANSWER != "DEFAULT"

    # WHEN reconfigured without constance
    loader_settings.reconfigure(
        loaders=[DjangoLoader, EnvironLoader],
    )

    # THEN the default value is show
    assert loader_settings.THE_ANSWER == "DEFAULT"


def test_django_settings(settings):
    settings.TEST_PREFIX = {"A_SETTING": "NEW_VALUE"}
    loader_settings = Settings(
        {"A_SETTING": "DEFAULT"}, "TEST_PREFIX", **settings_kwargs
    )

    assert loader_settings.A_SETTING == "NEW_VALUE"
    # Cover the _init flag short circut
    loader_settings._setup(None, None)


def test_django_settings_complex(settings):
    settings.TEST_PREFIX = {"A_SETTING": {"foo": "bar"}}
    loader_settings = Settings(
        {"A_SETTING": "DEFAULT"}, "TEST_PREFIX", **settings_kwargs
    )

    assert loader_settings.A_SETTING == {"foo": "bar"}


def test_environ_settings(settings, monkeypatch):
    monkeypatch.setenv("TEST_PREFIX_A_SETTING", "NEW_VALUE")
    loader_settings = Settings(
        {"A_SETTING": "DEFAULT"}, "TEST_PREFIX", **settings_kwargs
    )

    assert loader_settings.A_SETTING == "NEW_VALUE"


def test_environ_django_precedence(settings, monkeypatch):
    monkeypatch.setenv("TEST_PREFIX_A_SETTING", "environ")
    settings.TEST_PREFIX = {"A_SETTING": "django"}
    loader_settings = Settings(
        {"A_SETTING": "DEFAULT"}, "TEST_PREFIX", **settings_kwargs
    )

    assert loader_settings.A_SETTING == "django"


def test_looks_like_credstash(no_credstash, mocker, settings):
    # GIVEN no Secrets managers configured
    settings_kwargs = {
        "loaders": [ConstanceLoader, DjangoLoader, EnvironLoader],
    }
    settings.TEST_PREFIX = {"FISH": "%%fish%%"}
    loader_settings = Settings({"FISH": "thanks"}, "TEST_PREFIX", **settings_kwargs)
    mock_logger = mocker.patch("configular.logger")

    assert loader_settings.FISH == "%%fish%%"
    mock_logger.warning.assert_called_once()


def test_missing_secret(credstash, mocker, settings):
    loader_settings = Settings(
        {"FISH": "%%fish%%"}, "TEST_PREFIX", secrets_managers=[CM]
    )
    mock_logger = mocker.patch("configular.logger")

    assert loader_settings.FISH == "%%fish%%"
    mock_logger.warning.assert_called_once()


def test_non_string_value(credstash, settings):
    settings.TEST_PREFIX = {"FISH": 17}
    loader_settings = Settings({"FISH": 42}, "TEST_PREFIX", **settings_kwargs)

    assert loader_settings.FISH == 17


def test_settings_dir(settings):
    loader_settings = Settings(
        {"A_SETTING": "DEFAULT", "ANOTHER_SETTING": "AMAZING"},
        "TEST_PREFIX",
        **settings_kwargs,
    )

    assert dir(loader_settings) == ["ANOTHER_SETTING", "A_SETTING"]


def test_settings_raises_for_missing(settings):
    loader_settings = Settings(
        {"A_SETTING": "DEFAULT"}, "TEST_PREFIX", **settings_kwargs
    )

    with pytest.raises(AttributeError):
        loader_settings.FOO


@pytest.mark.skipif(
    os.environ.get("DJANGO_SETTINGS_MODULE") != "settings_constance",
    reason="requires constance to be installed when calling django.setup()",
)
@pytest.mark.usefixtures("no_credstash")
class TestWithConstance:
    def test_constance_settings(self, redisdb, settings):
        loader_settings = Settings({"THE_ANSWER": 21}, "TEST_PREFIX", **settings_kwargs)

        assert loader_settings.THE_ANSWER == settings.THE_ANSWER

    def test_constance_settings_reload(self, redisdb, settings):
        loader_settings = Settings({"THE_ANSWER": 21}, "TEST_PREFIX", **settings_kwargs)

        call_command("constance", "set", "TEST_PREFIX_THE_ANSWER", 0)

        assert loader_settings.THE_ANSWER == 0

    def test_constance_and_django_settings(self, redisdb, settings):
        settings.TEST_PREFIX = {"FISH": "goodbye"}
        loader_settings = Settings(
            {"THE_ANSWER": 21, "FISH": "thanks"}, "TEST_PREFIX", **settings_kwargs
        )

        call_command("constance", "set", "TEST_PREFIX_THE_ANSWER", 0)

        assert loader_settings.THE_ANSWER == 0
        assert loader_settings.FISH == "goodbye"

    def test_constance_and_django_settings_precedence(self, redisdb, settings):
        settings.TEST_PREFIX = {"THE_ANSWER": 13}
        loader_settings = Settings({"THE_ANSWER": 21}, "TEST_PREFIX", **settings_kwargs)

        assert loader_settings.THE_ANSWER == settings.THE_ANSWER


@pytest.mark.skipif(
    os.environ.get("DJANGO_SETTINGS_MODULE") != "settings_constance",
    reason="requires constance to be installed when calling django.setup()",
)
class TestWithCredstashAndConstance:
    def test_constance_settings(self, credstash, redisdb, settings):
        CM.flush_secret_cache()
        loader_settings = Settings(
            {"THE_SECRET": "Not a secret"}, "TEST_PREFIX", **settings_kwargs
        )

        assert loader_settings.THE_SECRET == settings.THE_SECRET_VALUE

    def test_constance_settings_reload(self, credstash, redisdb, settings):
        loader_settings = Settings(
            {"THE_SECRET": "Not a secret"}, "TEST_PREFIX", **settings_kwargs
        )

        call_command("constance", "set", "TEST_PREFIX_THE_SECRET", 0)

        # in constance the default value is an str(), so any value set will be str()
        assert loader_settings.THE_SECRET == "0"

        call_command(
            "constance",
            "set",
            "TEST_PREFIX_THE_SECRET",
            f"%%{settings.THE_SECRET_KEY}%%",
        )

        assert loader_settings.THE_SECRET == settings.THE_SECRET_VALUE

    def test_caching_credstash(self, redisdb, settings, mocker):
        CM.flush_secret_cache()
        mock_getSecret = mocker.patch(
            "configular.credstash_manager.credstash.getSecret", return_value="foo"
        )
        loader_settings = Settings(
            {"THE_SECRET": "Not Secret"}, "TEST_PREFIX", **settings_kwargs
        )

        # Any number of accesses for the same key
        assert loader_settings.THE_SECRET == "foo"
        assert loader_settings.THE_SECRET == "foo"
        assert loader_settings.THE_SECRET == "foo"
        # Only lookup from credstash once
        assert mock_getSecret.call_count == 1

        CM.flush_secret_cache()
        assert mock_getSecret.call_count == 1
        assert loader_settings.THE_SECRET == "foo"
        # until after the cache is flushed
        assert mock_getSecret.call_count == 2


class TestWithCredstash:
    def test_django_settings(self, credstash, settings):
        credstash.putSecret("fish", "goodbye")
        settings.TEST_PREFIX = {"FISH": "%%fish%%"}
        loader_settings = Settings({"FISH": "thanks"}, "TEST_PREFIX", **settings_kwargs)

        assert loader_settings.FISH == "goodbye"

    def test_django_settings_no_secrets(self, credstash, settings):
        # GIVEN normal config, with a secret
        credstash.putSecret("fish", "goodbye")
        settings.TEST_PREFIX = {"FISH": "%%fish%%"}
        loader_settings = Settings({"FISH": "thanks"}, "TEST_PREFIX", **settings_kwargs)

        # WHEN retrieved
        # THEN the secret value is found
        assert loader_settings.FISH == "goodbye"

        # WHEN reconfigured without a secret manager
        # THEN the key is found
        loader_settings.reconfigure(secrets_managers=[])
        assert loader_settings.FISH == "%%fish%%"

    def test_environ_value(self, credstash, monkeypatch):
        credstash.putSecret("fish", "goodbye")
        monkeypatch.setenv("TEST_PREFIX_FISH", "%%fish%%")
        loader_settings = Settings({"FISH": "thanks"}, "TEST_PREFIX", **settings_kwargs)

        assert loader_settings.FISH == "goodbye"

    def test_default_value(self, credstash):
        credstash.putSecret("fish", "goodbye")
        loader_settings = Settings(
            {"FISH": "%%fish%%"}, "TEST_PREFIX", **settings_kwargs
        )

        assert loader_settings.FISH == "goodbye"
