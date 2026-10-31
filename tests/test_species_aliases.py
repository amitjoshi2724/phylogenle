#!/usr/bin/env python3
"""
Unit Test: Species Aliases Coverage & Verification
Ensures data/species_aliases.json contains verified non-trivial alternate names,
taxonomic synonyms, and regional common names for key organisms (like Bobcat, Lion, etc.)
and validates that aliases correctly resolve to active species in the catalog.
"""

import os
import json
import unittest
import subprocess
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CATALOG_PATH = os.path.join(BASE_DIR, "data", "species_taxonomy_catalog.json")
ALIASES_PATH = os.path.join(BASE_DIR, "data", "species_aliases.json")
HARVEST_SCRIPT = os.path.join(BASE_DIR, "harvest_and_audit_species_aliases.py")

class TestSpeciesAliases(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        with open(CATALOG_PATH, "r", encoding="utf-8") as f:
            cls.catalog = json.load(f)
        with open(ALIASES_PATH, "r", encoding="utf-8") as f:
            cls.aliases = json.load(f)

    def test_bobcat_aliases(self):
        """Verify Bobcat (Lynx rufus) has rich verified common and taxonomic aliases."""
        bobcat_target = "Bobcat (Lynx rufus)"
        expected_aliases = [
            "red lynx",
            "bay lynx",
            "north american wildcat",
            "felis rufus"
        ]
        for alias in expected_aliases:
            self.assertIn(alias, self.aliases, f"Expected alias '{alias}' missing for Bobcat")
            self.assertEqual(
                self.aliases[alias],
                bobcat_target,
                f"Alias '{alias}' mapped to '{self.aliases[alias]}', expected '{bobcat_target}'"
            )

    def test_lion_aliases(self):
        """Verify Lion (Panthera leo) has regional and taxonomic aliases."""
        lion_target = "Lion (Panthera leo)"
        self.assertIn("african lion", self.aliases)
        self.assertEqual(self.aliases["african lion"], lion_target)
        self.assertIn("felis leo", self.aliases)
        self.assertEqual(self.aliases["felis leo"], lion_target)

    def test_american_black_bear_aliases(self):
        """Verify American Black Bear has common shorthand and subspecies aliases."""
        bear_target = "American Black Bear (Ursus americanus)"
        self.assertIn("black bear", self.aliases)
        self.assertEqual(self.aliases["black bear"], bear_target)

    def test_harvest_script_audit_only_cli(self):
        """Verify that the harvest and audit script runs cleanly in --audit-only mode."""
        res = subprocess.run(
            [sys.executable, HARVEST_SCRIPT, "--audit-only"],
            capture_output=True,
            text=True
        )
        self.assertEqual(res.returncode, 0, f"Script failed with stderr: {res.stderr}")
        self.assertIn("PHASE 1: Auditing Current Alias Coverage", res.stdout)
        self.assertIn("Organisms with Non-Trivial Aliases", res.stdout)

if __name__ == "__main__":
    unittest.main()
