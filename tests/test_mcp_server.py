"""Contract tests for MCP server parameter mapping logic.

Verifies: parameter adapter functions produce correct values before
delegating to underlying library calls.
Does NOT test: BERTopic model building, MCP protocol, or external APIs.
"""

from __future__ import annotations

import sys
import types
from unittest.mock import MagicMock

import pytest

# Stub the `mcp` package so mcp_server can be imported without the real SDK.
_mcp_stub = types.ModuleType("mcp")
_mcp_stub.server = types.ModuleType("mcp.server")
_mcp_stub.server.fastmcp = types.ModuleType("mcp.server.fastmcp")
_mcp_stub.server.fastmcp.FastMCP = MagicMock()
sys.modules.setdefault("mcp", _mcp_stub)
sys.modules.setdefault("mcp.server", _mcp_stub.server)
sys.modules.setdefault("mcp.server.fastmcp", _mcp_stub.server.fastmcp)

from scholaraio.mcp_server import _map_nr_topics  # noqa: E402


class TestBuildTopicsNrTopicsMapping:
    """nr_topics adapter: int sentinel → BERTopic-expected value."""

    @pytest.mark.parametrize(
        "nr_topics, expected",
        [
            (0, "auto"),  # default: automatic topic merging/reduction
            (-1, None),  # explicit: no reduction, keep HDBSCAN clusters
            (5, 5),  # explicit target count: passed through unchanged
            (20, 20),
        ],
    )
    def test_mapping(self, nr_topics: int, expected):
        assert _map_nr_topics(nr_topics) == expected
