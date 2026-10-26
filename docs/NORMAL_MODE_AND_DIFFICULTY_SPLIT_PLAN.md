# 🧬 Comprehensive Architecture Plan: Normal Mode & Difficulty Tier Split (v2)

> **Status:** Revised per User Feedback & Awaiting Final Approval  
> **Author:** Antigravity  
> **Target System:** Phylogenle Web Application & Data Pipeline  
> **Key Revisions (v2):**  
> 1. Replaced narrow/arbitrary 850–1,000 cap with an **Algorithmic Popularity & Prominence Engine** across all 29,748 species so no iconic animals (e.g. Zebra) are ever left out.  
> 2. Added curated **recognizable plants** (~5–10% of Normal pool) alongside animals.  
> 3. Implemented a **100% Colorblind-Safe Design System** (abandoning red/green circles; adopting distinct semantic glyphs `[ 🐾 Normal | ⚡ Hard ]`, high-contrast Blue vs. Amber styling, and explicit text tags).

---

## 1. Executive Summary & Vision

Phylogenle currently contains **29,748 species** spanning the entirety of life on Earth (including obscure micro-fungi, deep-sea worms, regional creek darters, and microscopic flora). While biologically rich, having all 29,748 species active by default makes daily puzzles and autocomplete overwhelming:
- Players typing common animal names are inundated with dozens of obscure regional subspecies and scientific names.
- Daily puzzle targets can turn out to be organisms like *"Darwin's Slimehead"* or *"Miquihuana Splayfoot Salamander"*, which casual puzzle solvers have never heard of.

### The Solution: Two Fully Partitioned Difficulty Tiers
1. **Normal Mode (Default):**
   - An algorithmically curated, recognizable, and fun pool of **universally familiar organisms** (~1,500–2,000 organisms, mostly animals + iconic plants).
   - Guaranteed to contain **100% of the original 344 untouched species**, all prominent wildlife (Zebra, Platypus, Cheetah, Giraffe, etc.), and iconic plants (Oak Tree, Sunflower, Giant Redwood, Apple Tree).
   - Separate Normal Daily Puzzle and Normal Practice Mode.
   - Dedicated Normal Mode Taxonomic Catalog.
   - Ultra-fast initial load time (<50ms, ~1.4 MB total data vs. 25 MB).
2. **Hard Mode (Expert Tier):**
   - Retains the entire **29,748-species master tree of life** (all kingdoms, deep-sea taxa, microbes, plants, fossils).
   - Separate Hard Daily Puzzle and Hard Practice Mode.
   - Retains the full 29,748 Taxonomic Catalog.

---

## 2. Algorithmic Popularity Engine: Constructing the Normal Organism Set

Instead of an arbitrary cap (like stopping at 1,000 and accidentally cutting off Zebra or Platypus), the Normal dataset is constructed via an **objective, multi-signal algorithmic pipeline** that evaluates all 29,748 organisms in the master tree:

```
┌────────────────────────────────────────────────────────────────────────┐
│                   ALL 29,748 MASTER SPECIES                            │
└──────────────────────────────────┬─────────────────────────────────────┘
                                   │
                                   ▼
    [Tier 1: Guaranteed Inclusions (0% Chance of Exclusion)]
    • 100% of the 344 Original Untouched Species (Lion, Dog, Wolf, etc.)
    • All Domesticated & Agricultural Fauna (Horse, Cow, Pig, Sheep, Cat)
    • Iconic Megafauna & Zoo Favorites (Zebra, Giraffe, Hippo, Kangaroo)
                                   │
                                   ▼
    [Tier 2: Algorithmic Global Popularity Scoring]
    • Signal A: Wikidata Global Sitelinks Count (Swiki >= 15 languages)
      (Plains Zebra = 68 languages, Lion = 274, English Oak = 86;
       Obscure creek darter = 4 languages)
    • Signal B: Wikipedia Global Monthly Pageviews (Vwiki >= 2,500 views)
    • Composite Popularity Metric: P = 0.6 * log10(Vwiki) + 0.4 * log10(Swiki)
                                   │
                                   ▼
    [Tier 3: Recognizable Plants Quota (~5–10% of Pool)]
    • Iconic Trees: English Oak, Giant Sequoia, Baobab, Sugar Maple, Pine
    • Famous Flowers: Sunflower, Red Rose, Tulip, Orchid, Dandelion, Venus Flytrap
    • Crops & Staples: Apple Tree, Coffee Plant, Cotton, Corn, Wheat, Rice
                                   │
                                   ▼
    [Tier 4: Linguistic Sanity Filter]
    • Must have an established English common name (no pure Latin stubs)
    • Filters out researcher-named regional sub-species (e.g. "Koningsberger's...")
                                   │
                                   ▼
    ======================================================================
    FINAL NORMAL ORGANISM SET (~1,500 to 2,000 Universally Known Organisms)
    ======================================================================
```

