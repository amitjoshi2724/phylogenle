"""
Unit tests for species common name override management (set_common_name_override.py)
and data/species_common_name_overrides.json integrity.
"""

import os
import sys
import json
import unittest
import subprocess
import tempfile
import shutil

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT_PATH = os.path.join(REPO_ROOT, "set_common_name_override.py")
OVERRIDES_PATH = os.path.join(REPO_ROOT, "data", "species_common_name_overrides.json")
CATALOG_PATH = os.path.join(REPO_ROOT, "data", "species_taxonomy_catalog.json")

# Import the module under test
sys.path.insert(0, REPO_ROOT)
import set_common_name_override as scno


class TestCommonNameOverrideCLI(unittest.TestCase):
    def test_script_exists_and_is_executable(self):
        self.assertTrue(os.path.exists(SCRIPT_PATH), "set_common_name_override.py should exist")
        self.assertTrue(os.access(SCRIPT_PATH, os.X_OK), "Script should be executable")

    def test_overrides_file_exists_and_is_valid_json(self):
        self.assertTrue(os.path.exists(OVERRIDES_PATH), "data/species_common_name_overrides.json should exist")
        with open(OVERRIDES_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.assertIsInstance(data, dict, "Overrides file must be a JSON object")

    def test_cli_help(self):
        res = subprocess.run([sys.executable, SCRIPT_PATH, "--help"], capture_output=True, text=True)
        self.assertEqual(res.returncode, 0, f"--help failed: {res.stderr}")
        self.assertIn("--set", res.stdout)
        self.assertIn("--remove", res.stdout)
        self.assertIn("--list", res.stdout)
        self.assertIn("--apply", res.stdout)

    def test_cli_list(self):
        res = subprocess.run([sys.executable, SCRIPT_PATH, "--list"], capture_output=True, text=True)
        self.assertEqual(res.returncode, 0, f"--list failed: {res.stderr}")

    def test_dry_run_does_not_modify_disk(self):
        # Read file before dry-run
        with open(OVERRIDES_PATH, "r", encoding="utf-8") as f:
            before = f.read()

        res = subprocess.run(
            [sys.executable, SCRIPT_PATH, "Mellivora capensis", "Honey Badger", "--dry-run"],
            capture_output=True, text=True
        )
        self.assertEqual(res.returncode, 0, f"--dry-run failed: {res.stderr}")
        self.assertIn("Would update", res.stdout)

        # File on disk must remain unchanged
        with open(OVERRIDES_PATH, "r", encoding="utf-8") as f:
            after = f.read()
        self.assertEqual(before, after, "--dry-run must not write changes to disk")


class TestCommonNameOverrideLogic(unittest.TestCase):
    def setUp(self):
        self.catalog = scno.load_json(CATALOG_PATH, default=[])

    def test_find_species_by_scientific_name(self):
        species, ambig = scno.find_species_in_catalog(self.catalog, "Mellivora capensis")
        self.assertIsNotNone(species)
        self.assertEqual(species.get("scientific"), "Mellivora capensis")
        self.assertEqual(species.get("common"), "Ratel")

    def test_find_species_by_current_common_name(self):
        species, ambig = scno.find_species_in_catalog(self.catalog, "Ratel")
        self.assertIsNotNone(species)
        self.assertEqual(species.get("scientific"), "Mellivora capensis")

    def test_find_species_by_display_string(self):
        species, ambig = scno.find_species_in_catalog(self.catalog, "Ratel (Mellivora capensis)")
        self.assertIsNotNone(species)
        self.assertEqual(species.get("scientific"), "Mellivora capensis")

    def test_isolated_apply_and_revert_cycle(self):
        """Test full override and revert in an isolated temporary directory to ensure 100% data fidelity."""
        temp_dir = tempfile.mkdtemp()
        try:
            # Create minimal mock datasets
            mock_catalog = [
                {
                    "common": "Ratel",
                    "scientific": "Mellivora capensis",
                    "display": "Ratel (Mellivora capensis)",
                    "kingdom": "Animalia",
                    "class": "Mammalia",
                    "order": "Carnivora",
                    "family": "Mustelidae"
                }
            ]
            mock_species_list = ["Ratel (Mellivora capensis)"]
            mock_tree = {
                "species": {
                    "ratel (mellivora capensis)": [1, 33208, 7711, 40674, 33554, 9655, 9664]
                },
                "nodes": {
                    "9664": {"rank": "Species", "name": "Mellivora capensis", "common_name": "Ratel"}
                }
            }
            mock_aliases = {
                "honey badger": "Ratel (Mellivora capensis)",
                "honeybadger": "Ratel (Mellivora capensis)"
            }
            mock_cache = {
                "Mellivora capensis": {"common": "Ratel", "scientific": "Mellivora capensis"}
            }

            temp_data_dir = os.path.join(temp_dir, "data")
            os.makedirs(temp_data_dir, exist_ok=True)

            cat_path = os.path.join(temp_data_dir, "species_taxonomy_catalog.json")
            list_path = os.path.join(temp_data_dir, "species_list.json")
            tree_path = os.path.join(temp_data_dir, "phylogeny_tree.json")
            alias_path = os.path.join(temp_data_dir, "species_aliases.json")
            cache_path = os.path.join(temp_data_dir, "wikimedia_popularity_cache.json")
            overrides_path = os.path.join(temp_data_dir, "species_common_name_overrides.json")

            scno.save_json(cat_path, mock_catalog)
            scno.save_json(list_path, mock_species_list)
            scno.save_json(tree_path, mock_tree)
            scno.save_json(alias_path, mock_aliases)
            scno.save_json(cache_path, mock_cache)
            scno.save_json(overrides_path, {"Mellivora capensis": {"common": "Honey Badger", "original_common": "Ratel"}})

            # Patch paths in scno
            old_cat = scno.CATALOG_PATH
            old_list = scno.SPECIES_LIST_PATH
            old_tree = scno.TREE_PATH
            old_alias = scno.ALIASES_PATH
            old_cache = scno.CACHE_PATH
            old_ov = scno.OVERRIDES_PATH
            old_build = scno.BUILD_CATALOG_SCRIPT

            scno.CATALOG_PATH = cat_path
            scno.SPECIES_LIST_PATH = list_path
            scno.TREE_PATH = tree_path
            scno.ALIASES_PATH = alias_path
            scno.CACHE_PATH = cache_path
            scno.OVERRIDES_PATH = overrides_path
            scno.BUILD_CATALOG_SCRIPT = "/dev/null"

            try:
                # Apply override
                applied = scno.apply_overrides(verbose=False)
                self.assertTrue(applied)

                updated_cat = scno.load_json(cat_path)
                self.assertEqual(updated_cat[0]["common"], "Honey Badger")
                self.assertEqual(updated_cat[0]["display"], "Honey Badger (Mellivora capensis)")

                updated_list = scno.load_json(list_path)
                self.assertIn("Honey Badger (Mellivora capensis)", updated_list)
                self.assertNotIn("Ratel (Mellivora capensis)", updated_list)

                updated_tree = scno.load_json(tree_path)
                self.assertIn("honey badger (mellivora capensis)", updated_tree["species"])
                self.assertNotIn("ratel (mellivora capensis)", updated_tree["species"])

                updated_aliases = scno.load_json(alias_path)
                # 'ratel' should now be an alias to the new display
                self.assertEqual(updated_aliases.get("ratel"), "Honey Badger (Mellivora capensis)")
                # 'honey badger' should no longer be an alias key (it is now primary)
                self.assertNotIn("honey badger", updated_aliases)
                # 'honeybadger' should now point to new display
                self.assertEqual(updated_aliases.get("honeybadger"), "Honey Badger (Mellivora capensis)")

                # Now remove override
                removed = scno.cmd_remove("Mellivora capensis")
                self.assertTrue(removed)

                restored_cat = scno.load_json(cat_path)
                self.assertEqual(restored_cat[0]["common"], "Ratel")
                self.assertEqual(restored_cat[0]["display"], "Ratel (Mellivora capensis)")

                restored_list = scno.load_json(list_path)
                self.assertIn("Ratel (Mellivora capensis)", restored_list)
                self.assertNotIn("Honey Badger (Mellivora capensis)", restored_list)

                restored_tree = scno.load_json(tree_path)
                self.assertIn("ratel (mellivora capensis)", restored_tree["species"])
                self.assertNotIn("honey badger (mellivora capensis)", restored_tree["species"])

            finally:
                scno.CATALOG_PATH = old_cat
                scno.SPECIES_LIST_PATH = old_list
                scno.TREE_PATH = old_tree
                scno.ALIASES_PATH = old_alias
                scno.CACHE_PATH = old_cache
                scno.OVERRIDES_PATH = old_ov
                scno.BUILD_CATALOG_SCRIPT = old_build

        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()

