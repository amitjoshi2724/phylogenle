"""
Unit test for sync_tree_wikipedia_and_common_names.py and generated data artifacts
"""

import unittest
import os
import json
import subprocess

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class TestSyncTreeScript(unittest.TestCase):
    def test_script_exists_and_is_executable(self):
        script_path = os.path.join(REPO_ROOT, "sync_tree_wikipedia_and_common_names.py")
        self.assertTrue(os.path.exists(script_path), "sync_tree_wikipedia_and_common_names.py should exist")
        self.assertTrue(os.access(script_path, os.X_OK), "Script should be executable")

    def test_cli_dry_run_offline(self):
        script_path = os.path.join(REPO_ROOT, "sync_tree_wikipedia_and_common_names.py")
        res = subprocess.run([sys.executable if "sys" in globals() else "python3", script_path, "--offline", "--dry-run"],
                             capture_output=True, text=True)
        self.assertEqual(res.returncode, 0, f"Script failed with: {res.stderr}")
        self.assertIn("Pipeline complete", res.stdout)

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
