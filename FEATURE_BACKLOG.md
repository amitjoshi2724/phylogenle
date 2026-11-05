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
- **💬 Amit's Raw Notes:**
  - *(Drop quick thoughts, quirks, or ideas for this item here)*
  Yea like there should be some sort of index (one for each game mode btw) that knows that batch 1 has this many things, so the prng should never pick more than that number of things from batch 1 for the days in which only batch 1 is active. then for the days where batch 2 is active, generate a random number from 1 to n where n is the number of things in batch 1 + the number of things in batch 2, and then go into the right batch using arithmetic and then find out what the target is. the practice mode should always be up-to-date btw

---

### 2. 🤝 Cooperative Real-Time Multiplayer Mode (Redactle-Style) [COMPLETED]
- **Goal:** Allow friends to join a shared game session via a share link and guess together collaboratively.
- **Core Features Implemented:**
  - **In-Game & Header Room Creation:** "Play with Friends" button accessible directly on the in-game action bar (alongside Guess, Hint, Give Up) and in the top navigation bar (`id="coop-nav-btn"`).
  - **Seamless Mid-Game Promotion:** Players can begin solo, click "Play with Friends" mid-game, and instantly convert their active game into a live room (`?room=XYZ-123`) without losing existing guesses, hints, or target species.
  - **Authentication & Guest Mode:** Integrates with Google Auth (`auth.js`) for profile pictures / names, while also supporting guest players with local animal avatar selection and custom nicknames.
  - **Animal & Plant Avatar Palette:** Interactive selector for 18 avatars (🦁, 🦊, 🐺, 🐻, 🐼, 🐨, 🦅, 🦉, 🐸, 🐢, 🐙, 🐬, 🦈, 🦋, 🐝, 🌿, 🍄, 🌵).
  - **Live Guess & Hint Feed:** Each guess and hint card displays a real-time badge with the author's avatar and name (`.coop-player-tag`), with automatic cladogram tree synchronization.
  - **Persistent Co-Op Status Bar:** Displays active room code, live pulse indicator, connected participants, one-click link copying, and leave button.
  - **All-Player Stats Synchronization:** When a co-op game is solved, `recordDailyCompletion` / `recordPracticeCompletion` is automatically invoked on both/all connected players' browsers to update their streaks, win percentage, guess distribution, and cloud backup.
  - **Hardened Firestore Security Rules:** Authored via `firestore-rules-author` subagent in `firestore.rules`, allowing public read access for room links, schema validation on creation, immutability of core puzzle fields on update, and creator-only deletion.
- **💬 Amit's Raw Notes:**
  - *(Drop quick thoughts, quirks, or ideas for this item here)*
  like uk how in spaceship flight you can join a server with a code, and then you see other people joining with their little cursor things, and you can see their names and their little cursors, and you can see them solving the puzzle, and you can see them chatting with each other? something like that but for phylogenle. so basically you copy the link, send it to your friend, and then they join the server with the code, and then you can see them on the phylogenetic tree, and you can see them guessing, and you can see them chatting with each other. except you can't see their names or their cursors or them guessing, you can only see the things that they guess, and you can see the phylogenetic tree updating in real time with their guesses. so yeah, basically just spaceship flight online coop but for phylogenle.
