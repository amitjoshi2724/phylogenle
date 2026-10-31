import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


class TestUIAndCatalogImprovements(unittest.TestCase):
    def test_kofi_widget_in_top_navbar(self):
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        nav_start = html.find('<nav class="top-navbar"')
        nav_end = html.find('</nav>')
        self.assertNotEqual(nav_start, -1)
        self.assertNotEqual(nav_end, -1)
        nav_html = html[nav_start:nav_end]
        self.assertIn('id="kofi-widget-container"', nav_html)

    def test_author_credits_in_header(self):
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        header_start = html.find('<header>')
        header_end = html.find('</header>')
        self.assertNotEqual(header_start, -1)
        self.assertNotEqual(header_end, -1)
        header_html = html[header_start:header_end]
        self.assertIn("Developed by", header_html)
        self.assertIn("Amit Joshi", header_html)
        self.assertIn("github.com/amitjoshi2724", header_html)

        # Ensure old credits section in left-panel is removed
        self.assertNotIn('class="credits-section"', html)

    def test_inline_catalog_button_in_guess_rows(self):
        script_js = (ROOT / "script.js").read_text(encoding="utf-8")
        self.assertIn('class="guess-catalog-btn"', script_js)
        # Check that addGuessToBoard and addHintToBoard both wire up openCatalogAtTaxon
        self.assertIn("openCatalogAtTaxon(hint.name, rank)", script_js)
        self.assertIn("openCatalogAtTaxon(targetLinnaeanName, data.rank)", script_js)

    def test_open_catalog_at_taxon_does_not_force_search_view(self):
        script_js = (ROOT / "script.js").read_text(encoding="utf-8")
        # Ensure openCatalogAtTaxon cleans up search mode and restores full Linnaean tree
        self.assertIn("renderCatalogView();", script_js)
        self.assertIn("resolvedRank", script_js)
        self.assertIn("resolvedName", script_js)


if __name__ == "__main__":
    unittest.main()

