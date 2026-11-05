import json
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


class TestCustomChallenge(unittest.TestCase):
    def test_challenge_module_exists_and_exports_expected_api(self):
        challenge_js_path = ROOT / "challenge.js"
        self.assertTrue(challenge_js_path.exists(), "challenge.js must exist in project root")
        content = challenge_js_path.read_text(encoding="utf-8")

        # Verify key module functions and exports
        self.assertIn("export function encodeChallengePayload", content)
        self.assertIn("export function decodeChallengePayload", content)
        self.assertIn("export function resolveWikipediaUrlOrQuery", content)
        self.assertIn("export function getChallengeShareUrl", content)
        self.assertIn("export async function copyChallengeLink", content)

    def test_challenge_encryption_decryption_and_salt_randomization(self):
        node_script = """
        import('./challenge.js').then(m => {
            const payload = {
                target: 'Honey badger (Mellivora capensis)',
                creator: 'Amit',
                message: 'Can you solve this under 6 guesses?'
            };
            const token1 = m.encodeChallengePayload(payload);
            const token2 = m.encodeChallengePayload(payload);

            if (!token1.startsWith('c1_')) throw new Error('Token missing c1_ prefix');
            if (token1 === token2) throw new Error('Identical tokens generated for same organism; salt failed');

            const dec1 = m.decodeChallengePayload(token1);
            const dec2 = m.decodeChallengePayload(token2);

            if (!dec1.isValid || !dec2.isValid) throw new Error('Payload failed validation');
            if (dec1.target !== payload.target || dec2.target !== payload.target) throw new Error('Decoded target mismatch');
            if (dec1.creator !== payload.creator || dec2.creator !== payload.creator) throw new Error('Decoded creator mismatch');
            if (dec1.message !== payload.message || dec2.message !== payload.message) throw new Error('Decoded message mismatch');

            // Test corrupted / invalid token
            const invalid = m.decodeChallengePayload('c1_invalid_payload_token');
            if (invalid.isValid) throw new Error('Corrupted token should not report isValid: true');

            console.log(JSON.stringify({ status: 'ok', tokenSample: token1 }));
        }).catch(err => {
            console.error(err);
            process.exit(1);
        });
        """
        proc = subprocess.run(
            ["node", "--input-type=module", "-e", node_script],
            capture_output=True,
            text=True,
            cwd=str(ROOT)
        )
        self.assertEqual(proc.returncode, 0, f"Node test failed: {proc.stderr}")
        res = json.loads(proc.stdout.strip())
        self.assertEqual(res["status"], "ok")

    def test_wikipedia_url_and_query_resolution(self):
        node_script = """
        import('./challenge.js').then(m => {
            const allSpecies = [
                'Honey badger (Mellivora capensis)',
                'Barn owl (Tyto alba)',
                'Atlantic sand fiddler crab (Leptuca pugilator)'
            ];
            const aliases = {
                'ratel': 'Honey badger (Mellivora capensis)',
                'fiddler crab': 'Atlantic sand fiddler crab (Leptuca pugilator)'
            };

            // 1. Desktop Wikipedia URL
            const r1 = m.resolveWikipediaUrlOrQuery('https://en.wikipedia.org/wiki/Honey_badger', allSpecies, aliases);
            if (r1 !== 'Honey badger (Mellivora capensis)') throw new Error('Desktop wiki URL failed: ' + r1);

            // 2. Mobile Wikipedia URL with scientific title
            const r2 = m.resolveWikipediaUrlOrQuery('https://en.m.wikipedia.org/wiki/Tyto_alba', allSpecies, aliases);
            if (r2 !== 'Barn owl (Tyto alba)') throw new Error('Mobile wiki URL failed: ' + r2);

            // 3. Encoded URL with query strings
            const r3 = m.resolveWikipediaUrlOrQuery('https://en.wikipedia.org/wiki/Atlantic_sand_fiddler_crab?veaction=edit', allSpecies, aliases);
            if (r3 !== 'Atlantic sand fiddler crab (Leptuca pugilator)') throw new Error('URL with query string failed: ' + r3);

            // 4. Alias resolution
            const r4 = m.resolveWikipediaUrlOrQuery('ratel', allSpecies, aliases);
            if (r4 !== 'Honey badger (Mellivora capensis)') throw new Error('Alias resolution failed: ' + r4);

            // 5. Direct common name or scientific name query
            const r5 = m.resolveWikipediaUrlOrQuery('Tyto alba', allSpecies, aliases);
            if (r5 !== 'Barn owl (Tyto alba)') throw new Error('Direct scientific name query failed: ' + r5);

            console.log(JSON.stringify({ status: 'ok' }));
        }).catch(err => {
            console.error(err);
            process.exit(1);
        });
        """
        proc = subprocess.run(
            ["node", "--input-type=module", "-e", node_script],
            capture_output=True,
            text=True,
            cwd=str(ROOT)
        )
        self.assertEqual(proc.returncode, 0, f"Node test failed: {proc.stderr}")
        res = json.loads(proc.stdout.strip())
        self.assertEqual(res["status"], "ok")

    def test_html_includes_custom_challenge_elements(self):
        html = (ROOT / "index.html").read_text(encoding="utf-8")

        # Top navigation button
        self.assertIn('id="challenge-modal-btn"', html)
        self.assertIn("Challenge", html)

        # In-game banner on left panel
        self.assertIn('id="challenge-banner"', html)
        self.assertIn('id="challenge-banner-creator"', html)
        self.assertIn('id="challenge-banner-msg"', html)
        self.assertIn('id="challenge-exit-btn"', html)

        # End round challenge friend button
        self.assertIn('id="end-challenge-friend-btn"', html)

        # Modal elements
        self.assertIn('id="challenge-modal"', html)
        self.assertIn('id="challenge-organism-input"', html)
        self.assertIn('id="challenge-autocomplete-list"', html)
        self.assertIn('id="challenge-selected-organism"', html)
        self.assertIn('id="challenge-creator-name"', html)
        self.assertIn('id="challenge-hint-msg"', html)
        self.assertIn('id="generate-challenge-btn"', html)
        self.assertIn('id="challenge-play-direct-btn"', html)
        self.assertIn('id="challenge-result-card"', html)
        self.assertIn('id="challenge-share-url-input"', html)
        self.assertIn('id="challenge-copy-link-btn"', html)
        self.assertIn('id="challenge-copy-toast"', html)
        self.assertIn('id="challenge-play-now-btn"', html)

    def test_css_contains_custom_challenge_styles(self):
        style_css = (ROOT / "style.css").read_text(encoding="utf-8")
        modals_css = (ROOT / "modals.css").read_text(encoding="utf-8")

        # Banner and action styles in style.css
        self.assertIn(".challenge-banner", style_css)
        self.assertIn(".challenge-banner-title", style_css)
        self.assertIn(".challenge-banner-msg", style_css)
        self.assertIn(".challenge-exit-btn", style_css)
        self.assertIn(".challenge-action-btn", style_css)

        # Modal styles in modals.css
        self.assertIn(".challenge-nav-btn", modals_css)
        self.assertIn(".challenge-modal-dialog", modals_css)
        self.assertIn(".challenge-selected-badge", modals_css)
        self.assertIn(".challenge-result-card", modals_css)
        self.assertIn(".challenge-share-group", modals_css)

    def test_script_wires_challenge_mode_and_modal_events(self):
        script_js = (ROOT / "script.js").read_text(encoding="utf-8")

        # Import statements from challenge.js
        self.assertIn("from './challenge.js'", script_js)
        self.assertIn("encodeChallengePayload", script_js)
        self.assertIn("decodeChallengePayload", script_js)
        self.assertIn("resolveWikipediaUrlOrQuery", script_js)
        self.assertIn("getChallengeShareUrl", script_js)
        self.assertIn("copyChallengeLink", script_js)

        # URL param detection for challenge / custom / direct wiki & organism
        self.assertIn("urlParams.get('challenge')", script_js)
        self.assertIn("urlParams.get('custom')", script_js)
        self.assertIn("urlParams.get('wiki')", script_js)

        # Challenge modal and UI handlers
        self.assertIn("function setChallengeSelectedTarget", script_js)
        self.assertIn("function openChallengeModal", script_js)
        self.assertIn("function renderChallengeAutocomplete", script_js)
        self.assertIn("handleChallengeOrganismInput", script_js)
        self.assertIn("generateChallengeBtn", script_js)
        self.assertIn("challengePlayDirectBtn", script_js)
        self.assertIn("challengeCopyLinkBtn", script_js)
        self.assertIn("challengePlayNowBtn", script_js)
        self.assertIn("challengeModalBtn", script_js)
        self.assertIn("endChallengeFriendBtn", script_js)
        self.assertIn("challengeExitBtn", script_js)

        # Share score includes custom challenge URL and creator
        self.assertIn("isCustomChallenge", script_js)
        self.assertIn("Phylogenle Challenge 🎁", script_js)


if __name__ == "__main__":
    unittest.main()