- **🛠️ Technical Implementation & Architecture Notes:**
  - **Files Created / Modified:**
    - `coop.js`: Core ES6 module managing Firestore real-time room operations, state subscription, player identities, and guess/hint submission.
    - `firestore.rules`: Production security rules governing `/coop_rooms/{roomId}` access, field immutability, schema validation, and participant boundaries.
    - `script.js`: Game loop integration, mid-game promotion handler (`promoteSoloGameToCoop`), live board rendering, and multiplayer stats synchronization.
    - `index.html`: Markup for header Co-op button (`#coop-nav-btn`), action bar button (`#in-game-coop-btn`), status bar (`#coop-status-bar`), and modal (`#coop-modal`).
    - `style.css` & `modals.css`: Responsive styles for player badges, pulsing indicators, avatar palettes, and lobby cards.
    - `tests/test_coop_multiplayer.py`: Automated unit and integration test suite.
  - **Firestore Schema & Data Model (`coop_rooms/{roomId}`):**
    ```typescript
    interface CoopRoomDocument {
      roomId: string;             // 6-char alphanumeric code (e.g., "7K9M2P")
      createdAt: FieldValue;      // Firestore serverTimestamp()
      creatorId: string;          // UID or local guest identifier
      dateStr: string;            // Puzzle date string (e.g. "2026-11-05")
      puzzleNum: number;          // Sequential puzzle number
      gameMode: "daily" | "practice";
      targetSpecies: string;      // Canonical target organism
      guesses: Array<{
        name: string;             // Submitted species string
        wikiTitle: string;        // Canonical Wikipedia slug
        isMatch: boolean;         // Whether this guess solved the puzzle
        guessedAlias?: string;    // Alias used if matched via synonym
        lca_rank: string;         // Shared taxonomic rank
        lca_name: string;         // Shared clade name
        tmrca: number;            // Divergence in MYA
        player: { id: string; name: string; avatarEmoji: string; };
      }>;
      hints: Array<{
        rank: string;             // e.g. "Family", "Order"
        name: string;             // Taxon name
        type: string;             // "taxon" | "species"
        player: { id: string; name: string; avatarEmoji: string; };
      }>;
      participants: Record<string, {
        id: string;
        name: string;
        avatarEmoji: string;
        joinedAt: number;
        lastSeen: number;
      }>;
      solved: boolean;            // Global room solved state
      winner: { id: string; name: string; avatarEmoji: string; } | null;
    }
    ```
  - **Live Sync & Snapshot Listener Protocol:**
    - `subscribeToRoom(roomId)` binds an `onSnapshot` listener to the Firestore document.
    - Emits internal events via `onCoopEvent(callback)`:
      - `ROOM_UPDATE`: Triggers differential ingestion of newly arrived guesses and hints without re-rendering existing items.
      - `ROOM_SOLVED`: Triggers end-game sequence, renders victory modal, and records stats.
      - `ROOM_LEFT`: Cleans up local listeners and resets the top status bar.
  - **Mid-Game Solo-to-Co-op Promotion (`promoteSoloGameToCoop`):**
    - A player who began guessing in solo mode can click `#in-game-coop-btn` mid-game.
    - The active `guesses`, `revealedHints`, `targetSpecies`, and `currentDateStr` are bundled into the initial room payload.
    - The URL is updated via `history.replaceState` to `?room=XYZ123` without reloading the page, seamlessly promoting the solo session to a live room.
  - **Dual / All-Player Stats Synchronization:**
    - When any participant submits the winning guess, the room document transitions to `solved: true` with the `winner` profile.
    - In `script.js`'s `ROOM_SOLVED` event handler, every active client invokes `recordDailyCompletion` or `recordPracticeCompletion` in `storage.js`.
    - Both/all participants earn the victory in their personal stats, streak counter, guess distribution chart, and cloud backup.
  - **Firestore Security Rules Invariants (`firestore.rules`):**
    - **Read:** Publicly readable (`allow read: if true;`) so anyone with the 6-character room code can view and join.
    - **Create:** Validates required keys, bounds participant map size ($\le 20$), enforces correct field types, and ensures `solved == false` and `winner == null`.
    - **Update Immutability:** Core puzzle fields (`targetSpecies`, `roomId`, `dateStr`, `createdAt`, `creatorId`, `gameMode`) are verified strictly equal to `resource.data` and cannot be modified by any client.
    - **Append-Only Guess/Hint History:** Guesses and hints can only grow in size; past guesses cannot be overwritten, reordered, or deleted.
    - **Winner Integrity:** `winner` can only transition from `null` to a non-null map when `solved` transitions from `false` to `true`.
    - **Delete:** Restricted exclusively to the room creator (`request.auth.uid == resource.data.creatorId`).
  - **Verification & Terminal Tests:**
    - Run: `python3 -m unittest tests/test_coop_multiplayer.py` (verifies API exports, HTML DOM controls, CSS classes, security rules, and script wiring).

---

