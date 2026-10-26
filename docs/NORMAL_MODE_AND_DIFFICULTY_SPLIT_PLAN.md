# 🧬 Comprehensive Architecture Plan: Normal Mode & Difficulty Tier Split

> **Status:** Proposed & Awaiting User Approval  
> **Author:** Antigravity  
> **Target System:** Phylogenle Web Application & Data Pipeline  
> **Related Documents:** [`docs/species_catalog_ORIGINAL_UNTOUCHED.md`](file:///Users/amitjoshi2724/Desktop/phylogenle/docs/species_catalog_ORIGINAL_UNTOUCHED.md), [`docs/TAXONOMIC_CATALOG_PLAN.md`](file:///Users/amitjoshi2724/Desktop/phylogenle/docs/TAXONOMIC_CATALOG_PLAN.md)

---

## 1. Executive Summary & Vision

Phylogenle currently contains **29,748 species** spanning all kingdoms of life (including microscopic fungi, deep-sea invertebrates, regional salamanders, and obscure plants). While scientifically extraordinary, having this entire pool active by default makes the daily puzzle and practice mode frustratingly difficult for general players:
- Autocomplete floods players with dozens of obscure regional variants and scientific names.
- Daily puzzle targets can turn out to be obscure organisms like *"Darwin's Slimehead"* or *"Miquihuana Splayfoot Salamander"*.
- General players who love animals cannot reasonably guess such extreme long-tail organisms.

### The Solution: Two Fully Partitioned Difficulty Tiers
1. **Normal Mode (Default):**
   - A carefully curated, recognizable, and fun pool of **~850 to 1,000 iconic animals** (*Kingdom Animalia* only).
   - Features **100% of the original untouched species** (the 344 animals) plus the most well-known, charismatic, and taxonomically diverse animals from the current dataset.
   - Separate Daily Puzzle and Practice Mode.
   - Dedicated Normal Mode Taxonomic Catalog.
   - Lightweight, lightning-fast initial page load (~1.2 MB total data vs. 25 MB).
2. **Hard Mode (Expert Tier):**
   - Retains the entire **29,748-species master tree of life** (all kingdoms, microbes, plants, fossils, and deep-sea taxa).
   - Separate Hard Daily Puzzle and Hard Practice Mode.
   - Retains the full 29,748 Taxonomic Catalog.

Both modes are accessible seamlessly via clean segmented controls, with independent stats, streaks, history, and URL persistence.

---

## 2. Methodology: Constructing & Defining the "Normal Animal Set"

### A. The Core Foundation (Guaranteed 100%)
- **The Original 344 Untouched Animals** from [`docs/species_catalog_ORIGINAL_UNTOUCHED.md`](file:///Users/amitjoshi2724/Desktop/phylogenle/docs/species_catalog_ORIGINAL_UNTOUCHED.md):
  - 148 Mammals (Big Cats, Canines, Bears, Marine Mammals, Primates, Ungulates)
  - 57 Birds (Raptors, Owls, Waterfowl, Parrots, Songbirds)
  - 58 Invertebrates (Octopuses, Squids, Butterflies, Bees, Crabs)
  - 33 Fishes (Sharks, Rays, Salmon, Tuna, Clownfish)
  - 32 Reptiles (Crocodilians, Snakes, Lizards, Sea Turtles)
  - 16 Amphibians (Poison Dart Frogs, Tree Frogs, Salamanders)
  - *All 344 are already present and calibrated in the current phylogeny tree.*

### B. Defining "Main Animals" from the 29,748 Master Dataset
To expand from 344 to an optimal pool of **~850 to 1,000 species**, candidate species must satisfy four strict, objective criteria:

1. **Kingdom Filter (*Animalia* Only):**
   - Plants (e.g. *Arizona Lupine*), fungi, bacteria, and archaea are excluded from Normal Mode to keep the puzzle focused on the animal kingdom.
2. **Verified English Common Name Presence:**
   - Must have an established, natural, recognizable English name (e.g., *"Koala"*, *"Axolotl"*, *"Capybara"*, *"Harpy Eagle"*, *"Great White Shark"*, *"Honey Badger"*).
   - Excludes obscure regional variants named after researchers or hyper-local creeks (e.g. *"Koningsberger's Herring"*).
3. **Wikipedia Popularity & Cultural Prominence:**
   - We utilize the verified candidate pool in `archive/legacy_scripts/` (981 curated candidate animals) and cross-reference with Wikipedia traffic and zoo/IUCN fauna registries.
   - High-traffic, beloved animals that players actually know and search for are prioritized.
4. **Taxonomic Diversity & Clade Balance Quota:**
   - Instead of lopsided clustering (e.g., 80 species of mice), each major branch of the animal tree receives a balanced allocation of recognizable representatives:
     - **Mammalia (~320 species):** Primates (Chimp, Orangutan, Lemur, Baboon), Carnivora (Lion, Cheetah, Wolf, Otter, Fennec Fox), Cetacea (Orca, Beluga, Blue Whale), Marsupials (Kangaroo, Koala, Wombat, Tasmanian Devil), Bats, Rodents, Ungulates.
     - **Aves (~220 species):** Birds of Prey (Bald Eagle, Peregrine Falcon, Osprey), Owls, Waterfowl, Penguins (Emperor, King), Parrots (Scarlet Macaw), Toucans, Hummingbirds, Peacocks, Flamingos.
     - **Reptiles & Amphibians (~140 species):** Crocodiles, Alligators, Komodo Dragon, Chameleons, Geckos, Cobras, Anacondas, Tortoises, Axolotl, Bullfrog, Fire Salamander.
     - **Fishes (~140 species):** Great White Shark, Hammerhead, Manta Ray, Moray Eel, Piranha, Seahorse, Lionfish, Swordfish, Pufferfish, Clownfish.
     - **Invertebrates (~140 species):** Monarch Butterfly, Praying Mantis, Tarantula, Scorpion, Giant Squid, Blue-ringed Octopus, Hermit Crab, Honeybee, Moon Jellyfish, Starfish.

### C. Why ~850–1,000 is the Ideal Size
- **Non-Repeating Daily Puzzles:** 850–1,000 species provides **2.5 to 3 years** of unique daily puzzles without repeating a single animal.
- **Endless Practice Replayability:** A player can play 50 practice rounds in an afternoon and encounter fresh, familiar creatures each time.
- **Fair & Fun:** Every target organism is something a player could reasonably identify or learn about with excitement.

---

## 3. Web App UI & Dual-Toggle Architecture

Phylogenle will feature an intuitive, modular 2-level toggle system in the top navigation bar:

```
[ 🟢 Normal | 🔴 Hard ]       [ 📅 Daily | 🧬 Practice ]       [ 📖 Species Catalog ]
```

### A. Navigation Controls
1. **Difficulty Selector (New Segmented Pill):**
   - `[ 🟢 Normal | 🔴 Hard ]`
   - Active state: Emerald green gradient (`#10b981`) for Normal; Crimson red gradient (`#ef4444`) for Hard.
   - Smooth animated pill transitions matching our CSS design system.
2. **Game Mode Selector (Existing Segmented Pill):**
   - `[ 📅 Daily | 🧬 Practice ]`
   - Active state: Royal purple (`#7c3aed`) for Daily; Amber (`#f59e0b`) for Practice.

### B. The 4 Playable Experiences
| Difficulty | Mode | Target Audience | Target Organism Pool | Streak / Stats |
| :--- | :--- | :--- | :--- | :--- |
| **Normal** | **Daily** | Everyone (Default) | ~850–1,000 iconic animals | Normal Daily Streak |
| **Normal** | **Practice** | Casual Replay | ~850–1,000 iconic animals | Unrecorded Practice |
| **Hard** | **Daily** | Biologists & Hardcore | 29,748 Master Tree of Life | Hard Daily Streak |
| **Hard** | **Practice** | Deep Exploration | 29,748 Master Tree of Life | Unrecorded Practice |

### C. URL Query & Storage Dual-Persistence
- **URL Parameters:**
  - `/?difficulty=normal&mode=daily` (or clean default `/`)
  - `/?difficulty=normal&mode=practice`
  - `/?difficulty=hard&mode=daily`
  - `/?difficulty=hard&mode=practice`
  - Replaying past daily puzzles: `/?difficulty=normal&date=2026-10-20`
- **LocalStorage Keys:**
  - `phylogenle_difficulty`: `"normal"` | `"hard"`
  - `phylogenle_game_mode`: `"daily"` | `"practice"`
- **Behavior on Refresh:**
  - The page **never** drops back to Normal Daily if the user was on Hard Practice or Normal Practice. `checkURLParamsAndStorage()` restores the exact state.
  - Browser Back/Forward buttons update the game cleanly via `popstate`.

### D. Autocomplete Experience
- **Normal Mode:**
  - Queries only the ~850–1,000 curated animals.
  - Typing *"Bear"* shows *Grizzly Bear, Polar Bear, Black Bear, Sun Bear, Sloth Bear, Panda Bear*. No obscure regional variants.
  - Lightning-fast typing response with zero lag.
- **Hard Mode:**
  - Queries all 29,748 species using our existing infinite-scroll progressive dropdown with clade/subclade badges.

---

## 4. Taxonomic Species Catalog for Normal Mode

The in-app taxonomic catalog modal (`#catalog-modal`) will dynamically switch its data source based on the active difficulty tier:

### A. Normal Mode Catalog (`data/normal/species_taxonomy_catalog.json`)
- Built specifically for the ~850–1,000 normal species.
- Follows the true 8-rank Linnaean hierarchy:
  - **⬛ Domain:** *Eukaryota*
  - **🟫 Kingdom:** *Animalia*
  - **🟦 Phylum:** *Chordata, Arthropoda, Mollusca, Cnidaria, Echinodermata, Annelida*
  - **🟪 Class:** *Mammalia, Aves, Reptilia, Amphibia, Actinopterygii, Chondrichthyes, Insecta, Arachnida, Malacostraca, Cephalopoda*
  - **🟥 Order / 🟧 Family / 🟨 Genus / 🟩 Species**
- Every clade is clean, uncluttered, and recognizable. Opening *Carnivora -> Felidae* shows 15 familiar wild cats instead of 200 obscure sub-taxa.

### B. Hard Mode Catalog (`data/hard/species_taxonomy_catalog.json`)
- Retains the existing 29,748 species directory across all kingdoms (Bacteria, Fungi, Plants, Animalia, Archaea).

### C. Catalog State & Persistence
- Switching between Normal and Hard difficulty automatically swaps the loaded catalog without requiring a page reload.
- Remembers scroll position and open clades within the active tier.

---

## 5. Backend, Data Pipeline & Performance Architecture

### A. Directory Structure
```
phylogenle/
├── data/
│   ├── normal/
│   │   ├── species_list.json                 (~65 KB — 850 species)
│   │   ├── phylogeny_tree.json               (~1.2 MB — pruned animal tree)
│   │   └── species_taxonomy_catalog.json     (~1.1 MB — normal taxonomic catalog)
│   ├── hard/
│   │   ├── species_list.json                 (~1.4 MB — 29,748 species)
│   │   ├── phylogeny_tree.json               (~12.8 MB — master tree of life)
│   │   └── species_taxonomy_catalog.json     (~11.6 MB — hard taxonomic catalog)
│   └── time_cache.json                       (~79 MB — TimeTree calibrated cache)
```

### B. Pruning & Subtree Extraction Pipeline (`build_normal_dataset.py`)
To ensure mathematical perfection and 100% taxonomic consistency:
1. The script takes the master `data/hard/phylogeny_tree.json` and the curated normal species list.
2. It extracts the **exact ancestor subgraph** linking all normal species back to *LUCA / Metazoa*.
3. **Zero Time Recalculation Required:** All internal node divergence times ($T_{\text{MRCA}}$), Linnaean ranks, and clade annotations are directly inherited from the calibrated master tree.
4. Generates `data/normal/phylogeny_tree.json` and runs `build_taxonomic_catalog.py` to create the normal catalog.

### C. Performance Benefits
- **Initial Load for 95% of Users (Normal Mode):**
  - Download size drops from **14.2 MB** down to **~1.3 MB**.
  - Parse time drops from ~250ms to **under 20ms**.
  - Mobile memory footprint drops by **85%**.
- Hard mode data is only fetched asynchronously on-demand when the user clicks **🔴 Hard**.

---

## 6. Database & Storage Architecture (`storage.js` & Firebase)

To prevent Normal mode victories from inflating Hard mode streaks (and vice versa), the storage engine will strictly partition data by difficulty:

### A. LocalStorage Keys & Data Structure
```javascript
// Streaks, Win Rates, and Guess Distributions
localStorage.getItem('phylogenle_stats_normal');
localStorage.getItem('phylogenle_stats_hard');

// Daily Puzzle Completion History (Records, Guesses, Hints, Surrenders)
localStorage.getItem('phylogenle_history_normal');
localStorage.getItem('phylogenle_history_hard');

// Active In-Progress Guesses
localStorage.getItem('phylogenle_active_guesses_normal_2026-10-26');
localStorage.getItem('phylogenle_active_guesses_hard_2026-10-26');

// Active In-Progress Hints
localStorage.getItem('phylogenle_active_hints_normal_2026-10-26');
localStorage.getItem('phylogenle_active_hints_hard_2026-10-26');
```

### B. Cloud Firestore Schema (Multi-Device Sync & Google Auth)
User profile documents in collection `users/{userId}`:
```json
{
  "uid": "user_12345",
  "email": "player@example.com",
  "phylogenle_stats_normal": {
    "played": 18,
    "won": 17,
    "currentStreak": 12,
    "maxStreak": 12,
    "distribution": { "1-3": 4, "4-6": 8, "7-9": 5, "10-12": 0, "13-15": 0, "16+": 0 },
    "lastPlayedDate": "2026-10-26"
  },
  "phylogenle_stats_hard": {
    "played": 5,
    "won": 2,
    "currentStreak": 1,
    "maxStreak": 2,
    "distribution": { "1-3": 0, "4-6": 1, "7-9": 0, "10-12": 1, "13-15": 0, "16+": 0 },
    "lastPlayedDate": "2026-10-25"
  },
  "phylogenle_history_normal": {
    "2026-10-26": { "solved": true, "guessCount": 4, "guesses": [...], "hints": [...] }
  },
  "phylogenle_history_hard": {
    "2026-10-26": { "solved": false, "guessCount": 12, "guesses": [...], "hints": [...] }
  },
  "lastSynced": 1792864800000
}
```

### C. Migration & Backward Compatibility
- Existing stats from `phylogenle_stats` and `phylogenle_history` will be automatically migrated to `phylogenle_stats_hard` and `phylogenle_history_hard` on first boot (since existing daily games used the 29,748 master pool).
- New players start fresh on Normal Mode stats.

---

## 7. Daily Puzzle PRNG & Calendar Archive

### A. Independent Daily Sequences (`prng.js`)
The PRNG hash algorithm will incorporate difficulty salts:
```javascript
// Normal daily target (picked from normalSpeciesList)
const normalTarget = getDailyTargetSpecies(normalSpeciesList, dateStr, 'normal');

// Hard daily target (picked from hardSpeciesList)
const hardTarget = getDailyTargetSpecies(hardSpeciesList, dateStr, 'hard');
```
This guarantees that each day has a distinct Normal Daily Organism (e.g. *Jaguar*) and a Hard Daily Organism (e.g. *Etheostoma luteovinctum*).

### B. Calendar Archive Modal
- The archive modal (`#archive-modal`) will reflect the active difficulty tier:
  - If viewing in Normal Mode: Shows calendar days and list view for Normal daily puzzles.
  - If viewing in Hard Mode: Shows calendar days and list view for Hard daily puzzles.
  - Includes a quick toggle inside the archive header so players can inspect past puzzles from either difficulty.

---

## 8. Copy-Paste Share Strings for Normal vs. Hard

Our newly implemented lightbulb (`💡`) hints and surrender flag (`⬜`) will distinguish between tiers in the share string:

### Normal Mode Victory:
```
Phylogenle #1026 🧬
Solved in 4 guesses (1 hint)!
⬛🟫💡🟦🟩
https://amitjoshi2724.github.io/phylogenle/
```

### Hard Mode Victory:
```
Phylogenle #1026 [Hard] 🧬
Solved in 7 guesses (2 hints)!
⬛⬛🟫💡🟦🟪💡🟩
https://amitjoshi2724.github.io/phylogenle/
```

---

## 9. Phased Implementation Roadmap

| Phase | Component | Key Deliverables | Risk Level |
| :---: | :--- | :--- | :---: |
| **Phase 1** | **Dataset Generation** | Write `build_normal_dataset.py`, merge 344 original species + curated animal candidates (~850 total), prune `phylogeny_tree.json`, generate `data/normal/` files. | Low |
| **Phase 2** | **Taxonomic Catalog** | Run `build_taxonomic_catalog.py` to create `data/normal/species_taxonomy_catalog.json` and markdown directory. | Low |
| **Phase 3** | **Storage & Database Partitioning** | Update [`storage.js`](file:///Users/amitjoshi2724/Desktop/phylogenle/storage.js) to support `_normal` and `_hard` stats, streaks, history, and Firestore cloud sync. | Medium |
| **Phase 4** | **UI & Controls Integration** | Add segmented difficulty pill `[ 🟢 Normal | 🔴 Hard ]` to navigation bar in [`index.html`](file:///Users/amitjoshi2724/Desktop/phylogenle/index.html) and [`style.css`](file:///Users/amitjoshi2724/Desktop/phylogenle/style.css); wire dual toggle state in [`script.js`](file:///Users/amitjoshi2724/Desktop/phylogenle/script.js). | Low |
| **Phase 5** | **Autocomplete & Archive Sync** | Scope autocomplete to active difficulty; update Archive modal to support Normal vs Hard past puzzles; verify in browser. | Low |

---

## 10. Decisions for User Approval

1. **Species Pool Size:** Does **~850 to 1,000 animals** (providing 2.5+ years of daily puzzles without repetition) match your vision for the Normal Mode set?
2. **Kingdom Scope:** Do you agree that Normal Mode should be strictly **Kingdom *Animalia*** (no plants, fungi, or bacteria), keeping non-animal kingdoms in Hard Mode?
3. **Toggle Layout:** Do you approve of two adjacent segmented pills in the navigation bar:  
   `[ 🟢 Normal | 🔴 Hard ]` &nbsp;&nbsp; `[ 📅 Daily | 🧬 Practice ]`?