### Why This Algorithmic Approach is Superior:
1. **Zero Risk of Missing Iconic Animals:** Species like Zebra, Cheetah, Platypus, Ostrich, Koala, and Kangaroo have massive global traffic and multilingual articles (often in 50–200 languages). They pass the algorithmic threshold with ease.
2. **No Arbitrary Cliff:** Organisms are included based on actual human familiarity, not an artificial integer limit.
3. **Multi-Kingdom Educational Depth:** Including recognizable plants creates fun cross-kingdom puzzles where guessing an animal against a plant yields the ancient **1,600 MYA LECA (Last Eukaryotic Common Ancestor)** divergence.

---

## 3. 100% Colorblind-Safe Design System (WCAG AAA)

To ensure the game is completely accessible to players with red-green colorblindness (deuteranomaly, protanomaly, deuteranopia, protanopia) as well as tritanopia and monochromacy, the UI **abandons red and green circles entirely** and employs a multi-sensory design:

```
[ 🐾 Normal | ⚡ Hard ]       [ 📅 Daily | 🧬 Practice ]       [ 📖 Species Catalog ]
```

### A. Shape & Semantic Silhouette Contrast (Monochrome-Ready)
- **Normal Mode:** Represented by **`🐾` (Animal Paw Print)**.
  - Conveys familiar, charismatic animals and nature.
  - Instant silhouette recognition that does not depend on color perception.
- **Hard Mode:** Represented by **`⚡` (Lightning Bolt)**.
  - Conveys high intensity, deep biological rigor, and master-level challenge.
  - Visually distinct silhouette from the paw print in black and white.

### B. Colorblind-Safe Palette (Royal Blue vs. Warm Amber)
In color vision research, **Blue vs. Yellow/Amber** is the universally recommended accessible pairing because blue and yellow cones function independently of the red-green photopigments:

| Difficulty | Glyph | Label | Active Background | Text Color | Glow / Elevation |
| :--- | :---: | :--- | :--- | :--- | :--- |
| **Normal** | `🐾` | **Normal** | Gradient: Deep Cobalt `#1d4ed8` to Royal Blue `#2563eb` | High-Contrast White `#ffffff` | `0 2px 8px rgba(37, 99, 235, 0.4)` |
| **Hard** | `⚡` | **Hard** | Gradient: Warm Amber `#d97706` to Golden Orange `#f59e0b` | High-Contrast Dark `#1e293b` / White `#ffffff` | `0 2px 8px rgba(245, 158, 11, 0.4)` |

*Inactive state:* Muted slate background (`rgba(255, 255, 255, 0.06)`), 500 font weight, transparent border.  
*Active state:* Solid saturated fill, bold 800 font weight, distinct glow, and high-contrast outline.

### C. Accessible Copy-Paste Share Strings
The victory/surrender share text will **not** rely on colored circles in the header:
- **Normal Mode Share Header:**
  ```
  Phylogenle #1026 🧬
  Solved in 4 guesses (1 hint)!
  ⬛🟫💡🟦🟩
  https://amitjoshi2724.github.io/phylogenle/
  ```
