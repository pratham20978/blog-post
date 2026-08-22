"""Time as a seam.

Expiry, TTL and version logic are testable without sleeping. A ``FrozenClock``
in tests costs nothing and removes a whole class of flake.

``Clock`` lives in ``core/`` rather than ``ports/`` because it is not an
outside-the-process boundary — there is no adapter, no connection and nothing to
fail.

This is also the seam behind dwell measurement: the client reports how long it
spent on an article, the server stamps every engagement row from here, and F1
later normalises that dwell against the article's word count. Because both the
stamp and the expiry checks come from one injectable source, a test can replay
a whole reading session without sleeping.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Protocol


class Clock(Protocol):
    def now(self) -> datetime: ...


class SystemClock:
    """Wall clock, always timezone-aware and always UTC.

    Naive datetimes are the source of the "expired an hour early in summer" bug
    class; there is no code path here that can produce one.
    """

    def now(self) -> datetime:
        return datetime.now(UTC)


class FrozenClock:
    """A clock that only moves when a test moves it."""

    def __init__(self, start: datetime) -> None:
        if start.tzinfo is None:
            raise ValueError("FrozenClock requires a timezone-aware datetime")
        self._now = start

    def now(self) -> datetime:
        return self._now

    def advance(self, delta: timedelta) -> None:
        self._now += delta
