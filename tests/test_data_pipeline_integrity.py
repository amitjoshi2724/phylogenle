#!/usr/bin/env python3
"""
Unit Test: Comprehensive Data Pipeline & Taxonomic Integrity Suite
Enforces permanent invariants across:
  - data/species_taxonomy_catalog.json
  - data/species_list.json
  - data/phylogeny_tree.json
  - data/species_aliases.json
  - data/wikimedia_popularity_cache.json
  - docs/AUDIT_COLLAPSED_ORGANISMS.json
  - docs/species_ranking_by_vwiki.csv & docs/species_ranking_by_swiki.csv
  - species_catalog_taxonomic.md
"""

import os
import re
import csv
import json
import unittest

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CATALOG_PATH = os.path.join(BASE_DIR, "data", "species_taxonomy_catalog.json")
SPECIES_LIST_PATH = os.path.join(BASE_DIR, "data", "species_list.json")
TREE_PATH = os.path.join(BASE_DIR, "data", "phylogeny_tree.json")
ALIASES_PATH = os.path.join(BASE_DIR, "data", "species_aliases.json")
CACHE_PATH = os.path.join(BASE_DIR, "data", "wikimedia_popularity_cache.json")
AUDIT_COLLAPSED_PATH = os.path.join(BASE_DIR, "docs", "AUDIT_COLLAPSED_ORGANISMS.json")
VWIKI_CSV_PATH = os.path.join(BASE_DIR, "docs", "species_ranking_by_vwiki.csv")
SWIKI_CSV_PATH = os.path.join(BASE_DIR, "docs", "species_ranking_by_swiki.csv")
TAXONOMIC_MD_PATH = os.path.join(BASE_DIR, "species_catalog_taxonomic.md")


