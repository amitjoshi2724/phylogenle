# 🧬 Phylogenle (`phylogenle-amitjoshi2724`)

> **The Daily Evolutionary Biology & Phylogenetic Cladistics Puzzle**  
> *Deduce the mystery organism across hundreds of millions of years of evolutionary divergence.*

Developed by **Amit Joshi** ([@amitjoshi2724](https://github.com/amitjoshi2724))  
🌐 **Live Game:** [https://amitjoshi2724.github.io/phylogenle/](https://amitjoshi2724.github.io/phylogenle/)

---

## 📖 Table of Contents
1. [What is Phylogenle?](#-what-is-phylogenle)
2. [How to Play & Core Mechanics](#-how-to-play--core-mechanics)
3. [The 8-Tier Taxonomic Color & Emoji System](#-the-8-tier-taxonomic-color--emoji-system)
4. [Game Modes: Daily vs. Practice](#-game-modes-daily-vs-practice)
5. [Interactive Gameplay Features](#-interactive-gameplay-features)
   - [Dynamic D3.js Cladogram (Phylogenetic Tree)](#1-dynamic-d3js-cladogram-phylogenetic-tree)
   - [Progressive Taxonomic Hint System](#2-progressive-taxonomic-hint-system)
   - [In-App Universal Species Catalog (29,748 Species)](#3-in-app-universal-species-catalog-29748-species)
   - [Wikipedia Previews & Clade Links](#4-wikipedia-previews--clade-links)
   - [Virtualized Autocomplete Search](#5-virtualized-autocomplete-search)
   - [Statistics, Streaks & Share System](#6-statistics-streaks--share-system)
6. [Dataset & Biodiversity Coverage](#-dataset--biodiversity-coverage)
7. [Scientific Data Sources & Provenance](#-scientific-data-sources--provenance)
8. [Technical Architecture & Performance](#-technical-architecture--performance)
9. [Documentation Directory](#-documentation-directory)
10. [CLI Tools & Expansion](#-cli-tools--expansion)
11. [Local Development](#-local-development)
12. [Credits & License](#-credits--license)

---

## 🌟 What is Phylogenle?

**Phylogenle** is an educational, daily deductive puzzle game that brings real-world evolutionary biology and phylogenetic cladistics into an interactive Wordle-style format. 

Instead of guessing five-letter words or geographical coordinates, players deduce a **mystery organism** chosen from an extensive catalog of **29,748 species spanning all domains of life**—animals (mammals, birds, reptiles, amphibians, fishes, invertebrates), land plants, fungi, bacteria, protists, and viruses.

With each guess, Phylogenle calculates the exact molecular divergence time and the Lowest Common Ancestor (LCA) shared between your guess and the secret organism, giving you scientific clues to navigate the Tree of Life.

---

## 🎮 How to Play & Core Mechanics

Each round begins with a hidden target organism. Enter any organism's common or scientific name into the search box to make a guess.

Whenever you submit a guess, Phylogenle computes two real-world evolutionary metrics:

### 1. Divergence Time (`Diverged: ... MYA`)
- **TMRCA (Time to Most Recent Common Ancestor):** The estimated time in **Millions of Years Ago (MYA)** when the evolutionary lineage of your guessed organism split from the lineage of the target organism.
- **The Golden Rule:** **The smaller the MYA number, the closer your guess is on the Tree of Life!**
  - *Example:* If the secret is **Lion** and you guess **Tiger**, they diverged only **4.72 MYA** (sister species in the same genus).
  - *Example:* If the secret is **Lion** and you guess **Wolf**, they diverged **55.0 MYA** (shared order *Carnivora*).
  - *Example:* If the secret is **Lion** and you guess **Bald Eagle**, they diverged **312.0 MYA** (shared clade *Amniota*).
  - *Example:* If the secret is **Lion** and you guess **Sunflower**, they diverged **1,100.0 MYA** (shared domain *Eukaryota*).

### 2. Lowest Common Ancestor (`Shared Taxonomic Clade: ...`)
- Phylogenle identifies the most specific ancestral taxonomic group that unites your guess with the mystery target.
- Clades range from broad ancestral domains down to immediate genera:
  - `Domain: Eukaryota`
  - `Kingdom: Animalia (Metazoa)`
  - `Phylum: Chordata`
  - `Class: Mammalia`
  - `Order: Carnivora`
  - `Family: Felidae`
  - `Genus: Panthera`
  - `Species: Panthera leo (Match!)`

---

## 🎨 The 8-Tier Taxonomic Color & Emoji System

Phylogenle maps the 8 standard Linnaean biological ranks to a high-contrast, intuitive color progression. Every feedback badge, guess card, and shareable score grid utilizes these colors:

```
[CLOSEST / EXACT]                                                                           [MOST DISTANT]
  🟩 Species  ➔  🟨 Genus  ➔  🟧 Family  ➔  🟥 Order  ➔  🟪 Class  ➔  🟦 Phylum  ➔  🟫 Kingdom  ➔  ⬛ Domain
   (0.0 MYA)     (~5 MYA)     (~30 MYA)     (~80 MYA)    (~310 MYA)    (~550 MYA)    (~680 MYA)     (>1000 MYA)
```

| Rank Level | Emoji | Badge Color | Hex Code | Typical Divergence | Meaning & Examples |
| :--- | :---: | :--- | :---: | :---: | :--- |
| **🟩 Species** | `🟩` | **Emerald Green** | `#10b981` | **0.0 MYA** | **Target Match!** You correctly deduced the mystery organism. |
| **🟨 Genus** | `🟨` | **Golden Yellow** | `#eab308` | **~1 – 15 MYA** | **Sister species in same genus** (e.g. *Panthera*: Lion vs. Tiger; *Canis*: Wolf vs. Coyote). |
| **🟧 Family** | `🟧` | **Vibrant Orange** | `#f97316` | **~15 – 45 MYA** | **Same family** (e.g. *Felidae*: Lion vs. Cheetah; *Canidae*: Dog vs. Red Fox). |
| **🟥 Order** | `🟥` | **Crimson Red** | `#ef4444` | **~45 – 100 MYA** | **Same order** (e.g. *Carnivora*: Dog vs. Grizzly Bear; *Primates*: Human vs. Lemur). |
| **🟪 Class** | `🟪` | **Royal Purple** | `#a855f7` | **~100 – 350 MYA** | **Same class** (e.g. *Mammalia*, *Aves*, *Reptilia*, *Amphibia*, *Actinopteri*). |
| **🟦 Phylum** | `🟦` | **Sapphire Blue** | `#3b82f6` | **~350 – 600 MYA** | **Same phylum** (e.g. *Chordata*, *Arthropoda*, *Mollusca*, *Streptophyta*). |
| **🟫 Kingdom** | `🟫` | **Earth Brown** | `#a16207` | **~600 – 900 MYA** | **Same kingdom** (e.g. *Animalia*, *Plantae*, *Fungi*, *Protista*, *Bacteria*). |
| **⬛ Domain** | `⬛` | **Jet Black** | `#475569` | **>1000 MYA** | **Cellular root** (*Eukaryota*, *Bacteria*, *Viruses*). |

### 🏳️ The Surrender Flag (`⬜` White Square)
- **Solved Victory:** Your share string concludes with `🟩`:
  ```
  Phylogenle #1026 🧬
  Solved in 5 guesses!
  ⬛🟦🟪🟥🟩
  ```
- **Surrender / Reveal:** If you choose to reveal the answer with "Give Up", your share string terminates with `⬜` (the white flag of surrender):
  ```
  Phylogenle #1026 🧬
  Revealed
  ⬛🟦🟪🟥⬜
  ```

---

## 🕹️ Game Modes: Daily vs. Practice

Phylogenle features a persistent dual-mode system accessible via a segmented toggle (`[ 📅 Daily | 🧬 Practice ]`) in the navigation bar:

### 1. 📅 Daily Challenge Mode
- **One puzzle per day:** Synchronized globally at midnight. All players solve the exact same target organism each day.
- **Streak & Stats Tracking:** Tracks games played, current win streak, max win streak, and guess count distribution.
- **Active State Persistence:** In-progress daily guesses are saved to `localStorage` under `daily_state_YYYY-MM-DD`.
- **Target Mismatch Protection:** If a player leaves an in-progress puzzle open across midnight, Phylogenle displays a clear alert banner indicating the daily organism has rotated, offering a one-click button to restart fresh without desyncing state.

### 2. 🧬 Practice Mode
- **Unlimited Gameplay:** Play as many rounds as you want from the full 29,748 organism catalog.
- **Instant Replay:** A "New Game" button allows you to spin up a new random target organism immediately upon solving or surrendering.
- **Streak-Safe Isolation:** Practice games are stored separately in `practice_state` and never alter or overwrite your daily competition stats and streaks.
- **URL & Storage Persistence:** Selecting practice mode updates the URL to `?mode=practice` and persists your preference across page refreshes.

---

## 🛠️ Interactive Gameplay Features

### 1. Dynamic D3.js Cladogram (Phylogenetic Tree)
As you make guesses, Phylogenle dynamically constructs an interactive evolutionary tree diagram in real-time using **D3.js**:
- **Branch Topology:** Visualizes where each guessed organism branches off relative to the target lineage.
- **Ancestor Node Badges:** Highlights the divergence points with their time in MYA and taxonomic clade names.
- **Interactive Navigation:** Smooth panning, zooming (mouse wheel / trackpad gestures / touch pinch), and reset controls.
- **Wikipedia Clade Previews:** Clicking or hovering over any clade node on the tree reveals summary descriptions and Wikipedia links for that ancestral group.

### 2. Progressive Taxonomic Hint System
Stuck on a tricky puzzle? Phylogenle provides a graduated hint button (`💡 Need a Hint?`):
- **Step-by-step rank reveals:** Rather than spoiling the species immediately, each hint reveals the next most specific taxonomic rank of the secret organism:
  - *Hint 1:* Reveals **Kingdom** (e.g. `Kingdom: Animalia`)
  - *Hint 2:* Reveals **Phylum** (e.g. `Phylum: Chordata`)
  - *Hint 3:* Reveals **Class** (e.g. `Class: Mammalia`)
  - *Hint 4:* Reveals **Order** (e.g. `Order: Carnivora`)
  - *Hint 5:* Reveals **Family** (e.g. `Family: Felidae`)
  - *Hint 6:* Reveals **Genus** (e.g. `Genus: Panthera`)
- Hints help narrow your search space while preserving the fun of deducing the exact species.

### 3. In-App Universal Species Catalog (29,748 Species)
Accessible via the bottom bar or modal button, the in-app catalog lets players explore every valid organism:
- **True 8-Rank Collapsible Hierarchy:** Domain ➔ Kingdom ➔ Phylum ➔ Class ➔ Order ➔ Family ➔ Genus/Species table.
- **Zero Endless Scrolling:** All sections start collapsed by default. Click any level to drill down smoothly.
- **Kingdom Quick Tabs:** Instant filters for *Full Tree*, *Animalia*, *Plantae*, *Fungi*, *Bacteria*, *Protista*, and *Viruses*.
- **Global Search:** Type any term to instantly filter across all 8 ranks (Domain, Kingdom, Phylum, Class, Order, Family, Genus, Common Name, and Scientific Name).
- **Lineage Breadcrumbs & Direct Guessing:** Search results display full lineage paths (e.g. `Animalia ➔ Mammalia ➔ Carnivora ➔ Felidae`) alongside an instant `🎯 Guess` button that loads the organism directly into your game.
- **Tree Controls:** Includes `[ ➕ Expand All ]` and `[ ➖ Collapse All ]` buttons.

### 4. Wikipedia Previews & Clade Links
- Every guess card and cladogram node includes clickable links to official English Wikipedia articles.
- Hovering over an organism's link fetches thumbnail photos and brief introductory snippets via the Wikipedia REST API without leaving the app.

### 5. Virtualized Autocomplete Search
- Searching among 29,748 species requires zero latency. The search bar employs virtualized scrolling and prefix matching.
- Displays both common and scientific binomial names with keyboard navigation support (`ArrowUp`, `ArrowDown`, `Enter`).

### 6. Statistics, Streaks & Share System
- **Comprehensive Stats Modal:** Displays Total Played, Win Rate %, Current Streak, and Max Streak.
- **Guess Distribution Histogram:** Visualizes how many attempts you typically require to solve puzzles.
- **One-Click Spoiler-Free Sharing:** Generates clean emoji summary strings for Twitter/X, Discord, and messaging apps.

---

## 📊 Dataset & Biodiversity Coverage

Phylogenle covers **29,748 active species** and **44,507 internal phylogenetic nodes** calibrated across all life:

| Group / Clade | Icon | Species Count | Primary Lineages Included |
| :--- | :---: | :---: | :--- |
| **Actinopteri & Fishes** | 🐟 | **9,862** | Ray-finned fishes, sharks, rays, chimaeras, lobe-finned fishes |
| **Birds (Aves)** | 🦅 | **4,651** | Passerines, raptors, waterfowl, seabirds, parrots, hummingbirds |
| **Mammals (Mammalia)** | 🐾 | **4,343** | Placentals, marsupials, monotremes, cetaceans, bats, carnivorans |
| **Amphibians (Amphibia)** | 🐸 | **3,402** | Frogs, toads, salamanders, newts, caecilians |
| **Invertebrates** | 🐙 | **2,941** | Arthropods, mollusks, echinoderms, cnidarians, annelids |
| **Reptiles (Sauropsida)** | 🦎 | **2,593** | Lizards, snakes, turtles, tortoises, crocodilians, tuatara |
| **Plants (Viridiplantae)** | 🌿 | **1,862** | Angiosperms (flowering plants), conifers, ferns, mosses, green algae |
| **Fungi** | 🍄 | **55** | Mushrooms, bracket fungi, yeasts, molds, lichens |
| **Bacteria** | 🧫 | **20** | Proteobacteria, Firmicutes, Gram-negative and Gram-positive bacilli |
| **Protists & Chromists** | 🧬 | **17** | Kelps, brown algae, red algae, water molds |
| **Viruses** | 🦠 | **2** | Herpesviruses and viral clades |
| **Total Universal Catalog** | 🌐 | **29,748** | **Complete coverage across all 8 universal biological ranks** |

---

## 🔬 Scientific Data Sources & Provenance

Phylogenle's phylogenetic tree is calibrated against peer-reviewed biological datasets:

### 1. NCBI Taxonomy Database (NIH / NLM)
- **Source:** [`taxdump.tar.gz`](https://ftp.ncbi.nih.gov/pub/taxonomy/) (`names.dmp`, `nodes.dmp`)
- **Role:** Official Linnaean hierarchy, verified Taxonomic Identifiers (TaxIDs), and ancestral lineage paths from cellular life (TaxID `1`) down to species leaves.

### 2. TimeTree 5 (The Molecular Scale of Life)
- **Source:** [TimeTree.org](http://www.timetree.org/) (Center for Biodiversity; Kumar, Stecher, Suleski, Hedges et al.)
- **Role:** Fossil-calibrated divergence time estimates (in MYA) compiled from thousands of molecular evolution publications.
- **Node Calibration Algorithm:**
  - Over 1.6 million pairwise divergence records were mapped to NCBI LCA nodes.
  - Internal ancestral nodes use the statistical median of all molecular divergence estimates:
    $$\text{NodeTime}(N_k) = \text{Median}(\{ T(A, B) \mid \text{LCA}(A, B) = N_k \})$$
  - Deep anchors calibrate the highest ranks: LUCA (~4000 MYA), Eukaryota (~1600 MYA), Animalia (~750 MYA), Chordata (~560 MYA).
  - Uncalibrated intermediate branches follow monotonic decay to preserve strict phylogenetic order:
    $$\text{Time}(\text{Species}) < \text{Time}(\text{Genus}) < \text{Time}(\text{Family}) < \dots < \text{Time}(\text{Domain})$$

### 3. Wikipedia REST API
- **Endpoint:** `https://en.wikipedia.org/api/rest_v1/page/summary/{title}`
- **Role:** Real-time hover snippets, photos, and educational article links for species and ancestral clades.

---

## ⚡ Technical Architecture & Performance

### 1. Single-File Phylogeny Tree ([`data/phylogeny_tree.json`](data/phylogeny_tree.json))
Rather than generating tens of thousands of separate JSON files, Phylogenle stores the entire tree of life in a single structured file:
- **`species`:** Maps each organism key to its full lineage array of NCBI TaxIDs:
  ```json
  "lion (panthera leo)": [1, 131567, 2759, 33154, 33208, 6072, 33213, 33511, 7711, 33554, 379583, 9681, 9688, 9689]
  ```
- **`nodes`:** Maps each TaxID to its calibrated divergence time, rank, and clade name:
  ```json
  "9681": { "rank": "Family", "name": "Felidae", "time": 13.6 }
  ```

### 2. Microsecond LCA Computation
Finding the Lowest Common Ancestor between any guess and target in [script.js](script.js) is a linear array walk from index `0` until TaxIDs diverge. Lookup takes **~0.4 microseconds** in browser memory with zero network requests.

### 3. Dual-Persistence State Machine
Game state operates on a dual-synchronization layer:
- **URL Query Parameters:** `?mode=practice` maintains mode through reloads and shared links.
- **LocalStorage Isolation:** `daily_state_YYYY-MM-DD` and `practice_state` prevent cross-mode pollution.

---

## 📂 Documentation Directory

Comprehensive project documentation is maintained in the [`docs/`](docs/) folder:

- [`docs/TAXONOMIC_CATALOG_PLAN.md`](docs/TAXONOMIC_CATALOG_PLAN.md) — The signed-off architectural specification for the 8-rank Linnaean directory.
- [`docs/DATA_ARCHITECTURE_AND_LCA_GUIDE.md`](docs/DATA_ARCHITECTURE_AND_LCA_GUIDE.md) — Technical details of the $O(1)$ memory LCA tree traversal algorithm.
- [`docs/EXCLUDED_SPECIES_REVIEW.md`](docs/EXCLUDED_SPECIES_REVIEW.md) — Review and promotion log of 3,683 evaluated candidate organisms.
- [`docs/SPECIES_EXPANSION_PLAN.md`](docs/SPECIES_EXPANSION_PLAN.md) — Roadmap for biodiversity additions across fungi, flora, and marine invertebrates.
- [`docs/DAILY_PRACTICE_TOGGLE_PROMPT.md`](docs/DAILY_PRACTICE_TOGGLE_PROMPT.md) — Standardized agent prompt template for replicating the persistent daily/practice segmented toggle in other games.

---

## ➕ CLI Tools & Expansion

### 1. Ingesting New Species (`add_species.py`)
Add any new organism to the database with a single CLI command:
```bash
python3 add_species.py "Dumbo Octopus" "Grimpoteuthis discoveryi"
# Or interactive mode:
python3 add_species.py
```
This script queries NCBI Taxonomy, interpolates ancestral divergence times, updates `phylogeny_tree.json`, and records the entry in the catalog.

### 2. Generating the 8-Rank Taxonomic Catalog (`build_taxonomic_catalog.py`)
Regenerates the complete hierarchical markdown catalog with automated sum-check assertions:
```bash
python3 build_taxonomic_catalog.py
```
*Outputs: [`species_catalog_taxonomic.md`](species_catalog_taxonomic.md) (46,036 lines, 100.00% species match, 0 dropped).*

---

## 🛠️ Local Development

To run Phylogenle locally:

```bash
# 1. Clone the repository
git clone https://github.com/amitjoshi2724/phylogenle.git
cd phylogenle

# 2. Start a static local HTTP server
python3 -m http.server 8093

# 3. Open in your browser
open http://localhost:8093/
```

---

## 📜 Credits & License

- **Creator & Lead Developer:** **Amit Joshi** ([@amitjoshi2724](https://github.com/amitjoshi2724))
- **Scientific References:** NCBI Taxonomy, TimeTree 5, and English Wikipedia.
- **License:** MIT License — free for educational and non-commercial exploration.
