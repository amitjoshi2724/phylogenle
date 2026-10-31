#!/usr/bin/env python3
"""
Unit tests to guarantee that search and catalog results across Phylogenle
do not have artificial truncation (e.g. 100-match cap or 60-day cap),
and that full results are browseable using scrollbars.
"""

import json
import os
import re
import unittest

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class TestUntruncatedSearch(unittest.TestCase):
    def setUp(self):
        self.script_js_path = os.path.join(ROOT_DIR, "script.js")
        with open(self.script_js_path, "r", encoding="utf-8") as f:
            self.script_content = f.read()

        self.catalog_json_path = os.path.join(ROOT_DIR, "data", "species_taxonomy_catalog.json")

    def test_no_hardcoded_search_caps(self):
        """Ensure no 'matches.length >= 100 break;' exists in script.js search handlers."""
        self.assertNotIn("matches.length >= 100", self.script_content)
        self.assertNotIn("Showing top 100", self.script_content)

    def test_catalog_infinite_scroll_chunking(self):
        """Verify chunked progressive scrolling is attached to avoid truncation."""
        self.assertIn("CATALOG_SEARCH_CHUNK_SIZE", self.script_content)
        self.assertIn("handleCatalogSearchScroll", self.script_content)
        self.assertIn("renderCatalogSearchRowsHtml", self.script_content)

    def test_catalog_matches_full_count_for_frog(self):
        """Verify that high-volume searches (like 'frog') match all >2000 species."""
        with open(self.catalog_json_path, "r", encoding="utf-8") as f:
            catalog = json.load(f)

        query = "frog"
        fields = ['common', 'scientific', 'genus', 'family', 'order', 'class', 'phylum', 'kingdom', 'domain']
        matches = [
            item for item in catalog
            if any(query in str(item.get(k, '')).lower() for k in fields)
        ]

        self.assertGreater(len(matches), 2000, f"Expected >2000 frog matches, got {len(matches)}")

    def test_archive_list_no_60_day_truncation(self):
        """Verify archive list iterates back to epoch without a hardcoded 60-day cap."""
        self.assertNotIn("for (let i = 0; i < 60; i++)", self.script_content)
        self.assertIn("EPOCH_DATE_STR", self.script_content)

    def test_search_bar_restored_on_game_init(self):
        """Verify search bar autocomplete-wrapper and buttons are restored on initGame."""
        self.assertIn("if (animalInput && animalInput.parentElement) animalInput.parentElement.style.display = '';", self.script_content)
        self.assertIn("if (inputSection) inputSection.style.display = 'flex';", self.script_content)
        self.assertIn("window.addEventListener('popstate'", self.script_content)

    def test_clade_search_indexing(self):
        """Verify phylogenetic clades like Muroidea and Tetrapoda are indexed and searchable."""
        self.assertIn("buildCatalogCladeIndex", self.script_content)
        self.assertIn("catalogCladeIndex", self.script_content)
        self.assertIn("getTaxonVariants", self.script_content)
        self.assertIn("catalog-clade-banner", self.script_content)

        tree_path = os.path.join(ROOT_DIR, "data", "phylogeny_tree.json")
        with open(tree_path, "r", encoding="utf-8") as f:
            tree = json.load(f)

        muroidea_node = None
        for nid, node in tree.get("nodes", {}).items():
            if node.get("name", "").lower() == "muroidea":
                muroidea_node = (int(nid), node)
                break

        self.assertIsNotNone(muroidea_node, "Muroidea node must exist in phylogeny_tree.json")
        nid, node = muroidea_node
        self.assertEqual(node.get("major_name"), "Rodentia")

        muroidea_species_count = sum(
            1 for sp, nids in tree.get("species", {}).items()
            if nid in nids
        )
        self.assertGreater(muroidea_species_count, 1000, f"Expected >1000 Muroidea species, got {muroidea_species_count}")


if __name__ == "__main__":
    unittest.main()
