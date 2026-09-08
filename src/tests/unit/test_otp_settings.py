"""Configuration and wire defaults for real OTP delivery."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from blogs.api.routers.auth import OtpRequestAccepted, OtpVerifyBody
from blogs.contracts.identity import AuthPurpose
from blogs.core.settings import Settings
from blogs.services.auth_service import _otp_email


def _resend_settings(**overrides: object) -> Settings:
    values: dict[str, object] = {
        "email_provider": "resend",
        "resend_api_key": "re_test",
        "email_from": "Canerly <auth@canery.in>",
        "email_reply_to": None,
        "otp_log_codes": False,
        "otp_dev_bypass_code": None,
    }
    values.update(overrides)
    return Settings(_env_file=None, **values)  # type: ignore[call-arg]


class TestOtpVerifyContract:
    def test_request_response_has_no_credential_field(self) -> None:
        accepted = OtpRequestAccepted(
            expires_at="2026-09-09T12:10:00+00:00",
            resend_after="2026-09-09T12:01:00+00:00",
        )
        assert accepted.model_dump() == {
            "expires_at": "2026-09-09T12:10:00+00:00",
            "resend_after": "2026-09-09T12:01:00+00:00",
        }

    def test_omitted_purpose_defaults_to_login_for_old_clients(self) -> None:
        body = OtpVerifyBody(email="reader@example.com", code="123456")
        assert body.purpose is AuthPurpose.LOGIN

    def test_signup_purpose_is_preserved(self) -> None:
        body = OtpVerifyBody(
            email="reader@example.com", code="123456", purpose=AuthPurpose.SIGNUP
        )
        assert body.purpose is AuthPurpose.SIGNUP

    def test_unknown_purpose_is_rejected(self) -> None:
        with pytest.raises(ValidationError):
            OtpVerifyBody(  # type: ignore[arg-type]
                email="reader@example.com", code="123456", purpose="password-reset"
            )


class TestOtpEmailCopy:
    @pytest.mark.parametrize(
        ("purpose", "subject", "instruction"),
        [
            (
                AuthPurpose.LOGIN,
                "Your Canery sign-in code",
                "Use this code to sign in to Canery:",
            ),
            (
                AuthPurpose.SIGNUP,
                "Your Canery signup code",
                "Use this code to create your Canery account:",
            ),
        ],
    )
    def test_each_purpose_has_safe_multipart_copy(
        self,
        purpose: AuthPurpose,
        subject: str,
        instruction: str,
    ) -> None:
        message = _otp_email(
            email="reader@example.com",
            code="123456",
            purpose=purpose,
            minutes=10,
        )

        assert message.to == "reader@example.com"
        assert message.subject == subject
        assert "123456" not in message.subject
        assert instruction in message.text
        assert "123456" in message.text
        assert "expires in 10 minutes" in message.text
        assert message.html is not None
        assert instruction in message.html
        assert "123456" in message.html
        assert "can be used once" in message.html


class TestRealEmailSafety:
    def test_complete_resend_configuration_is_accepted(self) -> None:
        settings = _resend_settings()
        assert settings.email_from == "Canerly <auth@canery.in>"
        assert settings.email_reply_to is None

    @pytest.mark.parametrize(
        ("field", "value"),
        [("resend_api_key", ""), ("email_from", "")],
    )
    def test_blank_required_resend_values_are_rejected(self, field: str, value: str) -> None:
        with pytest.raises(ValidationError, match=field):
            _resend_settings(**{field: value})

    def test_resend_refuses_plaintext_otp_logging(self) -> None:
        with pytest.raises(ValidationError, match="must not be written to logs"):
            _resend_settings(otp_log_codes=True)

    def test_resend_refuses_a_fixed_bypass_code(self) -> None:
        with pytest.raises(ValidationError, match="must not have a fixed bypass"):
            _resend_settings(otp_dev_bypass_code="000000")

    def test_an_empty_compose_bypass_value_counts_as_unset(self) -> None:
        settings = _resend_settings(otp_dev_bypass_code="")
        assert settings.otp_dev_bypass_code is not None
        assert settings.otp_dev_bypass_code.get_secret_value() == ""