### 3. 🎁 Custom Puzzle Generator ("Challenge a Friend") [COMPLETED]
- **Goal:** Allow players to pick a specific organism and send a custom puzzle challenge link to a friend.
- **Core Features Implemented:**
  - **Header & End-Game Triggers:** "🎁 Challenge" button accessible in top navigation (`#challenge-modal-btn`) and "🎁 Challenge a Friend" button on the victory/reveal card (`#end-challenge-friend-btn`), which automatically pre-populates the round's solved mystery organism.
  - **Organism Search & Direct Wikipedia URL Resolution:** Fast autocomplete over the master species catalog and aliases, plus automatic resolution of pasted Wikipedia URLs (desktop `https://en.wikipedia.org/wiki/...` and mobile `https://en.m.wikipedia.org/wiki/...`) into canonical organisms.
  - **Obfuscated Salt-Keyed URL Token (`challenge.js`):** Encodes payload into URL parameter `?challenge=c1_...` using a 4-byte randomized salt and deterministic keystream so inspecting the URL or page source never leaks the target answer, and identical organisms produce distinct tokens.
  - **Custom Challenge Gameplay Screen:** Features top puzzle badge `🎁 CHALLENGE • BY [CREATOR]`, customized challenge banner with friend's message/taunt, and a quick `Exit ✕` button to return to the daily puzzle.
  - **Customized Share Result:** Custom victory banner ("Challenge Conquered! 🏆") and share snippet containing creator credit and the direct challenge link.
  - **Automated Test Coverage:** Complete test suite in `tests/test_custom_challenge.py` testing encryption/decryption, Wikipedia URL resolver, DOM elements, and UI wiring.
- **💬 Amit's Raw Notes:**
  - *(Drop quick thoughts, quirks, or ideas for this item here)*
  yea as long as the encryption is not genuinely readable by a casual human its chill. even textbook rsa is fine right? idk tho u decide
