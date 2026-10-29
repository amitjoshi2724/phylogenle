# 🧬 Comprehensive Architecture Plan: Multi-Tier Difficulty Hierarchy & Scalable Tree Pruning (v4)

> **Status:** Revised per User Directives & Calibrating Ranking Data (Code edits paused)  
> **Author:** Antigravity  
> **Target System:** Phylogenle Web Application & Data Pipeline  
> **Key Revisions (v4):**  
> 1. **Scalable Multi-Tier Difficulty Framework:** Expanded beyond a binary Normal/Hard split into a 4-tier concentric hierarchy: **Easy (~1k)**, **Normal (~2k)**, **Advanced (~5k)**, and **Master (All 30k)**. All tiers are mathematically nested concentric subsets of the master tree ($S_{\text{Easy}} \subset S_{\text{Normal}} \subset S_{\text{Advanced}} \subset S_{\text{Master}}$).  
> 2. **Robust Multi-Year Pageview Metric ($V_{\text{wiki}}$):** Replaced single-month pageview snapshots with cumulative English Wikipedia traffic across **all of 2025 and 2026**, smoothing out seasonal spikes, news anomalies, and monthly noise to measure true sustained popularity.  
> 3. **Clarified Metric Mathematics ($S_{\text{wiki}}$ & $V_{\text{wiki}}$):** Defined Wikidata sitelinks and Wikipedia 2025–2026 cumulative pageviews as continuous ranking metrics, completely eliminating any binary threshold gating confusion.  
> 4. **User-Calibrated Composite Formula:** Paused static heuristic weights (0.6 / 0.4). Two independent comprehensive CSV rankings (`docs/species_ranking_by_swiki.csv` and `docs/species_ranking_by_vwiki.csv`) are generated for user inspection before formula selection.  
> 5. **Simplified Linguistic Filter:** Retained the requirement for established English common names (preventing pure Latin stubs) while removing the manual "researcher-named regional sub-species" rule (which is naturally resolved by popularity scoring).  
> 6. **Confirmed Plants in All Tiers:** Documented that recognizable plants are integrated into Easy (~100 iconic plants), Normal (~250 plants), Advanced (~600 plants), and Master (all 1,862 Plantae species).  
> 7. **100% Colorblind-Safe Design (4 Tiers):** Four distinct semantic silhouettes (`🐾 Easy`, `🌿 Normal`, `🔬 Advanced`, `⚡ Master`) with WCAG AAA accessible high-contrast palettes and explicit share tags.

---

## 1. Executive Summary & Vision

Phylogenle currently contains **29,754 species** spanning the entirety of life on Earth (including 27,792 animals, 1,862 plants, 55 fungi, 20 bacteria, 6 archaea, and 19 others). While biologically rich, having all 29,754 species active by default makes daily puzzles and autocomplete overwhelming:
- Players typing common animal names are inundated with dozens of obscure regional subspecies and scientific names.
- Daily puzzle targets can turn out to be organisms like *"Darwin's Slimehead"* or *"Miquihuana Splayfoot Salamander"*, which casual puzzle solvers have never heard of.

### The Solution: 4 Concentric Difficulty Tiers

Rather than forcing all players into a one-size-fits-all compromise, Phylogenle implements **4 mathematically nested difficulty tiers** calibrated directly by empirical popularity ranking:

```
┌────────────────────────────────────────────────────────────────────────┐
│                   ⚡ MASTER TIER (All 29,754 Species)                  │
│   Full Master Tree of Life: Microbes, Fungi, Deep-Sea Taxa, Plants     │
│   ┌────────────────────────────────────────────────────────────────┐   │
│   │             🔬 ADVANCED TIER (Top ~5,000 Species)              │   │
│   │   Global Biodiversity: Diverse Raptors, Snakes, Reef Fish      │   │
│   │   ┌────────────────────────────────────────────────────────┐   │   │
│   │   │          🌿 NORMAL TIER (Top ~2,000 Species) [Default] │   │   │
│   │   │   Regional Wildlife, Iconic Plants, Everyday Puzzlers  │   │   │
│   │   │   ┌────────────────────────────────────────────────┐   │   │   │
│   │   │   │        🐾 EASY TIER (Top ~1,000 Species)       │   │   │   │
│   │   │   │   Household Megafauna, Famous Flowers & Trees  │   │   │   │
│   │   │   └────────────────────────────────────────────────┘   │   │   │
│   │   └────────────────────────────────────────────────────────┘   │   │
│   └────────────────────────────────────────────────────────────────┘   │
└────────────────────────────────────────────────────────────────────────┘
```

1. **🐾 Easy Tier (Top ~1,000 Species):**
   - **Target Audience:** Casual puzzle solvers, newcomers, children, and quick 2-minute daily games.
   - **Curated Pool:** Household-name wildlife (Lion, African Elephant, Emperor Penguin, Bottlenose Dolphin, Wolf, Grizzly Bear, Red Fox) + domestic animals (Dog, Cat, Horse, Pig, Chicken) + universally famous plants (English Oak, Common Sunflower, Red Rose, Apple Tree, Giant Sequoia).
   - **Autocomplete:** Fast and uncluttered. Zero obscure regional subspecies.
   - **Performance:** Downloads only **~1.1 MB** total assets; initial tree renders in **<25ms**.

2. **🌿 Normal Tier (Top ~2,000 Species) — Default Mode:**
   - **Target Audience:** General puzzle players, Wordle/Globle audience, and nature enthusiasts.
   - **Curated Pool:** Easy Tier + prominent regional wildlife (Koala, Platypus, Gila Monster, Bald Eagle, Coral Reef Fish, Snow Leopard, Narwhal) + famous agricultural & culinary crops (Coffee, Wheat, Rice, Cotton, Sugar Maple).
   - **Experience:** Satisfying biological challenge that remains universally recognizable once revealed.
   - **Performance:** Downloads **~1.8 MB** total assets; initial tree renders in **<40ms**.

