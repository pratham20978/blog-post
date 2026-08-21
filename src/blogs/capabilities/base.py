"""Contract implemented by every reusable capability.

A capability is a **pure check over already-loaded context**: context in, result
out, no I/O. That purity is what lets the capability suite be exhaustive at
near-zero cost — no fakes, no fixtures, no event loop.

Distinct from a tool: a tool is an agent-callable action that may reach outward
through a port. A capability may not.

A capability never learns which profile selected it. Once it could, someone
would branch on document type inside it, and that is the 104-dead-stub directory
reappearing one level down (R1).
"""

from __future__ import annotations

from typing import Protocol

from ai_auditor.capabilities.context import CapabilityContext
from ai_auditor.configuration.models import CheckDefinition
from ai_auditor.contracts.common import NonEmptyStr
from ai_auditor.contracts.validation import CheckResult


class IntrinsicCapability(Protocol):
    """Evaluate one configured check for any compatible profile."""

    @property
    def check_id(self) -> NonEmptyStr:
        """The key this capability registers under, named by profiles."""
        ...

    def evaluate(
        self,
        context: CapabilityContext,
        definition: CheckDefinition,
    ) -> CheckResult:
        """Return an explicit result without persisting request data.

        Never return PASS for a check that could not run. ``CheckResult``
        enforces that at construction — NOT_EXECUTED and NOT_APPLICABLE are
        distinct outcomes and both require a reason where applicable.
        """
        ...