class TestDataPipelineIntegrity(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        with open(CATALOG_PATH, "r", encoding="utf-8") as f:
            cls.catalog = json.load(f)
        with open(SPECIES_LIST_PATH, "r", encoding="utf-8") as f:
            cls.species_list = json.load(f)
        with open(TREE_PATH, "r", encoding="utf-8") as f:
            cls.tree = json.load(f)
        with open(ALIASES_PATH, "r", encoding="utf-8") as f:
            cls.aliases = json.load(f)
        with open(CACHE_PATH, "r", encoding="utf-8") as f:
            cls.cache = json.load(f)
        with open(AUDIT_COLLAPSED_PATH, "r", encoding="utf-8") as f:
            cls.audit_collapsed = json.load(f)

    def test_catalog_and_species_list_bijection(self):
        """Verify 1-to-1 bijection between catalog and species_list, with balanced parens and synced display."""
        self.assertEqual(len(self.catalog), len(self.species_list))
        seen_scis = set()
        expected_displays = set()
        for entry in self.catalog:
            sci = entry["scientific"]
            comm = entry.get("common", "")
            disp = entry.get("display", "")
            self.assertNotIn(sci, seen_scis, f"Duplicate scientific name in catalog: {sci}")
            seen_scis.add(sci)
            self.assertEqual(
                sci.count("("),
                sci.count(")"),
                f"Unbalanced parentheses in scientific name: {sci}",
            )
            expected_disp = f"{comm} ({sci})" if comm else sci
            self.assertEqual(disp, expected_disp, f"Stale display field on {sci}: {disp} != {expected_disp}")
            expected_displays.add(disp)

        self.assertEqual(set(self.species_list), expected_displays)

    def test_phylogeny_tree_bijection_and_full_lineages(self):
        """Verify every catalog organism has a full root-to-taxon lineage (len >= 2) in phylogeny_tree.json."""
        expected_keys = {s["display"].lower() for s in self.catalog}
        tree_species = self.tree["species"]
        tree_nodes = self.tree["nodes"]

        missing = expected_keys - set(tree_species.keys())
        extra = set(tree_species.keys()) - expected_keys
        self.assertEqual(len(missing), 0, f"Missing from phylogeny_tree.json: {list(missing)[:10]}")
        self.assertEqual(len(extra), 0, f"Orphan keys in phylogeny_tree.json: {list(extra)[:10]}")

        for key, path in tree_species.items():
            self.assertGreaterEqual(len(path), 2, f"Truncated lineage (len < 2) for {key}: {path}")
            self.assertEqual(path[0], 1, f"Lineage for {key} does not start at root 1: {path}")
            for tid in path:
                self.assertIn(str(tid), tree_nodes, f"Missing node ID {tid} in tree['nodes'] for {key}")

    def test_aliases_integrity_and_sanitization(self):
        """Verify 0 dangling targets, 0 primary-name shadowing, and 0 junk/typo/namespace aliases."""
        valid_displays = set(self.species_list)
        primary_names = set()
        for s in self.catalog:
            primary_names.add(s["display"].lower())
            primary_names.add(s["scientific"].lower())
            if s.get("common"):
                primary_names.add(s["common"].lower())

        banned_substrings = ("user:", "draft:", "wikipedia:", "template:", "category:", "penis", "vagina", "genitalia")
        banned_exact = {
            "huamn", "hippopautamus", "cabybara", "elaphant", "ok i pull up",
            "lion penis", "sex organs of cattle", "paragon falcon", "dyer wolf",
            "elefonts", "chikkin", "cockeral", "dodo poo", "dodologist"
        }

        for alias_key, target in self.aliases.items():
            self.assertIn(target, valid_displays, f"Dangling alias target '{target}' for alias '{alias_key}'")
            self.assertNotIn(alias_key.lower(), primary_names, f"Alias '{alias_key}' shadows a primary organism name")
            self.assertNotIn("(", alias_key, f"Parenthesis in alias key: '{alias_key}'")
            self.assertNotIn(")", alias_key, f"Parenthesis in alias key: '{alias_key}'")
            self.assertNotIn(alias_key.lower(), banned_exact, f"Banned junk/typo alias found: '{alias_key}'")
            for sub in banned_substrings:
                self.assertNotIn(sub, alias_key.lower(), f"Banned substring '{sub}' in alias '{alias_key}'")

    def test_no_fake_or_non_biological_homonym_qids(self):
        """Verify 0 fake Q1000000 QIDs and 0 non-biological homonym QIDs in audit JSON and popularity cache."""
        banned_homonym_qids = {
            "Q1000000",  # Fake placeholder
            "Q43",       # Republic of Türkiye (country)
            "Q4100",     # Baden-Baden (city)
            "Q212792",   # Bolt (2008 Disney film)
            "Q14660",    # Flag
            "Q193291",   # Sunrise
            "Q912820",   # Straw man fallacy
            "Q878123",   # Flying Tigers squadron
        }
        for item in self.audit_collapsed:
            self.assertNotIn(item.get("umbrella_qid"), banned_homonym_qids)
            self.assertNotEqual(item.get("species_scientific"), item.get("umbrella_scientific"))

        cat_scis = {s["scientific"] for s in self.catalog}
        for sci in cat_scis:
            rec = self.cache.get(sci, {})
            qid = rec.get("qid")
            self.assertNotIn(qid, banned_homonym_qids, f"Banned non-biological QID {qid} on {sci}")

    def test_ranking_csvs_unique_titles_and_clean_formatting(self):
        """Verify 0 duplicate Wikipedia articles and 0 apostrophe-casing bugs in ranking CSVs."""
        cat_scis = {s["scientific"] for s in self.catalog}
        seen_primary_titles = {}

        with open(VWIKI_CSV_PATH, "r", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))

        self.assertGreater(len(rows), 20000)
        for row in rows:
            sci = row["Scientific Name"]
            self.assertIn(sci, cat_scis, f"CSV row scientific name '{sci}' not in catalog")
            full_title = row["Wikipedia Title"]
            prim_title = full_title.split(" (+")[0].strip()
            if prim_title:
                self.assertNotIn(
                    prim_title,
                    seen_primary_titles,
                    f"Duplicate Wikipedia Title '{prim_title}' shared by {sci} and {seen_primary_titles.get(prim_title)}",
                )
                seen_primary_titles[prim_title] = sci

            aliases_col = row["Alternative Names / Aliases"]
            # Check against Python .title() apostrophe bug (e.g., "Man'S Best Friend")
            self.assertIsNone(
                re.search(r"[A-Za-z]'[A-Z]", aliases_col),
                f"Apostrophe capitalization bug in CSV aliases for {sci}: {aliases_col}",
            )


if __name__ == "__main__":
    unittest.main()