- **🛠️ Technical Implementation & Architecture Notes:**
  - **Files Created / Modified:**
    - `challenge.js`: Core module handling salt-keyed keystream encryption/decryption, Wikipedia link resolution, and URL formatting.
    - `script.js`: Game controller handling `?challenge=`, `?custom=`, `?wiki=`, and `?organism=` URL routing, custom challenge modal autocomplete, and share formatting.
    - `index.html`: Custom Challenge modal (`#challenge-modal`), in-game banner (`#challenge-banner`), nav trigger (`#challenge-modal-btn`), and end panel button (`#end-challenge-friend-btn`).
    - `style.css` & `modals.css`: Styling for challenge banner, modal dialog, autocomplete dropdown, action buttons, and exit pill.
    - `tests/test_custom_challenge.py`: Comprehensive test suite covering encryption/decryption, salt randomization, Wikipedia URL parsing, HTML elements, and UI events.
  - **🎓 Theory & Concept: What is a "Salt" and Why Do We Need It?**
    - **The Core Problem:**
      - If you want to send a secret organism (like `"Honey badger"`) in a URL link so your friend's browser can calculate divergence distances, you have to transmit that information somehow.
      - If you use plain text (`?target=Honey badger`), anyone looking at the link immediately has the puzzle spoiled.
      - If you use standard Base64 encoding, anyone who recognizes the letters or pastes it into any decoder sees `"Honey badger"` immediately.
      - What if we used a fixed cipher or hash? If `"Honey badger"` *always* turns into `XYZ123`, then every time you challenge a friend to Honey badger, the URL will be `XYZ123`. A player can simply memorize or look up `XYZ123` to instantly know the answer before making a single guess! This is known as a **precomputed dictionary attack** (or rainbow table).
    - **What "Salt" Means (The Intuitive Metaphor):**
      - In cooking, salt is a small random ingredient you sprinkle into a dish.
      - In cryptography, a **"Salt"** is simply a random chunk of unpredictable data (in our case, a 4-byte random number generated on the spot) combined with the secret data *before* encrypting it.
      - Because the salt is freshly randomized every single time you click "Generate Link":
        - Round 1 (Salt = `349821`): `"Honey badger"` $\to$ `c1_8b77lfqsWYUk...`
        - Round 2 (Salt = `981240`): `"Honey badger"` $\to$ `c1_Ds5Ff0ew1pJU...`
      - Even though the secret organism is identical, the two generated URLs look 100% completely different! There is zero pattern between them, and nobody can build a cheat sheet of URLs.
    - **How Does the Receiver Decrypt It?**
      - The salt does *not* need to be kept secret—it just needs to be random!
      - We attach the 4-byte salt to the very front of the encrypted token.
      - When your friend opens the link, their browser reads those first 4 bytes to find out what salt was used, re-generates the exact matching keystream, and unscrambles the organism name.
  - **Obfuscated Keystream Encryption Algorithm & Constants:**
    - **Constants & Versioning:**
      - Version Prefix: `c1_` (enables backwards-compatible protocol upgrades in future versions).
      - Mixing Constant: `SECRET_KEY_HASH = 0x85ebca6b`.
      - PRNG Multiplier: `0x6D2B79F5` (fractional part of the golden ratio $2^{32} \cdot (\sqrt{5}-1)/2$, standard in SplitMix32 for maximum bit diffusion).
    - **4-Byte Randomized Salt Generation:**
      - Drawn via: `salt = (Math.floor(Math.random() * 0xFFFFFFFF) >>> 0)`.
    - **How the Keystream & XOR Work ($P \oplus K = C$ and $C \oplus K = P$):**
      - A **keystream** is an endless stream of pseudo-random bytes generated from the salt.
      - **XOR ($\oplus$)** has a magical mathematical property: **If you XOR a number with a key, and then XOR it with the same key again, you get the original number back!**
        - Example: Letter `'A'` (binary `01000001`) $\oplus$ Key byte (`10110010`) = Cipher byte (`11110011`).
        - Take Cipher byte (`11110011`) $\oplus$ Key byte (`10110010`) = Letter `'A'` (`01000001`)!
      - So the generator produces one keystream byte for each character of the JSON payload `{ t: "Honey badger", c: "Amit", m: "Beat my score!" }`.
      - Masking them byte-by-byte creates the ciphertext.
    - **Step-by-Step Walkthrough:**
      1. Player picks `"Honey badger"`.
      2. App creates JSON payload: `{"t":"Honey badger","c":"Amit","m":"Beat this!","v":1}`.
      3. App converts this string into raw UTF-8 bytes (length $L$).
      4. App generates a fresh 4-byte random `salt`.
      5. The PRNG uses `salt ^ SECRET_KEY_HASH` to produce $L$ keystream bytes.
      6. Each payload byte is XOR'd with its matching keystream byte.
      7. The 4 salt bytes are placed at the front, followed by the XOR'd bytes.
      8. The entire byte array is encoded into URL-safe Base64 (`+` $\to$ `-`, `/` $\to$ `_`, trailing `=` removed) and prefixed with `c1_`.
      9. Your friend clicks the link: their browser strips `c1_`, decodes the Base64, extracts the 4 salt bytes, regenerates the identical keystream, XORs the ciphertext bytes, and instantly recovers the original JSON!
  - **Wikipedia URL & Query Resolver (`resolveWikipediaUrlOrQuery`):**
    - Strips URL schemes, domain (`en.wikipedia.org` or `en.m.wikipedia.org`), path prefixes (`/wiki/`), anchor hashes (`#...`), and query parameters (`?veaction=...`).
    - Decodes URI encoding (`%20`, `%C3%A9`) and replaces underscores with spaces.
    - Resolution Priority:
      1. Exact match in `allSpecies`.
      2. Common name or Latin binomial match extracted from `allSpecies` format (`"Common (Scientific)"`).
      3. Synonym match in `speciesAliases` dictionary.
      4. Clade or genus match against `phylogenyTree.nodes` (matching `wiki_title` or node `name`).
      5. Substring prefix fallback in `allSpecies`.
  - **Dual Launch Workflow (`✨ Link for Friend` vs `▶️ Play Solo`):**
    - **Send to Friend:** Clicking `✨ Link for Friend` generates the encrypted URL token and displays a one-click clipboard copy card with toast confirmation.
    - **Play Solo:** Clicking `▶️ Play Solo` bypasses link sharing, immediately mounts the chosen organism onto the player's board, and begins a solo mystery challenge.
    - **Address Bar Direct Support:** Entering `?wiki=https://en.wikipedia.org/wiki/Peregrine_falcon` or `?organism=Peregrine_falcon` into the URL bar triggers automatic conversion into an obfuscated token on page load, hiding the answer from the address bar.
    - **Exit Pill:** In-game challenge banner includes a pink `Exit ✕` button (`#challenge-exit-btn`) allowing the player to safely abort and return to the daily puzzle.
  - **Verification & Terminal Tests:**
    - Run: `python3 -m unittest tests/test_custom_challenge.py` (tests encryption/decryption, salt randomization, Wikipedia URL parsing across desktop/mobile/encoded formats, HTML DOM elements, and UI event wiring).

