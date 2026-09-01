"""Outbound email adapters."""

from blogs.adapters.email.memory import InMemoryEmailSender
from blogs.adapters.email.resend import ResendEmailSender
from blogs.adapters.email.unconfigured import UnconfiguredEmailSender

__all__ = ["InMemoryEmailSender", "ResendEmailSender", "UnconfiguredEmailSender"]