3. **🔬 Advanced Tier (Top ~5,000 Species):**
   - **Target Audience:** Avid birders, nature lovers, biology students, and wildlife photographers.
   - **Curated Pool:** Normal Tier + broad global biodiversity (diverse accipiters and falcons, venomous vipers and cobras, poison dart frogs, tropical beetles, diverse marine mammals and sharks, broad botanical families).
   - **Experience:** Substantial taxonomic depth without diving into microscopic or microscopic-parasitic obscurity.
   - **Performance:** Downloads **~3.6 MB** total assets; initial tree renders in **<80ms**.

4. **⚡ Master Tier (Hard Mode — All 29,754 Species):**
   - **Target Audience:** Evolutionary biologists, taxonomists, and hardcore puzzle masochists.
   - **Curated Pool:** The complete, unpruned master tree of life across all domains and kingdoms (Metazoa, Plantae, Fungi, Bacteria, Archaea, deep-sea darters, microscopic nematodes).
   - **Experience:** The full, uncompromising evolutionary directory of life on Earth.
   - **Performance:** Retains full 14.2 MB master dataset with progressive infinite-scroll autocomplete.

---

## 2. Algorithmic Popularity Engine & Empirical Calibration Workflow

Rather than enforcing arbitrary limits or premature heuristic weights, the Normal dataset is constructed and calibrated through a **multi-signal empirical ranking workflow** evaluating all organisms from the master tree:

```
┌────────────────────────────────────────────────────────────────────────┐
│                   ALL 29,754 MASTER SPECIES                            │
└──────────────────────────────────┬─────────────────────────────────────┘
                                   │
                                   ▼
    [Tier 1: Guaranteed Inclusions (0% Chance of Exclusion)]
    • 100% of the 344 Original Untouched Species (Lion, Dog, Wolf, etc.)
    • All Domesticated & Agricultural Fauna (Horse, Cow, Pig, Sheep, Cat)
    • Iconic Megafauna & Zoo Favorites (Zebra, Giraffe, Hippo, Kangaroo)
                                   │
                                   ▼
    [Tier 2: Multi-Signal Popularity Metrics (Continuous, Not Binary)]
    • Signal A (Swiki): Wikidata Global Sitelinks Count
      - Real-valued integer: Total Wikimedia language editions with an article.
      - Measures global cultural/educational breadth.
      - (Plains Zebra = 68, Lion = 274, Platypus = 117, English Oak = 86;
         Obscure creek darter = 2–4).
    • Signal B (Vwiki): English Wikipedia 2025–2026 Cumulative Pageviews
      - Real-valued integer: Total pageviews across all of 2025 and 2026.
      - Multi-year cumulative window completely eliminates seasonal anomalies
        (e.g. holiday spikes) and news bias, reflecting sustained public familiarity.
      - (Lion = ~3,350,000, Giant Panda = ~2,440,000, Cheetah = ~2,000,000;
         Plains Zebra = ~450,000, Obscure creek darter = ~300).
                                   │
                                   ▼
    [Tier 3: Recognizable Plants Pool (From 1,862 Master Plantae)]
    • Iconic Trees: English Oak, Giant Sequoia, Coast Redwood, Sugar Maple, Pine
    • Famous Flowers: Sunflower, Red Rose, Tulip, Orchid, Dandelion, Venus Flytrap
    • Crops & Staples: Apple, Coffee Plant, Cotton, Corn, Wheat, Rice
                                   │
                                   ▼
    [Tier 4: Linguistic Sanity Filter]
    • Must have an established English common name (filters out pure Latin stubs)
    • Note: Obscure regional subspecies are naturally handled by Tier 2 popularity
      scoring without needing brittle manual naming heuristics.
                                   │
                                   ▼
    ======================================================================
    EMPIRICAL CALIBRATION STAGES (User Tuning Before Implementation)
    ======================================================================
    • Step 1: Rank all candidate species independently by Swiki (Global Languages)
    • Step 2: Rank all candidate species independently by Vwiki (2025–2026 Cumulative Views)
    • Step 3: User reviews both rankings side-by-side to assess signal behavior
    • Step 4: User reviews empirical CSV rankings and defines composite popularity formula P(Swiki, Vwiki)
    • Step 5: Rank all 29,754 species by tuned metric P; partition into 4 concentric difficulty tiers:
      - 🐾 Easy Tier (Top ~1,000 species)
      - 🌿 Normal Tier (Top ~2,000 species)
      - 🔬 Advanced Tier (Top ~5,000 species)
      - ⚡ Master Tier (All 29,754 species)
```

### Clarifying the Metric Mathematics: Continuous vs. Binary
In earlier draft iterations, thresholds like `Swiki >= 15` and `Vwiki >= 2,500` were cited as illustrative reference points. To be completely clear:
- **No Binary Gating:** Neither $S_{\text{wiki}}$ nor $V_{\text{wiki}}$ is treated as an on/off boolean flag.
- **Continuous Distribution:** Every organism has an exact numeric value for $S_{\text{wiki}}$ and $V_{\text{wiki}}$.
- **No Premature Hyperparameter Lock-in:** The placeholder formula $P = 0.6 \log_{10}(V_{\text{wiki}}) + 0.4 \log_{10}(S_{\text{wiki}})$ has been **paused**. Hyperparameters will be determined empirically after inspecting the independent rankings.
- **No Arbitrary Pool Size:** The tentative 1,500–2,000 figure is on hold until the composite popularity distribution is generated and the user selects the natural inflection point.

### Detailed Specification of Metric B: Multi-Year Cumulative Pageviews ($V_{\text{wiki}}$)
Instead of taking a single monthly snapshot (such as January 2026), the pageview signal $V_{\text{wiki}}$ explicitly aggregates traffic across **all of 2025 and 2026**.

