# 📋 Phylogenle: Feature Backlog & Roadmap

> **Document Purpose:** Feature backlog and development tracker for Phylogenle.  
> **Last Updated:** 2026-10-30  

---

## 🎯 Active Feature Backlog

### 1. 🧬 Smart Date-Bounded PRNG for New Species & Umbrella Taxa
- **Goal:** Add new species and umbrella taxa to a game mode (and by extension to all harder difficulty modes) without disrupting historical daily puzzle integrity.
- **Problem Solved:** If new species are naively inserted into the PRNG array, the random seed calculations shift, changing the mystery target for past and current calendar days.
- **Proposed Solution:**
  - **Batch Versioning (`batch_id`):** Group organisms into date-bounded pools (e.g., `Batch 1` active from launch through `2026-10-31`; `Batch 2` unlocked starting `2026-11-01`).
  - **Date-Gated Selection:** When computing the daily puzzle for date $D$, the PRNG only selects candidates from batches where $\text{release\_date} \le D$.
  - **Universal Catalog Sync:** While the PRNG target selection is date-bounded, the master catalog, autocomplete search, and guess evaluation remain universal and always up-to-date.

---

### 2. 🤝 Cooperative Real-Time Multiplayer Mode (Redactle-Style)
- **Goal:** Allow friends to join a shared game session via a share link and guess together collaboratively.
- **Core Features:**
  - **Instant Room Creation:** Click "Play with Friends" to generate a short room link (e.g., `phylogenle.com/room/abc-123`).
  - **Authentication:** Sign in with Google (integrating existing Firebase Auth setup in `auth.js` and `firebase-config.js`).
  - **Player Avatars:**
    - Player's Google Profile Picture (PFP).
    - Or an avatar emoji of their choosing (presenting animal and plant emojis as primary suggestions: 🦁, 🐬, 🦉, 🌿, 🍄, 🐙, 🦊, 🐢).
  - **Live Guess Feed:** Each guess appears in real-time labeled with the player's name and avatar, updating the phylogenetic tree cooperatively.

---

### 3. 🎁 Custom Puzzle Generator ("Challenge a Friend")
- **Goal:** Allow players to pick a specific organism and send a custom puzzle challenge link to a friend.
- **Core Features:**
  - **Target Selection:** Search and choose any organism from the catalog—either a specific species (*Peregrine Falcon*, *Atlantic Sand Fiddler Crab*) or a common umbrella taxon (*Barn Owl*, *Fiddler Crab*, *Electric Eel*).
  - **Secure Link Encoding:** Encode the target ID in the URL hash or query string (e.g., `?custom=...`) using lightweight encryption/obfuscation so inspecting the URL does not spoil the answer.
  - **Custom Gameplay Screen:** Displays "Custom Puzzle by [Friend]" with standard divergence feedback and a customized victory share banner.

---

### 4. 🎨 Unique Brand Logo Redesign
- **Goal:** Replace the generic system emoji with a distinctive, professional Phylogenle brand logo.
- **Design Directives:**
  - Retain the iconic DNA double-helix theme (`🧬`), but fuse it with phylogenetic tree branching / cladogram nodes.
  - Deliver clean, responsive SVG assets for both light and dark backgrounds, browser favicon, and OpenGraph social preview cards.

---

### 5. 🐾 UI Polish: Thematic Nature & Animal Emoji Decoration
- **Goal:** Bring the interface to life with curated animal and plant emoji accents across key user touchpoints.
- **Placement Ideas:**
  - Modal headers (About modal, Help modal, Difficulty selector).
  - Victory and Game Over celebration banners.
  - Clade category badges (e.g. 🦁 Mammals, 🦅 Birds, 🌿 Plants, 🍄 Fungi, 🦠 Microbes).
  - Interactive tree divergence cards and autocomplete hints.

---

### 6. 🔍 Missing Animals Inquiry & Gap Analysis
- **Goal:** Systematic workflow to audit and explain why certain user-requested or iconic animals may be missing from autocomplete or daily puzzle tiers.
- **Investigation Checklist:**
  - Is it present in the 29,609-entry master catalog under an alternate common name or scientific synonym?
  - Was it excluded from ranked difficulty tiers because $S_{\text{wiki}} \le 1$ or $V_{\text{wiki}} \le 1$?
  - Does it need an alias mapped in `data/species_aliases.json` (e.g. colloquial or regional common names)?
  - Does it represent an umbrella group that needs an explicit higher-level taxon node in `data/phylogeny_tree.json`?
