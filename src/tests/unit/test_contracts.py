"""The contract floor: totality, strictness, and the discriminated unions."""

from __future__ import annotations

import pytest
from pydantic import TypeAdapter, ValidationError

from blogs.api.envelope import HTTP_STATUS_BY_ERROR_CATEGORY, failure, status_for, success
from blogs.contracts.common import APIResponse, ContractModel, ErrorCategory
from blogs.contracts.identity import AnonymousPrincipal, Principal, UserPrincipal
from blogs.contracts.interaction import MarkerAnchor, OffsetAnchor, RangeAnchor, SectionAnchor
from blogs.core.errors import ERROR_CATALOG, BlogPlatformError

_ACTOR = "00000000-0000-7000-8000-000000000001"
_USER = "00000000-0000-7000-8000-000000000002"


class TestErrorCatalogTotality:
    """Both tables claim to be total by construction. These make it true.

    Without them the claim is a comment: a new ErrorCategory would sail through
    review and only fail in production, as a KeyError inside the exception
    handler — the one place an error must never itself error.
    """

    def test_every_category_has_a_descriptor(self) -> None:
        missing = [c.value for c in ErrorCategory if c not in ERROR_CATALOG]
        assert not missing, f"categories with no descriptor: {missing}"

    def test_every_category_has_a_status(self) -> None:
        missing = [c.value for c in ErrorCategory if c not in HTTP_STATUS_BY_ERROR_CATEGORY]
        assert not missing, f"categories with no HTTP status: {missing}"

    def test_every_status_is_a_client_or_server_error(self) -> None:
        # 304 is the only non-error status in the system and it never travels
        # as an envelope, so nothing here should be below 400.
        odd = {c.value: s for c, s in HTTP_STATUS_BY_ERROR_CATEGORY.items() if not 400 <= s <= 599}
        assert not odd, f"error categories mapped to non-error statuses: {odd}"

    def test_status_lookup_refuses_to_guess(self) -> None:
        """A `.get(..., 500)` default would hide a missing mapping forever."""
        with pytest.raises(KeyError):
            status_for("NOT_A_CATEGORY")  # type: ignore[arg-type]


class TestEnvelope:
    def test_success_carries_no_error(self) -> None:
        response = success({"value": 1})
        assert response.success and response.error is None

    def test_failure_carries_no_data(self) -> None:
        envelope = BlogPlatformError(
            ErrorCategory.BLOG_NOT_FOUND, correlation_id="abc"
        ).to_envelope()
        response = failure(envelope)
        assert not response.success
        assert response.data is None
        assert response.error is not None

    def test_a_success_with_an_error_is_unconstructable(self) -> None:
        envelope = BlogPlatformError(
            ErrorCategory.INTERNAL_ERROR, correlation_id="abc"
        ).to_envelope()
        with pytest.raises(ValidationError):
            APIResponse[str](success=True, message="ok", data="x", error=envelope)

    def test_a_failure_without_an_error_is_unconstructable(self) -> None:
        with pytest.raises(ValidationError):
            APIResponse[str](success=False, message="no", data=None, error=None)

    def test_correlation_id_may_be_stamped_by_the_transport(self) -> None:
        """A repository raises without one; the handler supplies it."""
        error = BlogPlatformError(ErrorCategory.SLUG_CONFLICT)
        assert error.correlation_id is None
        assert error.to_envelope(correlation_id="from-request").correlation_id == "from-request"

    def test_an_envelope_can_never_lack_a_correlation_id(self) -> None:
        with pytest.raises(ValueError, match="correlation id"):
            BlogPlatformError(ErrorCategory.SLUG_CONFLICT).to_envelope()


class TestStrictness:
    def test_unknown_fields_are_rejected_not_ignored(self) -> None:
        """`extra="ignore"` is how a renamed field becomes a silent default."""

        class Sample(ContractModel):
            known: int

        with pytest.raises(ValidationError):
            Sample(known=1, unknwon=2)  # type: ignore[call-arg]

    def test_contracts_are_immutable(self) -> None:
        principal = AnonymousPrincipal(actor_id=_ACTOR)
        with pytest.raises(ValidationError):
            principal.actor_id = _USER  # type: ignore[misc]


class TestPrincipalUnion:
    """Every principal has an actor id — that is what makes the anonymous path
    the same code path rather than a special case."""

    def test_both_principals_carry_an_actor(self) -> None:
        anon = AnonymousPrincipal(actor_id=_ACTOR)
        user = UserPrincipal(actor_id=_ACTOR, user_id=_USER, is_admin=False)
        assert anon.actor_id == user.actor_id == _ACTOR

    def test_anonymous_is_never_admin_and_has_no_user(self) -> None:
        anon = AnonymousPrincipal(actor_id=_ACTOR)
        assert anon.user_id is None
        assert anon.is_admin is False

    def test_the_union_discriminates_on_kind(self) -> None:
        adapter: TypeAdapter[Principal] = TypeAdapter(Principal)
        assert isinstance(
            adapter.validate_python({"kind": "anonymous", "actor_id": _ACTOR}), AnonymousPrincipal
        )
        assert isinstance(
            adapter.validate_python(
                {"kind": "user", "actor_id": _ACTOR, "user_id": _USER, "is_admin": True}
            ),
            UserPrincipal,
        )


class TestMarkerAnchorUnion:
    """Doc 01 open question 3 offered three representations. All three exist,
    and the round trip through jsonb has to preserve which one it was."""

    @pytest.mark.parametrize(
        "payload,expected",
        [
            ({"kind": "section", "anchor": "why-it-works"}, SectionAnchor),
            ({"kind": "offset", "char_offset": 512}, OffsetAnchor),
            (
                {"kind": "range", "start_anchor": "a-b", "end_anchor": "c-d"},
                RangeAnchor,
            ),
        ],
    )
    def test_each_kind_round_trips(self, payload: dict, expected: type) -> None:
        adapter: TypeAdapter[MarkerAnchor] = TypeAdapter(MarkerAnchor)
        anchor = adapter.validate_python(payload)
        assert isinstance(anchor, expected)
        assert adapter.validate_python(anchor.model_dump(mode="json")) == anchor

    def test_an_unknown_kind_is_refused(self) -> None:
        adapter: TypeAdapter[MarkerAnchor] = TypeAdapter(MarkerAnchor)
        with pytest.raises(ValidationError):
            adapter.validate_python({"kind": "xpath", "value": "//div"})

    def test_progress_ratio_is_bounded(self) -> None:
        from blogs.contracts.interaction import Marker

        with pytest.raises(ValidationError):
            Marker(
                user_id=_USER,
                blog_id=_ACTOR,
                anchor=OffsetAnchor(char_offset=0),
                progress_ratio=1.5,
                updated_at="2026-08-22T12:00:00Z",  # type: ignore[arg-type]
            )
