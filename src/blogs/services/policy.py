"""The authorization policy — every permission answer, in one place.

Doc 01 puts authorization in the application layer behind a policy port, and the
value of that is concentration: the rules are here, they are pure functions of a
principal, and a route cannot re-derive one slightly differently. A test can
enumerate the entire matrix without a database.

Three tiers, and the middle one is the interesting part:

* **Admin** — the single author. Publishes, edits, archives, pins, moderates,
  reads analytics.
* **User** — reads, comments, marks, saves. Doc 01 calls these accounts
  read-only, meaning they never author articles; they do own their own
  interactions.
* **Anonymous** — reads and generates engagement, nothing else. Engagement is
  deliberately allowed: it is what gives a visitor a history to inherit when
  they eventually sign in.
"""

from __future__ import annotations

from blogs.contracts.common import ErrorCategory
from blogs.contracts.identity import Principal, UserPrincipal
from blogs.core.errors import raise_error


def _is_admin(principal: Principal) -> bool:
    return isinstance(principal, UserPrincipal) and principal.is_admin


def _is_user(principal: Principal) -> bool:
    return isinstance(principal, UserPrincipal)


class DefaultAuthorizationPolicy:
    """Pure. No repository, no I/O, no async — so it is cheap to exhaust in tests."""

    # ── Admin-only ──────────────────────────────────────────────────────────
    def can_publish(self, principal: Principal) -> bool:
        return _is_admin(principal)

    def can_edit_blog(self, principal: Principal) -> bool:
        return _is_admin(principal)

    def can_archive_blog(self, principal: Principal) -> bool:
        return _is_admin(principal)

    def can_manage_pins(self, principal: Principal) -> bool:
        return _is_admin(principal)

    def can_manage_taxonomy(self, principal: Principal) -> bool:
        return _is_admin(principal)

    def can_read_analytics(self, principal: Principal) -> bool:
        return _is_admin(principal)

    def can_moderate(self, principal: Principal) -> bool:
        return _is_admin(principal)

    # ── Any signed-in account ───────────────────────────────────────────────
    def can_comment(self, principal: Principal) -> bool:
        return _is_user(principal)

    def can_mark(self, principal: Principal) -> bool:
        return _is_user(principal)

    def can_save(self, principal: Principal) -> bool:
        return _is_user(principal)

    # ── Everyone, including anonymous ───────────────────────────────────────
    def can_record_engagement(self, principal: Principal) -> bool:
        """True for anonymous visitors — that is the point of the actor id.

        Without this the log would only ever describe people who already have
        accounts, and every new user would start genuinely cold.
        """
        return True


def require(
    allowed: bool,
    *,
    principal: Principal,
    correlation_id: str | None = None,
) -> None:
    """Turn a policy answer into the right refusal.

    The distinction matters to a client: an anonymous caller should be told to
    sign in (401, ``AUTH_REQUIRED``) because retrying with credentials will
    work, while a signed-in non-admin should be told they lack permission (403)
    because retrying will not.
    """
    if allowed:
        return
    if isinstance(principal, UserPrincipal):
        raise_error(
            ErrorCategory.ADMIN_REQUIRED if not principal.is_admin else
            ErrorCategory.ACCESS_DENIED,
            correlation_id=correlation_id,
        )
    raise_error(ErrorCategory.AUTH_REQUIRED, correlation_id=correlation_id)
