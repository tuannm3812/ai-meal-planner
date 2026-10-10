"""This process's identity, returned on every response as X-Instance-Id (G6)."""

from uuid import uuid4

INSTANCE_HEADER = "X-Instance-Id"

INSTANCE_ID = str(uuid4())
"""Random per-process id, returned as X-Instance-Id.

Lets a client tell which instance answered when one URL is spread across
several, as on Cloud Run. It is random, so it reveals no host name, IP or other
environment detail."""