- **Hard Mode Share Header:**
  ```
  Phylogenle #1026 [Hard ⚡] 🧬
  Solved in 6 guesses (2 hints)!
  ⬛🟫💡🟦🟪💡🟩
  https://amitjoshi2724.github.io/phylogenle/
  ```
The explicit text tag `[Hard ⚡]` makes the difficulty unambiguously clear to friends across all chat apps without any color confusion.

---

## 4. Web App UI & Dual-Toggle Architecture

Phylogenle's navigation bar will feature two adjacent, complementary segmented pill controls:

```html
<nav class="game-nav-bar">
    <!-- Difficulty Selector (Colorblind-Safe) -->
    <div class="mode-segmented-toggle difficulty-toggle" role="group" aria-label="Difficulty Tier">
        <button type="button" id="diff-normal-btn" class="mode-toggle-btn active" data-difficulty="normal" title="Normal Mode: ~1,500 iconic animals and plants">
            <span class="mode-icon">🐾</span> Normal
        </button>
        <button type="button" id="diff-hard-btn" class="mode-toggle-btn" data-difficulty="hard" title="Hard Mode: All 30,000 species across all kingdoms">
            <span class="mode-icon">⚡</span> Hard
        </button>
    </div>

    <!-- Mode Selector (Daily vs Practice) -->
    <div class="mode-segmented-toggle mode-toggle" role="group" aria-label="Game Mode">
        <button type="button" id="mode-daily-btn" class="mode-toggle-btn active" data-mode="daily">
            <span class="mode-icon">📅</span> Daily
        </button>
        <button type="button" id="mode-practice-btn" class="mode-toggle-btn" data-mode="practice">
            <span class="mode-icon">🧬</span> Practice
        </button>
    </div>

    <!-- Tools -->
    <button id="open-catalog-btn" class="nav-action-btn">📖 Species Catalog</button>
    <button id="open-archive-btn" class="nav-action-btn">📅 Archive</button>
</nav>
```

### The 4 Playable Combinations
| Difficulty | Mode | Target Audience | Target Organism Pool | Streak / Stats |
| :--- | :--- | :--- | :--- | :--- |
| **Normal (`🐾`)** | **Daily (`📅`)** | Everyone (Default) | ~1,500–2,000 familiar organisms | Normal Daily Streak |
| **Normal (`🐾`)** | **Practice (`🧬`)** | Casual Replay | ~1,500–2,000 familiar organisms | Unrecorded Practice |
| **Hard (`⚡`)** | **Daily (`📅`)** | Biologists & Hardcore | 29,748 Master Tree of Life | Hard Daily Streak |
| **Hard (`⚡`)** | **Practice (`🧬`)** | Deep Exploration | 29,748 Master Tree of Life | Unrecorded Practice |

### Dual URL & LocalStorage Persistence
- **URL Parameters:**
  - `/?difficulty=normal&mode=daily` (or clean default `/`)
  - `/?difficulty=normal&mode=practice`
  - `/?difficulty=hard&mode=daily`
  - `/?difficulty=hard&mode=practice`
- **LocalStorage Keys:**
  - `phylogenle_difficulty`: `"normal"` | `"hard"`
  - `phylogenle_game_mode`: `"daily"` | `"practice"`
- **Zero Accidental Resets:** Refreshing or reopening the tab keeps the player exactly where they left off. Browser Back/Forward navigation is handled via `popstate`.

### Autocomplete Isolation
- **Normal Mode:** Typing queries only the ~1,500–2,000 curated organisms. Typing *"Bear"* shows *Grizzly Bear, Polar Bear, Black Bear, Sun Bear, Sloth Bear, Panda Bear*. No regional micro-subspecies.
- **Hard Mode:** Typing queries all 29,748 species with the progressive infinite-scroll dropdown.

---

## 5. Taxonomic Species Catalog for Normal Mode

The in-app taxonomic catalog modal (`#catalog-modal`) will dynamically switch its data source based on the active difficulty:

### A. Normal Mode Catalog (`data/normal/species_taxonomy_catalog.json`)
- Clean 8-rank Linnaean hierarchy encompassing both animals and plants:
  - **⬛ Domain:** *Eukaryota*
  - **🟫 Kingdoms:**
    - **Animalia:** *Chordata (Mammals, Birds, Reptiles, Amphibians, Fish), Arthropoda (Insects, Spiders, Crabs), Mollusca (Octopuses, Squids), Cnidaria (Jellyfish, Corals)*.
    - **Plantae:** *Streptophyta (Broadleaf Trees, Conifers, Flowering Plants, Crops)*.
  - **🟦 Phylum / 🟪 Class / 🟥 Order / 🟧 Family / 🟨 Genus / 🟩 Species**
- Every clade is clean and uncluttered. Opening *Carnivora → Felidae* reveals ~18 recognizable wild cats instead of 250 obscure entries.

### B. Hard Mode Catalog (`data/hard/species_taxonomy_catalog.json`)
- Retains the full 29,748 species directory spanning all kingdoms (Bacteria, Fungi, Plants, Animals, Archaea, Viruses).

---

## 6. Backend & Data Pipeline Changes

### A. Directory Structure
```
phylogenle/
├── data/
│   ├── normal/
│   │   ├── species_list.json                 (~120 KB — ~1,500 species)
│   │   ├── phylogeny_tree.json               (~1.8 MB — pruned normal tree)
│   │   └── species_taxonomy_catalog.json     (~1.6 MB — normal catalog)
│   ├── hard/
│   │   ├── species_list.json                 (~1.4 MB — 29,748 species)
│   │   ├── phylogeny_tree.json               (~12.8 MB — master tree of life)
│   │   └── species_taxonomy_catalog.json     (~11.6 MB — hard catalog)
│   └── time_cache.json                       (~79 MB — TimeTree calibrated cache)
```

### B. Pruning & Subtree Extraction Script (`build_normal_dataset.py`)
1. Evaluates all 29,748 species against the **Algorithmic Popularity Scoring Engine**.
2. Merges with the 344 original species and curated plant candidates.
3. Prunes the master `data/hard/phylogeny_tree.json` to retain only the ancestor nodes linking Normal species to *Eukaryota / Metazoa / Viridiplantae*.
4. **Zero Time Recalculation:** All internal node divergence times ($T_{\text{MRCA}}$) and Linnaean ranks are inherited directly from the master tree, guaranteeing 100% mathematical consistency.
5. Generates the normal dataset and executes `build_taxonomic_catalog.py` to produce the Normal Mode catalog.

### C. Performance Gains
- **Normal Mode Page Load:** Downloads only **~1.9 MB** total assets instead of **14.2 MB**. Initial tree load finishes in **<50ms** on mobile devices.
- Hard mode data is only fetched asynchronously if the player explicitly selects **⚡ Hard**.

---

## 7. Database & Storage Architecture (`storage.js` & Firebase)

To ensure Normal mode games do not inflate Hard mode streaks (and vice versa), storage is strictly partitioned by difficulty:

### A. LocalStorage Keys & Data Partitioning
```javascript
// Streaks, Win Rates, and Guess Distributions
localStorage.getItem('phylogenle_stats_normal');
localStorage.getItem('phylogenle_stats_hard');

// Daily Completion History (Records, Guesses, Clues Used, Surrenders)
localStorage.getItem('phylogenle_history_normal');
localStorage.getItem('phylogenle_history_hard');

// Active In-Progress Guesses & Hints
localStorage.getItem('phylogenle_active_guesses_normal_2026-10-26');
localStorage.getItem('phylogenle_active_guesses_hard_2026-10-26');
localStorage.getItem('phylogenle_active_hints_normal_2026-10-26');
localStorage.getItem('phylogenle_active_hints_hard_2026-10-26');
```