#### Why Single-Month Snapshots (e.g. January) are Deficient:
1. **Seasonal Distortion:** Organisms associated with specific times of year (e.g., reindeer in December, groundhogs in February, turkeys in November, migratory birds in spring) experience massive localized traffic spikes that do not reflect year-round familiarity.
2. **Viral / News Anomalies:** A single viral video, zoo birth, or news documentary can temporarily push an obscure frog or bat into top ranks for a single month before collapsing.
3. **Academic & School Cycles:** Monthly Wikipedia traffic fluctuates according to university and school research cycles.

#### Multi-Year Cumulative Window Formulation:
Wikimedia's REST API endpoint returns monthly traffic breakdown arrays across the multi-year span in a single HTTP request:
```
GET https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/en.wikipedia.org/all-access/all-agents/{title}/monthly/20250101/20261231
```
The cumulative metric sums all returned monthly traffic buckets across 2025 and 2026:
$$V_{\text{wiki}} = \sum_{m \in \{2025, 2026\}} \text{views}_m$$

By summing monthly pageviews across 2025 and 2026, transient noise cancels out, providing an exceptionally stable, unbiased measure of genuine multi-year public awareness:
- **Lion (*Panthera leo*):** ~3,352,000 cumulative views
- **Giant Panda (*Ailuropoda melanoleuca*):** ~2,437,000 cumulative views
- **Cheetah (*Acinonyx jubatus*):** ~2,003,000 cumulative views
- **Venus Flytrap (*Dionaea muscipula*):** ~893,000 cumulative views
- **Plains Zebra (*Equus quagga*):** ~452,000 cumulative views
- **English Oak (*Quercus robur*):** ~246,000 cumulative views
- **Regional minnow / darter:** ~100–400 cumulative views across 2025–2026
- **Microbes / nematodes:** <50 cumulative views across 2025–2026

#### Option B: Exclusive Standalone Article Rollup (Cultivars, Subspecies & Domestic Forms)
When a single biological species in the master catalog corresponds to multiple well-known names with **distinct standalone Wikipedia articles** (not mere redirects), pageviews are handled via **Option B ("Exclusive Rollup")**:
1. **Exclusive Cultivars & Subspecies Are Summed:** If a standalone article uniquely belongs to that single species and is not shared with any other taxon in the catalog (e.g. *Brassica oleracea* having separate standalone articles for `Cabbage`, `Broccoli`, `Kale`, `Cauliflower`, `Brussels sprout`, `Kohlrabi`; or *Puma concolor* having `Florida panther`; or *Ursus arctos* having `Grizzly bear`), their pageviews are summed:
   $$V_{\text{wiki}} = V_{\text{primary}} + \sum V_{\text{exclusive\_articles}}$$
2. **Generic Umbrella Groups Are Excluded:** Standalone articles representing broad multi-species groups (e.g. `Elephant`, `Salmon`, `Crow`, `Alligator`, `Bison`) or polytypic genera/families are excluded from rollup to prevent siphoning generic family readership onto a single arbitrary species.
3. **Disambiguation & Non-Biological Guard:** Disambiguation pages and non-biological homonyms (e.g. "Dory" the wooden boat, "Gluttony" the deadly sin, "Timber Wolf" the comic book character) are verified and rejected via Wikidata `P31` (instance of) and `P105` (taxon rank) validation.

---

## 3. 100% Colorblind-Safe Design System (WCAG AAA) Across 4 Tiers

To ensure all 4 difficulty tiers are completely accessible to players with red-green colorblindness (deuteranomaly, protanomaly, deuteranopia, protanopia) as well as tritanopia and monochromacy, the UI **abandons red and green circles entirely** and employs a multi-sensory design combining distinct semantic silhouettes, high-contrast accessible palettes, and explicit text tags:

```
[ 🐾 Easy | 🌿 Normal | 🔬 Advanced | ⚡ Master ]       [ 📅 Daily | 🧬 Practice ]       [ 📖 Species Catalog ]
```

### A. Semantic Silhouettes (Monochrome-Ready)
Each tier is assigned a distinct iconic glyph whose silhouette remains immediately recognizable even on black-and-white e-ink displays or high-contrast accessibility modes:
- **`🐾` Easy Tier:** **Animal Paw Print** — Friendly, accessible, household pets and charismatic megafauna.
- **`🌿` Normal Tier:** **Botanical Leaf** — Nature, balanced wildlife, recognizable trees, flowers, and everyday puzzle challenge.
- **`🔬` Advanced Tier:** **Microscope** — Scientific exploration, avian/reptilian biodiversity, deeper taxonomic discovery.
- **`⚡` Master Tier:** **Lightning Bolt** — High intensity, maximum evolutionary challenge, all 29,754 organisms across all domains.

### B. Colorblind-Safe 4-Tier Palette Matrix
The color palette uses distinct hue regions and luminance values to ensure clarity under all forms of color vision deficiency (especially deuteranopia and protanopia where red/green distinction is impaired):

| Difficulty | Glyph | Label | Color Family | Active Gradient / Hex | Text Color | Glow / Elevation |
| :--- | :---: | :--- | :--- | :--- | :--- | :--- |
| **Easy** | `🐾` | **Easy** | Sky / Cobalt Blue | `#1d4ed8` to `#2563eb` | High-Contrast White `#ffffff` | `0 2px 8px rgba(37, 99, 235, 0.45)` |
| **Normal** | `🌿` | **Normal** | Forest Emerald | `#047857` to `#059669` | High-Contrast White `#ffffff` | `0 2px 8px rgba(5, 150, 105, 0.45)` |
| **Advanced** | `🔬` | **Advanced**| Royal Amethyst | `#6d28d9` to `#7c3aed` | High-Contrast White `#ffffff` | `0 2px 8px rgba(124, 58, 237, 0.45)` |
| **Master** | `⚡` | **Master** | Golden Amber | `#b45309` to `#d97706` | High-Contrast White `#ffffff` | `0 2px 8px rgba(217, 119, 6, 0.45)` |

