#!/usr/bin/env python3
"""Tests for the repository validator without third-party dependencies."""

from __future__ import annotations

import importlib.util
import shutil
import tempfile
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[2]
VALIDATOR_PATH = REPO / "scripts" / "validate_opinion_piece_engine.py"
SPEC = importlib.util.spec_from_file_location("opinion_validator", VALIDATOR_PATH)
assert SPEC and SPEC.loader
VALIDATOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VALIDATOR)


class ValidatorTests(unittest.TestCase):
    def test_repository_passes(self) -> None:
        self.assertEqual([], VALIDATOR.validate(REPO))

    def test_internal_installation_path_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            copy = Path(temp) / "repo"
            shutil.copytree(REPO, copy)
            target = copy / "references" / "source-safety.md"
            forbidden_path = "/root/" + ".codex/internal"
            target.write_text(target.read_text() + f"\n{forbidden_path}\n", encoding="utf-8")
            errors = VALIDATOR.validate(copy)
            self.assertTrue(any("internal installation path" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