### B. Firebase Firestore Cloud Schema
In collection `users/{userId}`:
```json
{
  "uid": "user_12345",
  "email": "player@example.com",
  "phylogenle_stats_normal": {
    "played": 22,
    "won": 21,
    "currentStreak": 14,
    "maxStreak": 14,
    "distribution": { "1-3": 6, "4-6": 10, "7-9": 5, "10-12": 0, "13-15": 0, "16+": 0 },
    "lastPlayedDate": "2026-10-26"
  },
  "phylogenle_stats_hard": {
    "played": 6,
    "won": 2,
    "currentStreak": 1,
    "maxStreak": 2,
    "distribution": { "1-3": 0, "4-6": 1, "7-9": 0, "10-12": 1, "13-15": 0, "16+": 0 },
    "lastPlayedDate": "2026-10-25"
  },
  "phylogenle_history_normal": { ... },
  "phylogenle_history_hard": { ... },
  "lastSynced": 1792864800000
}
```

### C. Migration & Backward Compatibility
- Existing user stats and records from recent games are preserved and migrated into `phylogenle_stats_hard` and `phylogenle_history_hard` on first boot (since prior games drew from the 29,748 pool).
- Normal Mode stats begin clean and fresh.

---

## 8. Daily Puzzle PRNG & Calendar Archive

### A. Independent Daily Organisms (`prng.js`)
The daily PRNG seeds incorporate a difficulty salt:
```javascript
// Normal daily target (e.g. Zebra or Giant Sequoia)
const normalTarget = getDailyTargetSpecies(normalSpeciesList, dateStr, 'normal');

// Hard daily target (e.g. Etheostoma luteovinctum)
const hardTarget = getDailyTargetSpecies(hardSpeciesList, dateStr, 'hard');
```

### B. Calendar Archive Modal
- Archive view automatically reflects the active difficulty tier.
- Includes a top toggle: `[ 🐾 Normal Archive | ⚡ Hard Archive ]` allowing players to review or replay past puzzles from either mode.

---

## 9. Phased Implementation Roadmap

| Phase | Milestone | Key Deliverables | Risk Level |
| :---: | :--- | :--- | :---: |
| **Phase 1** | **Dataset & Algorithmic Filter** | Write `build_normal_dataset.py` with Wikimedia popularity evaluation; include 344 original species + iconic plants; prune master tree; output `data/normal/` files. | Low |
| **Phase 2** | **Taxonomic Catalog** | Update `build_taxonomic_catalog.py` to generate `data/normal/species_taxonomy_catalog.json` and markdown directory. | Low |
| **Phase 3** | **Storage & Database Partitioning** | Update [`storage.js`](file:///Users/amitjoshi2724/Desktop/phylogenle/storage.js) to support `_normal` and `_hard` stats, streaks, history, and Firestore cloud sync. | Medium |
| **Phase 4** | **UI & Colorblind-Safe Controls** | Implement `[ 🐾 Normal | ⚡ Hard ]` toggle in [`index.html`](file:///Users/amitjoshi2724/Desktop/phylogenle/index.html) and [`style.css`](file:///Users/amitjoshi2724/Desktop/phylogenle/style.css); wire dual toggle state in [`script.js`](file:///Users/amitjoshi2724/Desktop/phylogenle/script.js). | Low |
| **Phase 5** | **Autocomplete, Catalog & Archive Integration** | Scope autocomplete to active difficulty; connect catalog and archive modals to difficulty state; test in browser. | Low |

---

## 10. Summary of Revisions for User Approval

1. **Algorithmic Popularity Scoring:** No arbitrary cap (e.g. 1,000). Every organism from the 29,748 master tree is evaluated by Wikimedia pageviews and Wikidata global language sitelinks, guaranteeing Zebra, Platypus, and all prominent fauna are included.
2. **Iconic Plants Included:** Enriched with universally recognized trees, flowers, and crops (~5–10% of the normal pool).
3. **100% Colorblind-Safe UI:** Red/green circles removed; replaced with distinct semantic silhouettes `[ 🐾 Normal | ⚡ Hard ]`, Blue vs. Amber styling, and explicit share tags.