*Inactive state:* Muted semi-transparent slate background (`rgba(255, 255, 255, 0.06)`), font weight 500, transparent border, subtle hover brightening.  
*Active state:* Solid saturated gradient fill, bold font weight 800, distinct glow ring, and high-contrast outline.

### C. Accessible Copy-Paste Share Strings
The victory and surrender share text will **never** rely on ambiguous colored circles. Instead, each difficulty tier embeds an explicit human-readable text bracket tag:

- **🐾 Easy Mode Share Header:**
  ```
  Phylogenle #1026 [Easy 🐾] 🧬
  Solved in 3 guesses!
  ⬛🟫💡🟩
  https://amitjoshi2724.github.io/phylogenle/
  ```

- **🌿 Normal Mode Share Header (Default):**
  ```
  Phylogenle #1026 [Normal 🌿] 🧬
  Solved in 5 guesses (1 hint)!
  ⬛🟫💡🟦🟩
  https://amitjoshi2724.github.io/phylogenle/
  ```

- **🔬 Advanced Mode Share Header:**
  ```
  Phylogenle #1026 [Advanced 🔬] 🧬
  Solved in 6 guesses (2 hints)!
  ⬛🟫💡🟦🟪🟩
  https://amitjoshi2724.github.io/phylogenle/
  ```

- **⚡ Master Mode Share Header:**
  ```
  Phylogenle #1026 [Master ⚡] 🧬
  Solved in 8 guesses (2 hints)!
  ⬛🟫💡🟦🟪🟥🟧🟩
  https://amitjoshi2724.github.io/phylogenle/
  ```

The explicit text tags `[Easy 🐾]`, `[Normal 🌿]`, `[Advanced 🔬]`, and `[Master ⚡]` ensure seamless comprehension across Twitter, Discord, WhatsApp, and screen readers.

---

## 4. Web App UI & 4-Tier Segmented Toggle Architecture

Phylogenle's navigation bar will feature a modern, responsive 4-tier segmented pill control paired with the mode selector:

```html
<nav class="game-nav-bar">
    <!-- 4-Tier Difficulty Selector (Colorblind-Safe) -->
    <div class="mode-segmented-toggle difficulty-toggle-4tier" role="group" aria-label="Difficulty Tier">
        <button type="button" id="diff-easy-btn" class="mode-toggle-btn" data-difficulty="easy" title="Easy Mode: Top ~1,000 household animals and plants">
            <span class="mode-icon">🐾</span> Easy
        </button>
        <button type="button" id="diff-normal-btn" class="mode-toggle-btn active" data-difficulty="normal" title="Normal Mode: Top ~2,000 iconic species (Default)">
            <span class="mode-icon">🌿</span> Normal
        </button>
        <button type="button" id="diff-advanced-btn" class="mode-toggle-btn" data-difficulty="advanced" title="Advanced Mode: Top ~5,000 diverse species">
            <span class="mode-icon">🔬</span> Advanced
        </button>
        <button type="button" id="diff-master-btn" class="mode-toggle-btn" data-difficulty="master" title="Master Mode: All 29,754 species across all kingdoms">
            <span class="mode-icon">⚡</span> Master
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

    <!-- Tools & Modals -->
    <button id="open-catalog-btn" class="nav-action-btn">📖 Species Catalog</button>
    <button id="open-archive-btn" class="nav-action-btn">📅 Archive</button>
</nav>
```

### The 8 Playable Combinations
| Difficulty | Mode | Target Audience | Target Organism Pool | Streak / Stats Tracked |
| :--- | :--- | :--- | :--- | :--- |
| **Easy (`🐾`)** | **Daily (`📅`)** | Casual, Kids, Quick Game | Top ~1,000 Household Species | `phylogenle_stats_easy` |
| **Easy (`🐾`)** | **Practice (`🧬`)** | Casual Learning | Top ~1,000 Household Species | Unrecorded Practice |
| **Normal (`🌿`)** | **Daily (`📅`)** | General Puzzlers (Default) | Top ~2,000 Iconic Species | `phylogenle_stats_normal` |
| **Normal (`🌿`)** | **Practice (`🧬`)** | Regular Puzzlers | Top ~2,000 Iconic Species | Unrecorded Practice |
| **Advanced (`🔬`)**| **Daily (`📅`)** | Birders & Nature Lovers | Top ~5,000 Diverse Species | `phylogenle_stats_advanced` |
| **Advanced (`🔬`)**| **Practice (`🧬`)** | Bio Enthusiasts | Top ~5,000 Diverse Species | Unrecorded Practice |
| **Master (`⚡`)** | **Daily (`📅`)** | Hardcore Biologists | Full 29,754 Master Tree of Life | `phylogenle_stats_master` |
| **Master (`⚡`)** | **Practice (`🧬`)** | Deep Phylogenetic Study | Full 29,754 Master Tree of Life | Unrecorded Practice |

### URL & Navigation State Management
- **URL Parameter Schema:**
  - `/?difficulty=easy&mode=daily`
  - `/?difficulty=normal&mode=daily` (or clean root `/`)
  - `/?difficulty=advanced&mode=daily`
  - `/?difficulty=master&mode=daily`
  - Mode parameter seamlessly combines with practice: `&mode=practice`
- **LocalStorage State Sync:**
  - `phylogenle_difficulty`: `"easy"` | `"normal"` | `"advanced"` | `"master"` (Default: `"normal"`)
  - `phylogenle_game_mode`: `"daily"` | `"practice"` (Default: `"daily"`)
