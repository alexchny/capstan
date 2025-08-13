from __future__ import annotations

import json
from pathlib import Path

import pytest


def test_fixtures_jsonl_smoke() -> None:
    root = Path("tests/fixtures")
    files = sorted(root.rglob("*.jsonl"))
    assert files, "No fixtures found"
    for path in files:
        assert path.stat().st_size > 0, f"{path} is empty"
        with path.open("r") as f:
            for i, line in enumerate(f, 1):
                try:
                    json.loads(line)
                except Exception as e:
                    pytest.fail(f"{path}:{i}: {e}")
