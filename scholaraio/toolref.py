"""Compatibility shim for the refactored toolref package.

The implementation now lives under ``scholaraio.toolref`` package modules.
This module re-exports the public and test-touched symbols so existing imports
such as ``from scholaraio.toolref import toolref_fetch`` keep working.
"""

from __future__ import annotations

from scholaraio.toolref import *  # noqa: F403