---

### 4. 🎨 Unique Brand Logo Redesign
- **Goal:** Replace the generic system emoji with a distinctive, professional Phylogenle brand logo.
- **Design Directives:**
  - Retain the iconic DNA double-helix theme (`🧬`), but fuse it with phylogenetic tree branching / cladogram nodes.
  - Deliver clean, responsive SVG assets for both light and dark backgrounds, browser favicon, and OpenGraph social preview cards.
- **💬 Amit's Raw Notes:**
  - *(Drop quick thoughts, quirks, or ideas for this item here)*
yea ill j try to ai generate ts. my idea is to maybe have square emojis and the tree and the dna thingy kinda fused together, or maybe just a cool abstract logo with those things somewhere in it. something that 
---

### 5. 🐾 UI Polish: Thematic Nature & Animal Emoji Decoration
- **Goal:** Bring the interface to life with curated animal and plant emoji accents across key user touchpoints.
- **Placement Ideas:**
  - Modal headers (About modal, Help modal, Difficulty selector).
  - Victory and Game Over celebration banners.
  - Clade category badges (e.g. 🦁 Mammals, 🦅 Birds, 🌿 Plants, 🍄 Fungi, 🦠 Microbes).
  - Interactive tree divergence cards and autocomplete hints.
- **💬 Amit's Raw Notes:**
  - *(Drop quick thoughts, quirks, or ideas for this item here)*

---

### 6. 🔍 Missing Animals Inquiry & Gap Analysis
- **Goal:** Systematic workflow to audit and explain why certain user-requested or iconic animals may be missing from autocomplete or daily puzzle tiers.
- **Investigation Checklist:**
  - Is it present in the 29,609-entry master catalog under an alternate common name or scientific synonym?
  - Was it excluded from ranked difficulty tiers because $S_{\text{wiki}} \le 1$ or $V_{\text{wiki}} \le 1$?
  - Does it need an alias mapped in `data/species_aliases.json` (e.g. colloquial or regional common names)?
  - Does it represent an umbrella group that needs an explicit higher-level taxon node in `data/phylogeny_tree.json`?
- **💬 Amit's Raw Notes:**
  - *(Drop quick thoughts, quirks, or ideas for this item here)*

---

## 🧠 Amit's Scratchpad & Brain Dump (Raw / Unformatted Notes)

> 💡 **No Rules / No Formatting Required:**  
> Use this section as your personal scratchpad. Ramble, paste links, dump half-baked thoughts, list random animals to check, or vent about anything here. The assistant will always read this section to understand your thoughts without you having to clean it up or format it!

<!-- 👇 DROP YOUR RAW RAMBLINGS / BRAIN DUMPS BELOW THIS LINE 👇 -->

- [x] fix readme to show that the target organism is not necessarily a species, sometimes genus or family or even order
  - **🛠️ Technical Fix & Implementation Summary:**
    - **Files Modified:** `README.md` (Lines 16, 42–45).
    - **Documentation Clarification:** Added a dedicated callout block (`[!NOTE]`) detailing that mystery targets in Phylogenle are not restricted to individual species binomials (*Panthera leo*), but frequently encompass iconic higher-rank **umbrella taxa** including **Genera** (*Cygnus* / Swan, *Macropus* / Kangaroo, *Amphiprion* / Clownfish), **Families** (*Trochilidae* / Hummingbirds, *Theraphosidae* / Tarantulas), **Orders** (*Siluriformes* / Catfish, *Lophiiformes* / Anglerfish), and **Classes** (*Cubozoa* / Box Jellyfish).
    - **Scoring Invariant Documented:** Clarified that when an umbrella taxon is the secret target, guessing **any** subordinate species or sub-clade within that group scores as an exact match (`0.0 MYA`).
    - **In-App Taxonomic Notice:** Documented the post-round disclosure card (`.genus-notice-box` in `script.js`) that automatically alerts players whenever the solved target organism was a higher-order taxon.

