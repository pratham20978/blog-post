"""What a capability is given.

Everything a capability needs arrives here. It holds no port, no repository and
no connection — a capability that could open one would need infrastructure to
test, and the entire value of this layer is that it does not.

``__repr__`` is overridden rather than relying on field-level flags: the payload
is document content, which is customer material in full, and a default dataclass
repr would put it in every traceback that passes through a check.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from pydantic import JsonValue

from blogs.contracts.common import NonEmptyStr, tags


@dataclass(frozen=True, slots=True)
class CapabilityContext:
    
    
    
    # here we can deing the some capabilth with in regardace to the reranking and internla it gets help for the enign 
    # email pipeline line or etc