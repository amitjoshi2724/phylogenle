"""
Tests for Wikipedia Reader Integration, Dark Mode Layout, Screen Unblur, and Separated Clade Badges
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
        self.assertGreaterEqual(len(clades), 200, "Should have curated at least 200 major clades/ranks and subclades")

        # Check key major clades and subclades have common names
        expected_clades = [
            "animalia", "chordata", "actinopteri", "cypriniformes",
            "mammalia", "aves", "carnivora", "felidae", "arthropoda",
            "plantae", "fungi", "eukaryota", "clupeocephala", "euteleostomi"
        ]
        for clade in expected_clades:
            self.assertIn(clade, clades, f"Clade '{clade}' should be in clade_common_names.json")
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

    def test_css_styles_for_wiki_reader_and_no_blur(self):
        style_path = os.path.join(REPO_ROOT, 'style.css')
        with open(style_path, 'r', encoding='utf-8') as f:
            style_css = f.read()

        self.assertIn('.guess-wiki-btn', style_css, "style.css should style .guess-wiki-btn")
        self.assertIn('.wiki-reader-action-btn', style_css, "style.css should style .wiki-reader-action-btn")
        self.assertIn('.feedback-subclade', style_css, "style.css should style .feedback-subclade")

        modals_path = os.path.join(REPO_ROOT, 'modals.css')
        with open(modals_path, 'r', encoding='utf-8') as f:
            modals_css = f.read()

        self.assertIn('.wiki-drawer', modals_css, "modals.css should define .wiki-drawer")
        self.assertIn('.wiki-drawer-backdrop', modals_css, "modals.css should define .wiki-drawer-backdrop")
        # Ensure screen is not blurred when drawer opens
        self.assertIn('backdrop-filter: none', modals_css, "Backdrop must not blur the rest of the screen")
        self.assertIn('.wiki-guess-btn', modals_css, "modals.css should define .wiki-guess-btn")

    def test_script_js_implements_separated_badges_caching_and_dark_mode(self):
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

        # Client-side caching of Wikipedia pages
        self.assertIn('wikiArticleCache', code, "script.js should cache fetched articles in memory")
        self.assertIn('getCachedWikiArticle', code, "script.js should check cache before fetching")
        self.assertIn('setCachedWikiArticle', code, "script.js should store fetched articles in cache")

        # Separated main taxonomic rank and subclade badges
        self.assertIn('feedback-rank', code, "script.js should render main taxonomic rank badge")
        self.assertIn('feedback-subclade', code, "script.js should render separate evolutionary subclade badge")

        # Dark mode stylesheet proxying (routing from meta to en.wikipedia.org)
        self.assertIn('en.wikipedia.org/api/rest_v1/', code, "CSS links should be routed to en.wikipedia.org")

        # Inline Wiki buttons in guesses, clues, and surrender rows
        self.assertIn('guess-wiki-btn', code, "script.js should render .guess-wiki-btn in guess rows")

        # Escape key handling
        self.assertIn("e.key === 'Escape'", code)
        self.assertIn("wikiDrawerState.isOpen", code, "Escape should close wiki drawer when open")

    def test_wiki_tooltip_interactive_hover_persistence_and_buffer(self):
        style_path = os.path.join(REPO_ROOT, 'style.css')
        with open(style_path, 'r', encoding='utf-8') as f:
            style_css = f.read()

        script_path = os.path.join(REPO_ROOT, 'script.js')
        with open(script_path, 'r', encoding='utf-8') as f:
            script_js = f.read()

        # Tooltip must be interactive and have an invisible hover bridge
        self.assertIn('.wiki-tooltip::before', style_css, "style.css should define invisible bridge for tooltip hover")
        self.assertIn('pointer-events: auto', style_css, "style.css should grant pointer-events: auto to interactive tooltip")

        # script.js must track hovering state and prevent prematurely hiding while moving to buttons
        self.assertIn('isHoveringTooltip', script_js, "script.js should track tooltip hover state")
        self.assertIn('scheduleHideWikiTooltip', script_js, "script.js should use generous hide delay")
        self.assertIn('cancelTooltipHide', script_js, "script.js should cancel hide timer on hover")
        self.assertIn('hideWikiTooltipImmediate', script_js, "script.js should support immediate dismissal on action click")
        self.assertIn('if (isHoveringTooltip) return;', script_js, "script.js should not hijack tooltip while user is interacting with it")


if __name__ == '__main__':
    unittest.main()
