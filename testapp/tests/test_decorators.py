import pytest

from configular import Settings, decorators, exceptions


class TestValidateSettingDecorator:
    @staticmethod
    def get_settings():
        return Settings({"THE_ANSWER": 21}, "TEST_PREFIX")

    def test_validate_setting_passes(self, settings):
        @decorators.validate_setting(
            config=self.get_settings(), key="THE_ANSWER", validate_func=lambda x: True
        )
        def func():
            return "Hi"

        assert func() == "Hi"

    def test_constance_settings_fails(self, settings):
        @decorators.validate_setting(
            config=self.get_settings(), key="THE_ANSWER", validate_func=lambda x: False
        )
        def func():
            pass

        with pytest.raises(exceptions.ImproperlyConfigured):
            func()

    def test_validate_setting_without_func(self, settings):
        decorators.validate_setting(
            config=self.get_settings(), key="THE_ANSWER", validate_func=lambda x: True
        )
