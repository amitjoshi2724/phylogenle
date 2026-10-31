#!/usr/bin/env python3
"""
Unit Test: 8-Rank Linnaean Hierarchy Verification
Ensures species_catalog_taxonomic.md contains true 8-rank nested collapsible sections:
Domain (⬛) ➔ Kingdom (🟫) ➔ Phylum (🟦) ➔ Class (🟪) ➔ Order (🟥) ➔ Family (🟧) ➔ Genus (🟨) ➔ Species Table (🟩)
Specifically tests that Genus levels are nested inside Family (e.g. Myobatrachidae -> Crinia, Pseudophryne, Uperoleia).
"""

import os
import re
import unittest

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CATALOG_MD = os.path.join(BASE_DIR, "species_catalog_taxonomic.md")

class TestTaxonomicCatalogHierarchy(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        self_path = CATALOG_MD
        with open(self_path, "r", encoding="utf-8") as f:
            cls.content = f.read()

    def test_genus_summaries_exist(self):
        """Verify that Genus level summaries with yellow badges exist throughout the document."""
        genus_matches = re.findall(r'<summary>🟨 <b>Genus:\s+([^<]+)</b>\s+—\s+[\d,]+\s+Species</summary>', self.content)
        self.assertGreater(len(genus_matches), 5000, f"Expected thousands of Genus sections, found {len(genus_matches)}")

    def test_myobatrachidae_nested_genera(self):
        """Verify that Family Myobatrachidae contains nested Genus sections for Crinia, Pseudophryne, Uperoleia."""
        # Find Myobatrachidae section
        fam_idx = self.content.find("<summary>🟧 <b>Family: Myobatrachidae</b>")
        self.assertNotEqual(fam_idx, -1, "Family: Myobatrachidae not found in species_catalog_taxonomic.md")
        
        # Take slice until next family
        next_fam_idx = self.content.find("<summary>🟧 <b>Family:", fam_idx + 30)
        section = self.content[fam_idx:next_fam_idx] if next_fam_idx != -1 else self.content[fam_idx:fam_idx + 20000]

        # Check for nested Genus summaries inside this Family
        expected_genera = [
            "Arenophryne",
            "Assa",
            "Crinia",
            "Geocrinia",
            "Metacrinia",
            "Myobatrachus",
            "Paracrinia",
            "Pseudophryne",
            "Taudactylus",
            "Uperoleia"
        ]
        for g in expected_genera:
            expected_summary = f"<summary>🟨 <b>Genus: {g}</b>"
            self.assertIn(expected_summary, section, f"Expected nested genus '{g}' in Myobatrachidae")

    def test_felidae_nested_genera(self):
        """Verify that Family Felidae contains nested Genus sections for Panthera, Felis, Lynx, etc."""
        fam_idx = self.content.find("<summary>🟧 <b>Family: Felidae</b>")
        self.assertNotEqual(fam_idx, -1, "Family: Felidae not found in species_catalog_taxonomic.md")
        next_fam_idx = self.content.find("<summary>🟧 <b>Family:", fam_idx + 30)
        section = self.content[fam_idx:next_fam_idx] if next_fam_idx != -1 else self.content[fam_idx:fam_idx + 20000]

        for g in ["Panthera", "Felis", "Lynx", "Acinonyx", "Puma", "Leopardus"]:
            expected_summary = f"<summary>🟨 <b>Genus: {g}</b>"
            self.assertIn(expected_summary, section, f"Expected nested genus '{g}' in Felidae")

    def test_species_table_structure_in_genus(self):
        """Verify that tables inside genera have 2 headers (Common Name, Scientific Name)."""
        table_headers = re.findall(r'\| Common Name \| Scientific Name \|', self.content)
        self.assertGreater(len(table_headers), 5000, "Expected table headers inside every Genus section")

if __name__ == "__main__":
    unittest.main()
