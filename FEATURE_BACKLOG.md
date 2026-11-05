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

---

### 3. 🎁 Custom Puzzle Generator ("Challenge a Friend")
- **Goal:** Allow players to pick a specific organism and send a custom puzzle challenge link to a friend.
- **Core Features:**
  - **Target Selection:** Search and choose any organism from the catalog—either a specific species (*Peregrine Falcon*, *Atlantic Sand Fiddler Crab*) or a common umbrella taxon (*Barn Owl*, *Fiddler Crab*, *Electric Eel*).
  - **Secure Link Encoding:** Encode the target ID in the URL hash or query string (e.g., `?custom=...`) using lightweight encryption/obfuscation so inspecting the URL does not spoil the answer.
  - **Custom Gameplay Screen:** Displays "Custom Puzzle by [Friend]" with standard divergence feedback and a customized victory share banner.
- **💬 Amit's Raw Notes:**
  - *(Drop quick thoughts, quirks, or ideas for this item here)*
  yea as long as the encryption is not genuinely readable by a casual human its chill. even textbook rsa is fine right? idk tho u decide

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

- [x] alias overrides; sometimes the most common name for a species is not the shortest, so it wasn't selected as the main common name. allow me to manually set the common name for things for example honey badger instead of ratel. I will be the one to come up w these overrides just get the functionality in place for me to do so.

- more umbrella taxa? such as collapsing all fiddler crabs into "fiddler crab", all pumas into "puma", etc. i want there to be a good selection of umbrella taxa

- support creation of puzzles to send to a friend or play by urself via wikipedia link (as well as j searching it up urself in the catalog)

- [x] More intense wikipedia integration, can open the wiki page of any organism within the website itself, instead of having to open a new tab. Facilitates learning and overcomes the mental obstacle of opening a new tab. Connect each species or clade or genus or anything like that to its own wikipedia page. And use this info to display the common name of each taxonomic rank/subclade in the tree and guess list. Uk how theres an 'catalog' button within the guess? Next to it there should be a wikipedia button that opens up a pane within our website for that lca node. It shows the common name of that taxonomic rank/subclade or even species. And that pane should have clickable links to allow the users to explore a bit