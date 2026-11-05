"""
Unit test for wikimedia_taxonomy_pipeline.py, sync_tree_wikipedia_and_common_names.py, and generated data artifacts
"""

import unittest
import sys
import os
import json
import subprocess

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class TestTaxonomyPipelineScripts(unittest.TestCase):
    def test_original_rank_species_popularity_preserved(self):
        script_path = os.path.join(REPO_ROOT, "rank_species_popularity.py")
        self.assertTrue(os.path.exists(script_path), "rank_species_popularity.py must be preserved intact")

    def test_sync_script_exists_and_is_executable(self):
        script_path = os.path.join(REPO_ROOT, "sync_tree_wikipedia_and_common_names.py")
        self.assertTrue(os.path.exists(script_path), "sync_tree_wikipedia_and_common_names.py should exist")
        self.assertTrue(os.access(script_path, os.X_OK), "Script should be executable")

    def test_unified_wikimedia_taxonomy_pipeline_exists_and_is_executable(self):
        script_path = os.path.join(REPO_ROOT, "wikimedia_taxonomy_pipeline.py")
        self.assertTrue(os.path.exists(script_path), "wikimedia_taxonomy_pipeline.py should exist")
        self.assertTrue(os.access(script_path, os.X_OK), "Script should be executable")

    def test_unified_pipeline_cli_help(self):
        script_path = os.path.join(REPO_ROOT, "wikimedia_taxonomy_pipeline.py")
        res = subprocess.run([sys.executable, script_path, "--help"],
                             capture_output=True, text=True)
        self.assertEqual(res.returncode, 0, f"--help failed with: {res.stderr}")
        self.assertIn("--tree-only", res.stdout)
        self.assertIn("--offline", res.stdout)

    def test_unified_pipeline_cli_dry_run_offline(self):
        script_path = os.path.join(REPO_ROOT, "wikimedia_taxonomy_pipeline.py")
        res = subprocess.run([sys.executable, script_path, "--tree-only", "--offline", "--dry-run"],
                             capture_output=True, text=True)
        self.assertEqual(res.returncode, 0, f"Script failed with: {res.stderr}")
        self.assertIn("Step 7: Exporting", res.stdout)

    def test_tree_nodes_have_wiki_title_and_common_name(self):
        tree_path = os.path.join(REPO_ROOT, "data", "phylogeny_tree.json")
        with open(tree_path, "r", encoding="utf-8") as f:
            tree = json.load(f)
        nodes = tree.get("nodes", {})
        self.assertGreater(len(nodes), 40000)

        # Check key nodes have wiki_title and common_name
        # Node 7952 (Cypriniformes)
        node_7952 = nodes.get("7952")
        self.assertIsNotNone(node_7952)
        self.assertEqual(node_7952.get("name"), "Cypriniformes")
        self.assertTrue(node_7952.get("wiki_title"), "Node 7952 should have wiki_title")
        self.assertTrue(node_7952.get("common_name"), "Node 7952 should have common_name")

        # Node 9681 (Felidae)
        node_9681 = nodes.get("9681")
        self.assertIsNotNone(node_9681)
        self.assertEqual(node_9681.get("name"), "Felidae")
        self.assertTrue(node_9681.get("common_name"), "Node 9681 should have common_name")

    def test_clade_common_names_json_has_over_2000_entries(self):
        clade_path = os.path.join(REPO_ROOT, "data", "clade_common_names.json")
        with open(clade_path, "r", encoding="utf-8") as f:
            clades = json.load(f)
        self.assertGreaterEqual(len(clades), 2000, "Should have algorithmically indexed at least 2,000 clades")


if __name__ == "__main__":
    unittest.main()