- [x] alias overrides; sometimes the most common name for a species is not the shortest, so it wasn't selected as the main common name. allow me to manually set the common name for things for example honey badger instead of ratel. I will be the one to come up w these overrides just get the functionality in place for me to do so.
  - **🛠️ Technical Fix & Implementation Summary:**
    - **Files Created / Modified:**
      - `set_common_name_override.py`: Production CLI utility to inspect, apply, and revert common name overrides.
      - `data/species_common_name_overrides.json`: Persistent source-of-truth JSON dictionary mapping scientific names to manual common names (`{ "Mellivora capensis": "Honey Badger" }`).
      - `tests/test_common_name_overrides.py`: Test suite verifying CLI argument parsing, dry-run safety, and data integrity.
    - **Atomic Multi-Dataset Synchronization:** Running `set_common_name_override.py --apply` atomically updates 6 project files without breaking cladogram references or PRNG seeds:
      1. `data/species_taxonomy_catalog.json`: Updates the organism's `common` and `display` strings.
      2. `data/species_list.json`: Updates the canonical search and autocomplete display entry.
      3. `data/phylogeny_tree.json`: Updates the `species` dictionary key while preserving identical tree branch topology, LCA parent nodes, and divergence timings.
      4. `data/species_aliases.json`: Moves the displaced algorithmic name (e.g. "Ratel") into the alias map pointing to the new canonical name; removes the new name from alias keys to prevent circular synonym redirects.
      5. `data/wikimedia_popularity_cache.json`: Synchronizes the cached `common` field.
      6. `species_catalog_taxonomic.md`: Automatically re-invokes `build_taxonomic_catalog.py` to regenerate the Markdown documentation directory.
    - **CLI Commands Reference:**
      ```bash
      # Add or update an override by scientific or current common name:
      python3 set_common_name_override.py "Mellivora capensis" "Honey Badger"
      python3 set_common_name_override.py "Ratel" "Honey Badger"
      python3 set_common_name_override.py --set "Mellivora capensis" "Honey Badger"

      # List all currently active manual overrides:
      python3 set_common_name_override.py --list

      # Revert an override back to the algorithmic shortest name:
      python3 set_common_name_override.py --remove "Mellivora capensis"

      # Re-apply all persisted overrides to datasets on disk:
      python3 set_common_name_override.py --apply

      # Test run without modifying disk:
      python3 set_common_name_override.py --set "Mellivora capensis" "Honey Badger" --dry-run
      ```
    - **Verification & Terminal Tests:**
      - Run: `python3 -m unittest tests/test_common_name_overrides.py`

- more umbrella taxa? such as collapsing all fiddler crabs into "fiddler crab", all pumas into "puma", etc. i want there to be a good selection of umbrella taxa

- [x] support creation of puzzles to send to a friend or play by urself via wikipedia link (as well as j searching it up urself in the catalog)
  - **🛠️ Technical Fix & Implementation Summary:**
    - **Files Created / Modified:** `challenge.js`, `script.js`, `index.html`, `tests/test_custom_challenge.py`.
    - **Integration Architecture:** Solved in tandem with Backlog Item #3.
    - **Dual Player Flow:**
      - **Send to Friend:** Clicking `✨ Link for Friend` in `#challenge-modal` encrypts the organism into an obfuscated token (`?challenge=c1_...`) with random 4-byte salt and provides a one-click clipboard copy card.
      - **Play Solo Instantly:** Clicking `▶️ Play Solo` (`#challenge-play-direct-btn`) immediately starts the puzzle on the active board without generating or copying a share link.
      - **Direct URL Resolution:** Users can enter `?wiki=https://en.wikipedia.org/wiki/Honey_badger` or `?organism=Honey_badger` directly into their browser address bar; `checkURLParams()` resolves the target, converts the URL parameter to `?challenge=c1_...` on load to hide spoilers, and loads the game.
    - **Wikipedia Resolver Engine:** `resolveWikipediaUrlOrQuery()` handles desktop and mobile URLs (`en.wikipedia.org/wiki/...`, `en.m.wikipedia.org/wiki/...`), strips query strings, decodes URI escapes, and matches across canonical names, synonyms, and clade tree nodes.
    - **Verification & Terminal Tests:**
      - Run: `python3 -m unittest tests/test_custom_challenge.py`

