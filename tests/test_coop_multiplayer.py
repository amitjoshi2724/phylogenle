import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


class TestCooperativeMultiplayer(unittest.TestCase):
    def test_coop_module_exists_and_exports_expected_api(self):
        coop_js_path = ROOT / "coop.js"
        self.assertTrue(coop_js_path.exists(), "coop.js must exist in project root")
        content = coop_js_path.read_text(encoding="utf-8")

        # Verify key module functions and exports
        self.assertIn("export async function createCoopRoom", content)
        self.assertIn("export async function joinCoopRoom", content)
        self.assertIn("export function leaveCoopRoom", content)
        self.assertIn("export async function submitCoopGuess", content)
        self.assertIn("export async function submitCoopHint", content)
        self.assertIn("export function getMyPlayerProfile", content)
        self.assertIn("export function saveProfile", content)
        self.assertIn("export function onCoopEvent", content)
        self.assertIn("export function getRoomShareUrl", content)
        self.assertIn("export async function copyRoomLink", content)
        self.assertIn("export const AVATAR_PALETTE", content)

    def test_html_includes_in_game_and_nav_coop_controls(self):
        html = (ROOT / "index.html").read_text(encoding="utf-8")

        # Header nav button
        self.assertIn('id="coop-nav-btn"', html)
        self.assertIn("Co-op", html)

        # In-game button directly on the play action bar (next to Guess / Hint / Give Up)
        self.assertIn('id="in-game-coop-btn"', html)
        self.assertIn("Play with Friends", html)

        # Persistent Co-Op Status Bar
        self.assertIn('id="coop-status-bar"', html)
        self.assertIn('id="coop-room-code-display"', html)
        self.assertIn('id="coop-participants-list"', html)
        self.assertIn('id="coop-copy-link-btn"', html)
        self.assertIn('id="coop-leave-room-btn"', html)

        # Co-Op Modal & Lobby/Active Views
        self.assertIn('id="coop-modal"', html)
        self.assertIn('id="coop-active-view"', html)
        self.assertIn('id="coop-lobby-view"', html)
        self.assertIn('id="coop-create-room-btn"', html)
        self.assertIn('id="coop-join-room-btn"', html)
        self.assertIn('id="coop-join-code-input"', html)
        self.assertIn('id="coop-avatar-palette"', html)
        self.assertIn('id="coop-player-name-input"', html)

    def test_css_contains_coop_button_status_bar_and_modal_styles(self):
        style_css = (ROOT / "style.css").read_text(encoding="utf-8")
        modals_css = (ROOT / "modals.css").read_text(encoding="utf-8")

        # Action button and status bar in style.css
        self.assertIn(".coop-action-btn", style_css)
        self.assertIn(".coop-player-tag", style_css)
        self.assertIn(".coop-status-bar", style_css)
        self.assertIn(".coop-pulse-dot", style_css)

        # Modal styles in modals.css
        self.assertIn(".coop-modal-dialog", modals_css)
        self.assertIn(".coop-avatar-palette", modals_css)
        self.assertIn(".coop-avatar-option", modals_css)
        self.assertIn(".coop-room-card", modals_css)

    def test_firestore_rules_cover_coop_rooms_and_preserve_user_security(self):
        rules = (ROOT / "firestore.rules").read_text(encoding="utf-8")

        # Must preserve users/{userId} collection security
        self.assertIn("match /users/{userId}", rules)

        # Must govern coop_rooms/{roomId}
        self.assertIn("match /coop_rooms/{roomId}", rules)
        self.assertIn("allow read: if true;", rules)
        self.assertIn("isValidRoomCreate", rules)
        self.assertIn("isValidRoomUpdate", rules)
        self.assertIn("isRoomCreator", rules)

        # Critical immutability checks for targetSpecies and core room data
        self.assertIn("targetSpecies", rules)
        self.assertIn("roomId", rules)
        self.assertIn("winner", rules)

    def test_script_wires_midgame_promotion_live_sync_and_both_players_stats(self):
        script_js = (ROOT / "script.js").read_text(encoding="utf-8")

        # Co-Op imports from coop.js
        self.assertIn("from './coop.js'", script_js)
        self.assertIn("createCoopRoom", script_js)
        self.assertIn("joinCoopRoom", script_js)
        self.assertIn("submitCoopGuess", script_js)
        self.assertIn("submitCoopHint", script_js)
        self.assertIn("onCoopEvent", script_js)

        # URL parameter auto-join
        self.assertIn("urlParams.get('room')", script_js)

        # Mid-game promotion logic
        self.assertIn("handleInGameCoopClick", script_js)
        self.assertIn("existingGuesses: guesses", script_js)
        self.assertIn("existingHints: revealedHints", script_js)

        # Player attribution on guesses and hints
        self.assertIn("playerBadgeHtml", script_js)
        self.assertIn("coop-player-tag", script_js)

        # Updating stats for both/all players upon co-op completion
        self.assertIn("recordDailyCompletion(currentDateStr, puzzleNum, true, guesses.length", script_js)
        self.assertIn("recordPracticeCompletion(true, guesses.length", script_js)


if __name__ == "__main__":
    unittest.main()
