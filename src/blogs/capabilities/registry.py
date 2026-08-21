"""Explicit registry for reusable capabilities.

A thin wrapper over ``core.registry.Registry`` rather than a second hand-rolled
dict: duplicate rejection, key ordering and the error type are decided once, for
every registry in the system.

The only thing added here is that the key is *derived from the value* —
a capability knows its own ``check_id``, so registering it twice under different
names is not possible.
"""

from __future__ import annotations

from collections.abc import Iterable

from blogs.capabilities.base import IntrinsicCapability
from blogs.core.registry import Registry


class CapabilityRegistry:

    def __init__(self, capabilities: Iterable[IntrinsicCapability] = ()) -> None:
        self._registry: Registry[str, IntrinsicCapability] = Registry("capabilities")
        for capability in capabilities:
            self.register(capability)

    def register(self, capability: IntrinsicCapability) -> None:
        self._registry.register(capability.anytype of id or someitng if there onot , capability)

    def resolve(self, check_id: str) -> IntrinsicCapability | None:
        return self._registry.resolve(check_id)

    def registered_ids(self) -> tuple[str, ...]:
        return self._registry.registered_keys()

    def __contains__(self, check_id: object) -> bool:
        return check_id in self._registry

    def __len__(self) -> int:
        return len(self._registry)