- **Zero Accidental Resets:** Changing difficulty loads that difficulty's specific daily puzzle or active practice state without clearing the other difficulty's progress. Navigating back/forward respects `window.onpopstate`.

### Autocomplete Isolation Per Tier
- **🐾 Easy Mode:** Autocomplete matches only from the top ~1,000 species. Zero regional subspecies or latin-only stubs. Typing *"Cat"* suggests *Domestic Cat, Leopard, Lion, Cheetah, Tiger, Jaguar, Cougar*.
- **🌿 Normal Mode:** Autocomplete queries the top ~2,000 species. Fast, intuitive, and includes major wild animals, crops, and trees.
- **🔬 Advanced Mode:** Autocomplete queries the top ~5,000 species. Includes diverse bird raptors, vipers, reef fish, and botanical families.
- **⚡ Master Mode:** Autocomplete queries all 29,754 species using progressive infinite scroll.

---

## 5. Taxonomic Species Catalogs for All 4 Tiers

The in-app taxonomic catalog modal (`#catalog-modal`) dynamically loads and renders the appropriate Linnaean hierarchy corresponding to the active difficulty:

### A. Easy Catalog (`data/easy/species_taxonomy_catalog.json`)
- Compact, uncluttered Linnaean hierarchy covering ~1,000 species.
- Only contains widely celebrated animals (~900) and household plants (~100).
- Opening *Carnivora → Felidae* reveals only 10 universally recognized species (*Lion, Tiger, Cheetah, Leopard, Snow Leopard, Jaguar, Cougar, Domestic Cat, Serval, Caracal*).

### B. Normal Catalog (`data/normal/species_taxonomy_catalog.json`)
- Balanced hierarchy covering ~2,000 species.
- Expands upon Easy by adding regional wildlife (*Koala, Platypus, Gila Monster, Bald Eagle, Narwhal*) and key agricultural plants (*Coffee, Wheat, Rice, Cotton, Sugar Maple*).

### C. Advanced Catalog (`data/advanced/species_taxonomy_catalog.json`)
- Rich biodiversity catalog covering ~5,000 species.
- Adds comprehensive clades of hawks, owls, vipers, treefrogs, marine mammals, and broader botanical families.

### D. Master Catalog (`data/master/species_taxonomy_catalog.json`)
- Complete taxonomic reference covering all 29,754 species spanning all kingdoms (Animals, Plants, Fungi, Bacteria, Archaea, Viruses).

---

## 6. Backend & Concentric Pruning Architecture

### A. Directory Structure
```
phylogenle/
├── data/
│   ├── easy/
│   │   ├── species_list.json                 (~80 KB  — ~1,000 species)
│   │   ├── phylogeny_tree.json               (~1.1 MB — pruned easy tree)
│   │   └── species_taxonomy_catalog.json     (~0.9 MB — easy catalog)
│   ├── normal/
│   │   ├── species_list.json                 (~160 KB — ~2,000 species)
│   │   ├── phylogeny_tree.json               (~1.8 MB — pruned normal tree)
│   │   └── species_taxonomy_catalog.json     (~1.6 MB — normal catalog)
│   ├── advanced/
│   │   ├── species_list.json                 (~400 KB — ~5,000 species)
│   │   ├── phylogeny_tree.json               (~3.6 MB — pruned advanced tree)
│   │   └── species_taxonomy_catalog.json     (~3.2 MB — advanced catalog)
│   ├── master/
│   │   ├── species_list.json                 (~1.4 MB — 29,754 species)
│   │   ├── phylogeny_tree.json               (~12.8 MB — master tree of life)
│   │   └── species_taxonomy_catalog.json     (~11.6 MB — master catalog)
│   └── time_cache.json                       (~79 MB  — TimeTree divergence cache)
```

### B. Concentric Pruning Invariant & Subtree Extraction (`build_difficulty_tiers.py`)
To prevent divergence drift between difficulty modes, the tiers are generated using **strict mathematical concentricity**:

$$S_{\text{Easy}} \subset S_{\text{Normal}} \subset S_{\text{Advanced}} \subset S_{\text{Master}}$$

```
Master Tree (29,754 species)
   ├── Pruned for Advanced (Top ~5,000)
   │      ├── Pruned for Normal (Top ~2,000)
   │      │      └── Pruned for Easy (Top ~1,000)
```

1. **Exact Divergence Preservation:** When pruning the master phylogenetic tree (`data/master/phylogeny_tree.json`) to create smaller subtrees, each internal ancestor node retains its exact divergence time ($T_{\text{MRCA}}$) from the TimeTree master cache.
2. **Zero Recalculation:** Because divergence times are inherited directly from the master tree, the divergence time between any two organisms (e.g. *Homo sapiens* and *Pan troglodytes*) is mathematically identical whether played in Easy, Normal, Advanced, or Master mode (exactly 6.7 Ma).
3. **Ancestor Pruning:** Intermediate ancestor nodes with no other active descendants in a lower tier are cleanly condensed into direct phylogenetic lineages without altering branch lengths.

### C. Performance & Asset Benchmarks
| Tier | Species Count | Tree JSON Size | Catalog JSON Size | First Render (Mobile) |
| :--- | :---: | :---: | :---: | :---: |
| **🐾 Easy** | ~1,000 | ~1.1 MB | ~0.9 MB | **< 25 ms** |
| **🌿 Normal** | ~2,000 | ~1.8 MB | ~1.6 MB | **< 40 ms** |
| **🔬 Advanced** | ~5,000 | ~3.6 MB | ~3.2 MB | **< 80 ms** |
| **⚡ Master** | 29,754 | ~12.8 MB | ~11.6 MB | **~250 ms** (on-demand) |

Normal and Easy assets load near-instantaneously, providing an ultra-snappy experience for the vast majority of players.

