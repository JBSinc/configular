import pytest

from configular import Settings
from configular.base_secret_manager import BaseSecretManager

# BaseSecretManager.do_get_secret() will raise NotImplementedError triggering
# the exception handling code. These tests exist for coverage of those paths.


def test_log_errors_and_fail_by_default(mocker):
    loader_settings = Settings(
        {"FISH": "%%fish%%"}, "TEST_PREFIX", secrets_managers=[BaseSecretManager()]
    )
    mock_logger = mocker.patch("configular.base_secret_manager.logger")

    with pytest.raises(NotImplementedError):
        loader_settings.FISH
    mock_logger.exception.assert_called_once()


def test_log_errors_and_continue(mocker):
    loader_settings = Settings(
        {"FISH": "%%fish%%"},
        "TEST_PREFIX",
        secrets_managers=[BaseSecretManager(fail_on_error=False)],
    )
    mock_logger = mocker.patch("configular.base_secret_manager.logger")

    assert loader_settings.FISH == "%%fish%%"
    mock_logger.exception.assert_called_once()


def test_no_log_errors_and_continue(mocker):
    loader_settings = Settings(
        {"FISH": "%%fish%%"},
        "TEST_PREFIX",
        secrets_managers=[BaseSecretManager(fail_on_error=False, ignore_errors=True)],
    )
    mock_logger = mocker.patch("configular.base_secret_manager.logger")

    assert loader_settings.FISH == "%%fish%%"
    mock_logger.exception.assert_not_called()


def test_no_log_errors_and_fail(mocker):
    loader_settings = Settings(
        {"FISH": "%%fish%%"},
        "TEST_PREFIX",
        secrets_managers=[BaseSecretManager(fail_on_error=True, ignore_errors=True)],
    )
    mock_logger = mocker.patch("configular.base_secret_manager.logger")

    with pytest.raises(NotImplementedError):
        loader_settings.FISH
    mock_logger.exception.assert_not_called()
