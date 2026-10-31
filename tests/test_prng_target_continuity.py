import unittest
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


class TestTargetContinuity(unittest.TestCase):
    def test_oct_31_pinned_to_flatjaw_minnow(self):
        prng_js = (ROOT / "prng.js").read_text(encoding="utf-8")
        self.assertIn("2026-10-31", prng_js)
        self.assertIn("flatjaw minnow (tampichthys mandibularis)", prng_js.lower())

    def test_active_session_locks_target_species(self):
        script_js = (ROOT / "script.js").read_text(encoding="utf-8")
        self.assertIn("targetSpecies = savedTargetSpecies", script_js)


if __name__ == "__main__":
    unittest.main()