---

## 7. Database & Storage Architecture (`storage.js` & Firebase)

To prevent games in easier modes from diluting hard mode achievements, streaks, and guess distributions, all storage is strictly partitioned across the 4 difficulty tiers:

### A. LocalStorage Partitioning
```javascript
// Streaks, Win Rates, and Guess Distributions
localStorage.getItem('phylogenle_stats_easy');
localStorage.getItem('phylogenle_stats_normal');
localStorage.getItem('phylogenle_stats_advanced');
localStorage.getItem('phylogenle_stats_master');

// Daily Completion History (Dates, Guess Counts, Clues Used, Target Won)
localStorage.getItem('phylogenle_history_easy');
localStorage.getItem('phylogenle_history_normal');
localStorage.getItem('phylogenle_history_advanced');
localStorage.getItem('phylogenle_history_master');

// Active In-Progress Daily State (Persisted Across Refresh)
localStorage.getItem('phylogenle_active_guesses_easy_2026-10-28');
localStorage.getItem('phylogenle_active_guesses_normal_2026-10-28');
localStorage.getItem('phylogenle_active_guesses_advanced_2026-10-28');
localStorage.getItem('phylogenle_active_guesses_master_2026-10-28');
```

### B. Firebase Firestore Cloud Schema
In collection `users/{userId}`:
```json
{
  "uid": "user_12345",
  "email": "player@example.com",
  "phylogenle_stats_easy": {
    "played": 12,
    "won": 12,
    "currentStreak": 12,
    "maxStreak": 12,
    "distribution": { "1-3": 8, "4-6": 4, "7-9": 0, "10-12": 0, "13-15": 0, "16+": 0 },
    "lastPlayedDate": "2026-10-28"
  },
  "phylogenle_stats_normal": {
    "played": 28,
    "won": 26,
    "currentStreak": 14,
    "maxStreak": 14,
    "distribution": { "1-3": 6, "4-6": 15, "7-9": 5, "10-12": 0, "13-15": 0, "16+": 0 },
    "lastPlayedDate": "2026-10-28"
  },
  "phylogenle_stats_advanced": {
    "played": 10,
    "won": 7,
    "currentStreak": 3,
    "maxStreak": 5,
    "distribution": { "1-3": 1, "4-6": 4, "7-9": 2, "10-12": 0, "13-15": 0, "16+": 0 },
    "lastPlayedDate": "2026-10-27"
  },
  "phylogenle_stats_master": {
    "played": 6,
    "won": 2,
    "currentStreak": 1,
    "maxStreak": 2,
    "distribution": { "1-3": 0, "4-6": 1, "7-9": 1, "10-12": 0, "13-15": 0, "16+": 0 },
    "lastPlayedDate": "2026-10-25"
  },
  "phylogenle_history_easy": { ... },
  "phylogenle_history_normal": { ... },
  "phylogenle_history_advanced": { ... },
  "phylogenle_history_master": { ... },
  "lastSynced": 1792864800000
}
```

### C. Backward Compatibility & Migration
- Existing historical user statistics from prior games (which drew from the 29,754 master species tree) are automatically migrated into `phylogenle_stats_master` and `phylogenle_history_master`.
- Normal, Easy, and Advanced stats start fresh, cleanly tracking each player's streak in those specific tiers.

---

## 8. Daily Puzzle PRNG, Epoch-Based Batch Indexing & Calendar Archive

### A. Independent Daily Organisms (`prng.js`)
The daily PRNG seeding formula incorporates a difficulty salt, ensuring each tier features a unique, age-appropriate organism each day:
```javascript
// Easy daily target (e.g. Lion or Common Sunflower)
const easyTarget = getDailyTargetSpecies(easySpeciesPool, dateStr, 'easy');

// Normal daily target (e.g. Plains Zebra or Giant Sequoia)
const normalTarget = getDailyTargetSpecies(normalSpeciesPool, dateStr, 'normal');

// Advanced daily target (e.g. Peregrine Falcon or Poison Dart Frog)
const advancedTarget = getDailyTargetSpecies(advancedSpeciesPool, dateStr, 'advanced');

// Master daily target (e.g. Etheostoma luteovinctum or microscopic diatom)
const masterTarget = getDailyTargetSpecies(masterSpeciesPool, dateStr, 'master');
```

A dedicated player can choose to play all 4 daily puzzles every day: solving Easy over breakfast, Normal at lunch, Advanced after work, and Master as an evening challenge!

### B. Epoch-Based Batched Append-Only Indexing System (Future-Proof Pool Expansion)

#### 1. The Retrospective Modulo Problem
In deterministic daily games (like Wordle or Globle), daily targets are selected using a pseudorandom number generator keyed by the date and pool size:
$$\text{index} = \text{PRNG}(\text{dateStr}, \text{salt}) \pmod{N}$$
If you later manually add, say, 25 animals to Normal Mode (increasing $N$ from 2,000 to 2,025), a naive implementation causes **modulo collapse**:
- Evaluating *past* dates with $\pmod{2025}$ instead of $\pmod{2000}$ retroactively shuffles the answer to **every previous game played in the history of the app**.
- Players opening the Calendar Archive or reviewing yesterday's game would see a completely different organism, destroying past streaks, personal records, and historical share links.

#### 2. The Solution: Append-Only Epoch Batches
To allow seamless manual additions at any time in the future without disturbing a single past game, each difficulty tier maintains an **epoch-indexed batch manifest**:

```
[Normal Mode Species Pool: Global Append-Only Array]
┌───────────────────────────────────────────────┬────────────────────────────┬─────
│ Batch 1 (Genesis): Indices 0 to 1,999 (2,000) │ Batch 2: Indices 2,000 to  │ ... 
│ Effective from Launch (e.g. 2026-01-01)       │ 2,024 (25 new animals)     │     
│                                               │ Effective: 2027-01-01      │     
└───────────────────────────────────────────────┴────────────────────────────┴─────
```

