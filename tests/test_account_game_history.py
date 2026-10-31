import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


class TestAccountGameHistoryAndStatsUI(unittest.TestCase):
    def test_storage_persists_all_game_types_to_account(self):
        storage_js = (ROOT / "storage.js").read_text(encoding="utf-8")
        # Must persist daily history, practice history, and active/unfinished games
        self.assertIn("phylogenle_history", storage_js)
        self.assertIn("phylogenle_practice_history", storage_js)
        self.assertIn("phylogenle_active_games", storage_js)
        self.assertIn("export function recordPracticeCompletion", storage_js)
        self.assertIn("export function getAllGamesLedger", storage_js)
        self.assertIn("meanGuesses", storage_js)

    def test_stats_modal_html_matches_requested_layout(self):
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        # Top metric cards
        self.assertIn('id="stat-played"', html)
        self.assertIn('id="stat-streak"', html)
        self.assertIn('id="stat-max-streak"', html)
        self.assertIn('id="stat-mean-guesses"', html)
        self.assertIn('id="stat-win-pct"', html)
        # Toolbar controls (Unfinished toggle + Total count, NO Unstarted or Mean Duration)
        self.assertIn('id="stats-unfinished-toggle"', html)
        self.assertIn('id="stats-total-count"', html)
        self.assertNotIn("Mean Duration", html)
        self.assertNotIn("Unstarted", html)
        # Heatmap & History Table
        self.assertIn('id="stats-heatmap-months"', html)
        self.assertIn('id="stats-heatmap-grid"', html)
        self.assertIn('id="stats-history-tbody"', html)
        self.assertIn('id="stats-game-detail-drawer"', html)

    def test_script_renders_heatmap_history_and_spoiler_protection(self):
        script_js = (ROOT / "script.js").read_text(encoding="utf-8")
        self.assertIn("recordPracticeCompletion", script_js)
        self.assertIn("getAllGamesLedger", script_js)
        self.assertIn("renderStatsHeatmap", script_js)
        self.assertIn("renderStatsHistoryTable", script_js)
        self.assertIn("openStatsGameDetail", script_js)
        # Spoiler protection for unfinished games
        self.assertIn("Mystery Organism (In Progress)", script_js)


if __name__ == "__main__":
    unittest.main()
