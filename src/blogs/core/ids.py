"""Identifier generation as a seam.

UUIDv7 rather than v4: the first 48 bits are a millisecond timestamp, so ids
generated in sequence sort in creation order. That matters for the append-heavy
tables here — a v4 primary key scatters inserts across the whole B-tree and
dirties a new page almost every time, while a v7 key appends to the rightmost
leaf. On ``engagement_events``, which is the highest-write table in the system,
that is the difference between an index that stays compact and one that bloats.

They remain opaque to consumers: foundation §9 says ids carry no cross-context
meaning, and "roughly time-ordered" is a storage property, not a contract.

``uuid.uuid7`` is standard library as of Python 3.13, so this costs nothing.
"""

from __future__ import annotations

from typing import Protocol
from uuid import UUID, uuid4, uuid7


class IdGenerator(Protocol):
    def new_id(self) -> str: ...


class Uuid7Generator:
    """The production generator."""

    def new_id(self) -> str:
        return str(uuid7())


class SequentialIdGenerator:
    """A deterministic generator for tests.

    Produces valid, ordered UUIDs from a counter, so a test can assert on exact
    ids without freezing the clock or mocking a module.
    """

    def __init__(self, seed: int = 0) -> None:
        self._counter = seed

    def new_id(self) -> str:
        self._counter += 1
        return str(UUID(int=self._counter, version=4))


def random_id() -> str:
    """A v4 id for values that must not be time-ordered.

    Used where the id is a secret or a correlation handle rather than a row
    key — a token reference embedding its creation time leaks when it was made.
    """
    return str(uuid4())