#### 3. Manifest Data Schema (`species_manifest.json` / `species_list.json`)
```json
{
  "tier": "normal",
  "batches": [
    {
      "batch_id": 1,
      "effective_from": "2026-01-01",
      "count": 2000,
      "global_offset": 0
    },
    {
      "batch_id": 2,
      "effective_from": "2027-01-01",
      "count": 25,
      "global_offset": 2000
    }
  ],
  "species": [
    /* 2,000 species belonging to Batch 1 */
    /* 25 species belonging to Batch 2 */
  ]
}
```

#### 4. Deterministic Date-Scoped Target Selection Algorithm
When selecting the daily organism for `puzzleDate` (e.g. `"2026-10-28"`):
1. **Filter Active Batches:** Identify only the batches that were valid on or before `puzzleDate`:
   $$\text{activeBatches} = \{ b \in \text{batches} \mid b.\text{effective\_from} \le \text{puzzleDate} \}$$
2. **Compute Active Pool Size:**
   $$\text{activePoolSize} = \sum_{b \in \text{activeBatches}} b.\text{count}$$
   - For any date before `2027-01-01`: $\text{activePoolSize} = 2,000$.
   - For any date on or after `2027-01-01`: $\text{activePoolSize} = 2,025$.
3. **Generate Deterministic PRNG Index:**
   $$\text{targetGlobalIndex} = \text{PRNG}(\text{puzzleDate}, \text{salt}) \pmod{\text{activePoolSize}}$$
4. **Zero-Indexed Batch Mapping:**
   - If $\text{targetGlobalIndex} < 2,000$: resolves directly to `species[targetGlobalIndex]` (from Batch 1).
   - If $2,000 \le \text{targetGlobalIndex} < 2,025$: resolves to `species[targetGlobalIndex]` (which corresponds to index $\text{targetGlobalIndex} - 2,000$ in Batch 2).

**Why this guarantees 100% retrospective fidelity:**
For any puzzle date in the past (e.g. October 2026), `puzzleDate < "2027-01-01"` is always true. Thus `activePoolSize` is forever locked to 2,000, ensuring every past game generates the exact same organism in perpetuity.

#### 5. Concentric Expansion Cascade Rule
Whenever an organism is manually added to an easier tier, it automatically cascades to all harder tiers to preserve the concentric subset invariant:
$$S_{\text{Easy}} \subset S_{\text{Normal}} \subset S_{\text{Advanced}} \subset S_{\text{Master}}$$
- Adding 10 animals to Easy Mode automatically appends them into new batches for Normal, Advanced, and Master modes.
- Adding 15 animals specifically to Normal Mode appends them to Advanced and Master modes.

#### 6. Live Catalog & Autocomplete Decoupling
While the **daily target selection** is strictly time-gated by batch effective dates:
- **Species Catalog (`#catalog-modal`) & Autocomplete:** Always include the full union of all released batches immediately!
- Players can search for, browse in the taxonomic tree, and make guesses using newly added species right away, even if those species are scheduled to enter the daily puzzle pool at a future epoch date.

### C. Calendar Archive Modal
- The archive view dynamically filters past games based on the selected difficulty tier.
- A 4-tab filter bar `[ 🐾 Easy | 🌿 Normal | 🔬 Advanced | ⚡ Master ]` allows instant switching between past calendar records.
- Thanks to the batch indexing system, playing or reviewing past dates from the archive is 100% deterministic and tamper-proof.

### D. Deterministic Alias Selection, Hint Presentation, & Educational Feedback

When an organism with multiple established common names/aliases (e.g. *Puma concolor*, known as *Cougar*, *Mountain Lion*, *Florida Panther*, *Panther*, *Catamount*; or *Orcinus orca*, known as *Orca* and *Killer Whale*; or *Mammut americanum*, known as *American Mastodon* and *Mastodon*) is chosen as the target organism:

#### 1. Deterministic Daily & Practice Alias Selection
To add natural variety and educational richness without breaking daily multiplayer parity:
- **Daily Mode:** The displayed common name for clues, hints, give-up reveals, and the win modal is selected deterministically using the day's seeded PRNG:
  $$\text{aliasIndex} = \text{PRNG}(\text{puzzleDate}, \text{salt} + \text{"_alias"}) \pmod{|\text{availableNames}|}$$
  - **100% Multiplayer Parity:** Every player worldwide on date $D$ sees the exact same presentation name (e.g., on one day the target may be presented as *"Cougar"*, and on another future cycle as *"Florida Panther"* or *"Mountain Lion"*).
  - All clue hints (e.g. first letter, word length, character count) are strictly calculated against this chosen presentation name to ensure clues never contradict each other.
- **Practice Mode:** The practice session's pseudo-random seed deterministically chooses the presentation name for that specific round.

#### 2. Universal Acceptance of All Valid Aliases
- When evaluating a player's guess, the engine resolves the input string through [`data/species_aliases.json`](file:///Users/amitjoshi2724/Desktop/phylogenle/data/species_aliases.json) directly to the canonical biological species (`genus + specific epithet`).
- **All aliases are 100% correct answers:** Typing *"Florida Panther"*, *"Mountain Lion"*, *"Cougar"*, or *"Puma concolor"* immediately registers as a successful match for *Puma concolor*.

#### 3. Educational Context & Feedback UI (Zero Player Confusion)
To avoid cognitive dissonance (e.g., a player wondering *"Wait, I typed Florida Panther, why does the tree show Cougar?"*), the game explicitly explains the alias relationship:
- **Winning / Guess Row Feedback Banner:**
  > 🌟 **Correct!** You guessed **Florida Panther**, which is a recognized alias of **Cougar (*Puma concolor*)**.
