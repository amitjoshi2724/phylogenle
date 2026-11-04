"""
Tests for Wikipedia Reader Integration and Clade Common Names
"""

import unittest
import os
import json
import re

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class TestWikiIntegration(unittest.TestCase):
    def test_clade_common_names_json_validity(self):
        json_path = os.path.join(REPO_ROOT, 'data', 'clade_common_names.json')
        self.assertTrue(os.path.exists(json_path), "data/clade_common_names.json should exist")
        with open(json_path, 'r', encoding='utf-8') as f:
            clades = json.load(f)

        self.assertIsInstance(clades, dict)
        self.assertGreaterEqual(len(clades), 150, "Should have curated at least 150 major clades/ranks")

        # Check key major clades have common names
        expected_clades = [
            "animalia", "chordata", "actinopteri", "cypriniformes",
            "mammalia", "aves", "carnivora", "felidae", "arthropoda",
            "plantae", "fungi", "eukaryota"
        ]
        for clade in expected_clades:
            self.assertIn(clade, clades, f"Major clade '{clade}' should be in clade_common_names.json")
            self.assertTrue(len(clades[clade]) > 0, f"Common name for '{clade}' should not be empty")

    def test_index_html_has_wiki_drawer_and_tooltip_button(self):
        html_path = os.path.join(REPO_ROOT, 'index.html')
        with open(html_path, 'r', encoding='utf-8') as f:
            html = f.read()

        # Wiki reader drawer elements
        self.assertIn('id="wiki-drawer"', html, "Drawer container should exist in index.html")
        self.assertIn('id="wiki-drawer-backdrop"', html, "Backdrop should exist in index.html")
        self.assertIn('id="wiki-drawer-title"', html, "Drawer title should exist")
        self.assertIn('id="wiki-drawer-iframe"', html, "Drawer iframe should exist")
        self.assertIn('id="wiki-nav-back"', html, "Nav back button should exist")
        self.assertIn('id="wiki-nav-forward"', html, "Nav forward button should exist")
        self.assertIn('id="wiki-nav-reload"', html, "Nav reload button should exist")
        self.assertIn('id="wiki-guess-btn"', html, "Guess in Game button should exist")
        self.assertIn('id="wiki-catalog-shortcut-btn"', html, "Catalog shortcut should exist")
        self.assertIn('id="wiki-theme-toggle-btn"', html, "Theme toggle button should exist")
        self.assertIn('id="wiki-drawer-close-btn"', html, "Close button should exist")
        self.assertIn('id="wiki-tooltip-reader-btn"', html, "Tooltip reader button should exist")

    def test_css_styles_for_wiki_reader_and_guess_button(self):
        style_path = os.path.join(REPO_ROOT, 'style.css')
        with open(style_path, 'r', encoding='utf-8') as f:
            style_css = f.read()

        self.assertIn('.guess-wiki-btn', style_css, "style.css should style .guess-wiki-btn")
        self.assertIn('.wiki-reader-action-btn', style_css, "style.css should style .wiki-reader-action-btn")

        modals_path = os.path.join(REPO_ROOT, 'modals.css')
        with open(modals_path, 'r', encoding='utf-8') as f:
            modals_css = f.read()

        self.assertIn('.wiki-drawer', modals_css, "modals.css should define .wiki-drawer")
        self.assertIn('.wiki-drawer-backdrop', modals_css, "modals.css should define .wiki-drawer-backdrop")
        self.assertIn('.wiki-guess-btn', modals_css, "modals.css should define .wiki-guess-btn")

    def test_script_js_implements_wiki_game_reader_and_common_names(self):
        script_path = os.path.join(REPO_ROOT, 'script.js')
        with open(script_path, 'r', encoding='utf-8') as f:
            code = f.read()

        # Wikipedia Reader Engine
        self.assertIn('openWikiDrawer', code, "script.js should define openWikiDrawer")
        self.assertIn('closeWikiDrawer', code, "script.js should define closeWikiDrawer")
        self.assertIn('openWikiArticle', code, "script.js should define openWikiArticle")
        self.assertIn('loadWikiArticle', code, "script.js should define loadWikiArticle")
        self.assertIn('fetchWikiMobileHtml', code, "script.js should define fetchWikiMobileHtml")
        self.assertIn('buildWikiArticleHtml', code, "script.js should define buildWikiArticleHtml")
        self.assertIn('findMatchingCatalogSpecies', code, "script.js should match articles to species")

        # In-App link interception like the Wikipedia Game
        self.assertIn('contentDocument', code, "script.js should access iframe contentDocument for link interception")
        self.assertIn('articleTitle', code, "script.js should extract destination articleTitle")

        # Inline Wiki buttons in guesses, clues, and surrender rows
        self.assertIn('guess-wiki-btn', code, "script.js should render .guess-wiki-btn in guess rows")

        # Common name support
        self.assertIn('getCladeCommonName', code, "script.js should provide getCladeCommonName")
        self.assertIn('getTreeCladeLabel', code, "script.js should provide getTreeCladeLabel for tree nodes")
        self.assertIn('clade_common_names.json', code, "script.js should load clade_common_names.json")

        # Escape key handling
        self.assertIn("e.key === 'Escape'", code)
        self.assertIn("wikiDrawerState.isOpen", code, "Escape should close wiki drawer when open")


if __name__ == '__main__':
    unittest.main()
