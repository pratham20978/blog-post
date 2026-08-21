"""The generic registry. Explicit registration, duplicate-rejecting.

Every registry in the system is an instance of this: parsers, renderers, tools,
capabilities, profiles.

No importlib binding by dotted filename. In the old repo tools were bound by
literal filename through importlib, which is why ``processingg.tools.py`` and
``document-buiilder.py`` are load-bearing typos. Registration is explicit
Python, so renaming a file is a rename and not a breakage (R2).
"""

from __future__ import annotations

from collections.abc import Iterable, Iterator


class DuplicateRegistrationError(RuntimeError):
    """Raised at application assembly, never at request time.

    A duplicate that silently replaced would mean the behaviour of the system
    depends on import order.
    """


class Registry[K, V]:
    """Resolve a value by key. Registration happens once, in bootstrap.py."""

    def __init__(self, name: str, entries: Iterable[tuple[K, V]] = ()) -> None:
        self._name = name
        self._entries: dict[K, V] = {}
        for key, value in entries:
            self.register(key, value)

    def register(self, key: K, value: V) -> None:
        if key in self._entries:
            raise DuplicateRegistrationError(f"{self._name}: already registered: {key!r}")
        self._entries[key] = value

    def resolve(self, key: K) -> V | None:
        return self._entries.get(key)

    def registered_keys(self) -> tuple[K, ...]:
        """Stably ordered, so startup reconciliation reports the same way twice.

        Sorted by ``repr`` rather than by the key itself: ``K`` is unconstrained
        and need not be orderable, and requiring a ``SupportsRichComparison``
        bound here would force every registry key to be sortable for the sake of
        one diagnostic. ``repr`` is defined for every object.
        """
        return tuple(sorted(self._entries, key=repr))

    def __contains__(self, key: object) -> bool:
        return key in self._entries

    def __len__(self) -> int:
        return len(self._entries)

    def __iter__(self) -> Iterator[K]:
        return iter(self._entries)

    def __repr__(self) -> str:
        return f"Registry({self._name!r}, {len(self._entries)} entries)"