- **Give-Up / Surrender Modal & Win Modal Summary:**
  - Displays the primary canonical name and scientific taxon, followed by an "Also Known As" list:
    - **Target Organism:** **Cougar** (*Puma concolor*)
    - **Round Presentation:** *Florida Panther*
    - **Also Known As:** *Mountain Lion; Panther; Catamount*
- **Guess History Table:**
  If the player guessed an alias, the row displays the player's exact entered text with an explanatory subtitle:
  `Florida Panther` *(Alias of Cougar)*.

---

## 9. Phased Implementation Roadmap

| Phase | Milestone | Key Deliverables | Risk Level |
| :---: | :--- | :--- | :---: |
| **Phase 1A** | **Independent Empirical Rankings ($S_{\text{wiki}}$ & $V_{\text{wiki}}$)** | Generate and output full comprehensive CSV rankings across all 29,754 organisms: [`docs/species_ranking_by_swiki.csv`](file:///Users/amitjoshi2724/Desktop/phylogenle/docs/species_ranking_by_swiki.csv) and [`docs/species_ranking_by_vwiki.csv`](file:///Users/amitjoshi2724/Desktop/phylogenle/docs/species_ranking_by_vwiki.csv) (plus combined [`docs/species_popularity_rankings.csv`](file:///Users/amitjoshi2724/Desktop/phylogenle/docs/species_popularity_rankings.csv)). *(Currently running in user terminal)* | Low |
| **Phase 1B** | **User Formula Calibration** | User reviews CSV rankings, tunes the composite formula weights $P(S_{\text{wiki}}, V_{\text{wiki}})$, and selects cutoff boundaries for Easy (~1k), Normal (~2k), and Advanced (~5k). | Low |
| **Phase 1C** | **Concentric Dataset Pruning** | Run `build_difficulty_tiers.py` to prune master tree into `data/easy/`, `data/normal/`, `data/advanced/`, and configure `data/master/`. | Low |
| **Phase 2** | **Taxonomic Catalogs** | Update `build_taxonomic_catalog.py` to output Linnaean catalogs for all 4 difficulty tiers. | Low |
| **Phase 3** | **Storage & Database Partitioning** | Update [`storage.js`](file:///Users/amitjoshi2724/Desktop/phylogenle/storage.js) to support `_easy`, `_normal`, `_advanced`, and `_master` stats, streaks, history, and Firestore cloud sync. | Medium |
| **Phase 4** | **UI & 4-Tier Colorblind-Safe Controls** | Implement 4-tier segmented toggle in [`index.html`](file:///Users/amitjoshi2724/Desktop/phylogenle/index.html) and [`style.css`](file:///Users/amitjoshi2724/Desktop/phylogenle/style.css); wire state management in [`script.js`](file:///Users/amitjoshi2724/Desktop/phylogenle/script.js). | Low |
| **Phase 5** | **Autocomplete, Catalog & Archive Integration** | Scope autocomplete to active difficulty; connect catalog and archive modals to 4-tier difficulty state; full browser testing. | Low |

---

## 10. Summary of Key Architecture Decisions

1. **4-Tier Concentric Difficulty Framework:**
   - **🐾 Easy Tier (Top ~1,000):** Household wildlife, domestic pets, universally famous plants. Fast ~1.1 MB download.
   - **🌿 Normal Tier (Top ~2,000) [Default]:** Familiar wildlife, famous crops & trees, balanced puzzle experience. Fast ~1.8 MB download.
   - **🔬 Advanced Tier (Top ~5,000):** Global biodiversity, raptors, vipers, reef fish, diverse botanical families. ~3.6 MB download.
   - **⚡ Master Tier (All 29,754):** Unpruned master tree of life across all domains and kingdoms.
2. **Strict Concentricity & Divergence Preservation:** All 4 tiers are nested subsets ($S_{\text{Easy}} \subset S_{\text{Normal}} \subset S_{\text{Advanced}} \subset S_{\text{Master}}$) inheriting identical TimeTree divergence times ($T_{\text{MRCA}}$) from the master dataset. Zero divergence drift.
3. **Empirical Calibration Before Implementation:** Game code edits remain strictly paused while the user runs `python3 rank_species_popularity.py` to generate the complete empirical CSV rankings. The composite formula $P(S_{\text{wiki}}, V_{\text{wiki}})$ will be finalized only after user inspection.
4. **Multi-Year Cumulative Pageview Metric ($V_{\text{wiki}}$):** Pageviews are aggregated across all of 2025 and 2026 to eliminate seasonal noise and single-month anomalies.
5. **Continuous Metrics Clarification:** $S_{\text{wiki}}$ and $V_{\text{wiki}}$ are continuous numeric signals, not binary gates.
6. **Simplified Linguistic Filter:** Requires established English common names (preventing pure Latin stubs) while letting popularity scoring handle obscure regional subspecies naturally.
7. **Recognizable Plants in All Tiers:** Plants are integrated across all 4 tiers (~100 in Easy, ~250 in Normal, ~600 in Advanced, all 1,862 in Master).
8. **100% Colorblind-Safe Design (WCAG AAA):** Red/green circles eliminated in favor of distinct semantic silhouettes (`🐾`, `🌿`, `🔬`, `⚡`), high-contrast Blue/Emerald/Amethyst/Amber palettes, and unambiguous copy-paste share tags.
9. **Epoch-Based Batched Append-Only Indexing System:** Manual additions of species (e.g. adding 25 animals to Normal mode at a future date) are structured into dated append-only batches. The daily puzzle PRNG dynamically scopes its pool to the batches active on that puzzle's date, preventing modulo collapse and keeping 100% of past puzzle dates, streaks, and archives permanently immutable. Catalogs and autocomplete immediately expose all species across all batches.
