#!/usr/bin/env python3
"""
Unit Test: Prevent Regression of Collapsed Biological Taxa
Ensures that no species in data/species_list.json or data/species_taxonomy_catalog.json
has its common name collapsed to an umbrella animal term (e.g. 'Fiddler Crab', 'Barn Owl', 'Electric Eel').
"""

import os
import sys
import json
import unittest

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CATALOG_PATH = os.path.join(BASE_DIR, "data", "species_taxonomy_catalog.json")
SPECIES_LIST_PATH = os.path.join(BASE_DIR, "data", "species_list.json")
AUDIT_JSON = os.path.join(BASE_DIR, "docs", "AUDIT_COLLAPSED_ORGANISMS.json")

class TestCollapsedTaxa(unittest.TestCase):

    def setUp(self):
        with open(CATALOG_PATH, "r", encoding="utf-8") as f:
            self.catalog = json.load(f)
        with open(SPECIES_LIST_PATH, "r", encoding="utf-8") as f:
            self.species_list = json.load(f)
        with open(AUDIT_JSON, "r", encoding="utf-8") as f:
            self.audit_items = json.load(f)

    def test_single_species_common_names_not_collapsed(self):
        """Test that single species binomials have their distinct biological common names."""
        cat_by_sci = {s["scientific"]: s for s in self.catalog}

        for item in self.audit_items:
            sci = item["species_scientific"]
            expected_distinct = item["restored_species_common"]
            self.assertIn(sci, cat_by_sci, f"Species {sci} missing from catalog")
            actual_common = cat_by_sci[sci]["common"]
            self.assertEqual(
                actual_common,
                expected_distinct,
                f"Species {sci} has collapsed common name '{actual_common}', expected '{expected_distinct}'"
            )

    def test_umbrella_taxa_exist_independently(self):
        """Test that every umbrella taxon exists as its own higher-level record."""
        cat_by_sci = {s["scientific"]: s for s in self.catalog}

        for item in self.audit_items:
            umb_sci = item["umbrella_scientific"]
            umb_common = item["umbrella_common"]
            umb_rank = item["umbrella_rank"]
            self.assertIn(umb_sci, cat_by_sci, f"Umbrella taxon {umb_sci} missing from catalog")
            self.assertEqual(cat_by_sci[umb_sci]["rank"], umb_rank, f"Taxon {umb_sci} has wrong rank")
            self.assertEqual(cat_by_sci[umb_sci]["common"], umb_common, f"Taxon {umb_sci} has wrong common name")

    def test_species_list_contains_both_distinct_and_umbrella(self):
        """Test that species_list.json includes both the distinct species and the umbrella taxon."""
        species_set = set(self.species_list)

        for item in self.audit_items:
            spec_entry = f"{item['restored_species_common']} ({item['species_scientific']})"
            umb_entry = f"{item['umbrella_common']} ({item['umbrella_scientific']})"
            self.assertIn(spec_entry, species_set, f"Distinct species entry '{spec_entry}' missing from species_list.json")
            self.assertIn(umb_entry, species_set, f"Umbrella taxon entry '{umb_entry}' missing from species_list.json")

if __name__ == "__main__":
    unittest.main()
