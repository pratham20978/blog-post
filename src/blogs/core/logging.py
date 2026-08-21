from __future__ import annotations

import json
import logging
import re
import sys
from typing import Final

_SENSITIVE_KEY_MARKERS: Final = (
    "password",
    "secret",
    "token",
    "authorization",
    "signature",
    "otp",
    "signed_url",
)

#: Values that look like secrets regardless of the key they arrived under.
_BEARER = re.compile(r"(?i)\bbearer\s+[A-Za-z0-9._\-]+")
_QUERY_SIG = re.compile(r"(?i)([?&](?:sig|signature|token|x-amz-signature)=)[^&\s]+")

_REDACTED: Final = "[REDACTED]"


def redact_text(value: str) -> str:
    """Scrub secret-shaped substrings from free text."""
    value = _BEARER.sub(f"Bearer {_REDACTED}", value)
    return _QUERY_SIG.sub(rf"\1{_REDACTED}", value)


def _is_sensitive(key: str) -> bool:
    lowered = key.lower()
    return any(marker in lowered for marker in _SENSITIVE_KEY_MARKERS)


class RedactingJsonFormatter(logging.Formatter):
    """One JSON object per line, with sensitive fields removed.

    Extra fields are read from ``record.__dict__`` so a caller can write
    ``logger.info("saved", extra={"document_id": did})`` and get a structured
    field rather than an interpolated string.
    """

    _RESERVED: Final = frozenset(logging.LogRecord("", 0, "", 0, "", None, None).__dict__) | {
        "message",
        "asctime",
        "taskName",
    }

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, object] = {
            "level": record.levelname,
            "logger": record.name,
            "message": redact_text(record.getMessage()),
        }

        for key, value in record.__dict__.items():
            if key in self._RESERVED:
                continue
            if _is_sensitive(key):
                payload[key] = _REDACTED
                continue
            payload[key] = redact_text(value) if isinstance(value, str) else repr(value)

        if record.exc_info is not None:
            payload["exception"] = redact_text(self.formatException(record.exc_info))

        return json.dumps(payload, default=repr)


def configure_logging(*, level: int = logging.INFO) -> None:
    """Install the redacting formatter as the only root handler.

    Replaces existing handlers rather than adding to them: a second handler with
    the default formatter would emit the unredacted line alongside the safe one.
    """
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(RedactingJsonFormatter())

    root = logging.getLogger()
    root.handlers = [handler]
    root.setLevel(level)
