"""OAuth capability discovery exposes names, never adapter credentials."""

from __future__ import annotations

from datetime import UTC, datetime

from blogs.contracts.identity import OAuthProviderName
from blogs.core.clock import FrozenClock
from blogs.core.registry import Registry
from blogs.services.oauth_flow_service import OAuthFlowService


def test_enabled_oauth_providers_are_stable_and_configuration_driven() -> None:
    providers: Registry[str, object] = Registry(
        "oauth-providers",
        (("github", object()), ("disabled-experiment", object()), ("google", object())),
    )
    service = OAuthFlowService(
        providers=providers,
        clock=FrozenClock(datetime(2026, 9, 8, tzinfo=UTC)),
        state_secret="test-state-secret-value-at-least-32-bytes",
        issuer="blogs-test",
        redirect_base_url="http://localhost:3001",
    )

    assert service.enabled_providers() == (
        OAuthProviderName.GOOGLE,
        OAuthProviderName.GITHUB,
    )