- [x] More intense wikipedia integration, can open the wiki page of any organism within the website itself, instead of having to open a new tab. Facilitates learning and overcomes the mental obstacle of opening a new tab. Connect each species or clade or genus or anything like that to its own wikipedia page. And use this info to display the common name of each taxonomic rank/subclade in the tree and guess list. Uk how theres an 'catalog' button within the guess? Next to it there should be a wikipedia button that opens up a pane within our website for that lca node. It shows the common name of that taxonomic rank/subclade or even species. And that pane should have clickable links to allow the users to explore a bit
  - **🛠️ Technical Fix & Implementation Summary:**
    - **Files Created / Modified:**
      - `wikimedia_taxonomy_pipeline.py`: Unified pipeline connecting all catalog species (Steps 1–4) and all non-species tree nodes (Steps 5–7) to canonical Wikimedia articles and verified vernacular names.
      - `sync_tree_wikipedia_and_common_names.py`: Standalone algorithmic resolver querying MediaWiki REST/SPARQL APIs in 50-item batches with redirect chain following and NCBI Taxdump integration.
      - `data/clade_common_names.json`: Generated dictionary mapping clade names to verified biological common names.
      - `data/phylogeny_tree.json`: Attached `wiki_title` and `common_name` directly to tree nodes.
      - `index.html`: Built sliding Wikipedia side drawer (`#wiki-drawer`) with header navigation, retry boundaries, theme toggle, and external link buttons.
      - `script.js`: Iframe sandboxing (`sandbox="allow-scripts allow-same-origin allow-popups"`), fast MediaWiki REST summary fallback (`https://en.wikipedia.org/api/rest_v1/page/summary/...`), clade label augmentation in D3 cladogram, and drawer buttons on guess cards.
      - `style.css`: Sliding drawer animations, responsive mobile viewport constraints, and dark/light iframe theme overrides.
      - `tests/test_sync_script.py` & `tests/test_wiki_integration.py`: Test suites verifying API batch queries, redirect resolution, iframe security attributes, and UI drawer behavior.
    - **Algorithmic Disambiguation & Anti-Poisoning Architecture:**
      - Completely replaces ad-hoc or LLM guesswork with strict, verifiable joins:
        1. Exact NCBI taxid join: Wikidata item where P685 (NCBI Taxon ID) matches node taxid.
        2. Homonym-safe scientific name join: Wikidata item where P225 matches node name and P685 does not conflict with a different NCBI taxon.
        3. MediaWiki redirect resolution: Queries MediaWiki API batch for canonical titles, following multi-hop redirect chains (e.g. `Mammalia` $\to$ `Mammal`, `Clupeocephala` $\to$ `Teleost`).
      - Verified English Common Name Priority:
        1. Wikidata P1843 ("taxon common name" in English).
        2. MediaWiki article title when verified as a vernacular name of the exact taxon (e.g. *Aves* $\to$ "Bird", *Anura* $\to$ "Frog").
        3. NCBI `taxdump/names.dmp`: GenBank common name $>$ common name $>$ BLAST name.
      - Transient network errors are never poisoned as "no article" (cached as `None` or `error` for safe retry).
    - **In-Game UX:**
      - Guess cards include a dedicated 📖 Wikipedia button next to the Catalog button, opening the drawer directly to that LCA node's article.
      - D3 Cladogram nodes display verified common names alongside scientific clades (e.g., `Aves (Birds)`, `Cetacea (Whales & Dolphins)`).
    - **Verification & Terminal Tests:**
      - Run: `python3 -m unittest tests/test_sync_script.py tests/test_wiki_integration.py`