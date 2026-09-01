"""Set the admin's console password from the environment.

The designed way to rotate it is ``POST {admin_prefix}/auth/password``, which
re-checks the current password — deliberately, so a stolen access token cannot
be escalated into permanent access. That leaves one situation with no way out:
the current password is genuinely unknown.

It is easy to arrive there. ``_seed_admin_password`` in ``bootstrap`` runs only
for a *freshly created* admin, so editing ``BLOGS_ADMIN_INITIAL_PASSWORD`` after
the first start changes nothing — the database keeps the old hash and the new
value silently does not work. That is the right behaviour (a restart must not
reset a password the admin has since changed) and it is also exactly how you
lock yourself out.

So this is the escape hatch, and it is honest about what it is: **it sets the
password without proving knowledge of the old one.** The only thing standing in
front of it is access to the database and the environment file — which is to
say, whoever runs this could already read and rewrite anything. It grants no
authority that the caller did not already have.

Every existing session is revoked, because ``set_admin_password`` revokes them:
if the password is being reset because it leaked, leaving its tokens alive would
defeat the reset.

Usage::

    python -m blogs.database.reset_admin_password
    python -m blogs.database.reset_admin_password --password 'new-secret'
"""

from __future__ import annotations

import argparse
import asyncio
import logging
import sys

from blogs.bootstrap import build_container, close_container
from blogs.core.logging import configure_logging
from blogs.core.settings import Settings

logger = logging.getLogger(__name__)


async def _run(password: str | None) -> int:
    settings = Settings()
    configure_logging(level=logging.INFO)

    resolved = password or (
        settings.admin_initial_password.get_secret_value()
        if settings.admin_initial_password
        else None
    )
    if not resolved:
        print(
            "reset-admin-password: no password given and BLOGS_ADMIN_INITIAL_PASSWORD "
            "is not set. Pass --password or set it in .env.",
            file=sys.stderr,
        )
        return 1

    container = await build_container(settings)
    try:
        async with container.uow.read() as uow:
            admin = await uow.users.get_admin()

        if admin is None:
            print(
                "reset-admin-password: no admin account exists. Set "
                "BLOGS_ADMIN_EMAIL and start the API once so it is seeded.",
                file=sys.stderr,
            )
            return 1

        await container.auth_service.set_admin_password(
            user_id=admin.id, password=resolved
        )
        # The address is printed because knowing which account was changed is
        # the whole point of the confirmation. The password never is.
        print(f"reset-admin-password: password set for {admin.email}")
        print("Every existing admin session has been signed out.")
    finally:
        await close_container(container)

    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--password",
        help=(
            "the new password. Defaults to BLOGS_ADMIN_INITIAL_PASSWORD. "
            "Prefer the environment: an argument lands in your shell history."
        ),
    )
    args = parser.parse_args(argv)

    return asyncio.run(_run(args.password))


if __name__ == "__main__":
    raise SystemExit(main())
