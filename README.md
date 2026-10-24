# 🧬 Phylogenle (`phylogenle-amitjoshi2724`)

> **The Daily Evolutionary Biology & Phylogenetic Cladistics Puzzle**  
> *Deduce the mystery organism through hundreds of millions of years of evolutionary divergence.*

Developed by **Amit Joshi** ([@amitjoshi2724](https://github.com/amitjoshi2724))  
🌐 **Live Game:** [https://amitjoshi2724.github.io/phylogenle/](https://amitjoshi2724.github.io/phylogenle/)

---

## 🎮 How to Play

Each day at midnight, a secret organism is selected deterministically. Your goal is to deduce the target organism in as few guesses as possible using evolutionary divergence and cladistic lineage.

Whenever you submit a guess, Phylogenle calculates two real-world evolutionary metrics:

1. **`Diverged: ... MYA` (TMRCA):**  
   The estimated **Time to Most Recent Common Ancestor** measured in Millions of Years Ago (MYA). The smaller the number, the closer your guess is on the Tree of Life to the mystery organism.
   - *Example:* Guessing **Tiger** when the secret is **Lion** reveals `Diverged: 4.72 MYA`.
   - *Example:* Guessing **Blue Whale** when the secret is **Chimpanzee** reveals `Diverged: 96.0 MYA`.

2. **Shared Taxonomic Clade (LCA):**  
   The Lowest Common Ancestor rank and clade name shared between your guess and the secret organism.
   - *Example:* `Genus: Panthera`, `Family: Felidae`, `Order: Carnivora`, `Class: Mammalia`, etc.

---

## 🎨 The 8-Tier Color Square & Emoji System

Every guess card, feedback badge, and shareable score grid utilizes an 8-tier solid square color spectrum:

```
[CLOSEST / EXACT]                                                                           [MOST DISTANT]
  🟩 Species  ➔  🟨 Genus  ➔  🟧 Family  ➔  🟥 Order  ➔  🟪 Class  ➔  🟦 Phylum  ➔  🟫 Kingdom  ➔  ⬛ Domain
   (0 MYA)       (~5 MYA)     (~30 MYA)     (~80 MYA)    (~310 MYA)    (~550 MYA)    (~680 MYA)     (>1000 MYA)
```

| Rank Level | Square Emoji | Badge Color | Meaning & Examples |
| :--- | :---: | :--- | :--- |
| **Species (Match)** | `🟩` | **Emerald Green** (`#10b981`) | **Target Match (0.0 MYA)!** You correctly deduced the mystery organism. |
| **Genus Match** | `🟨` | **Golden Yellow** (`#eab308`) | **Direct sister species** in the same genus (e.g. *Lion* vs *Tiger*, *Dog* vs *Wolf*). |
| **Family Match** | `🟧` | **Vibrant Orange** (`#f97316`) | **Same family** (e.g. *Felidae*: Cat vs Cheetah, *Canidae*: Wolf vs Fox). |
| **Order Match** | `🟥` | **Crimson Red** (`#ef4444`) | **Same order or suborder** (e.g. *Carnivora*: Dog vs Bear, *Feliformia*: Cat vs Hyena). |
| **Class Match** | `🟪` | **Royal Purple** (`#a855f7`) | **Same class** (e.g. *Mammalia*, *Aves*, *Reptilia*, *Insecta*). |
| **Phylum Match** | `🟦` | **Sapphire Blue** (`#3b82f6`) | **Same phylum** (e.g. *Chordata*, *Arthropoda*, *Mollusca*). |
| **Kingdom Match** | `🟫` | **Earth Brown** (`#a16207`) | **Kingdom Animalia / Metazoa** (Metazoa/Bilateria root ~600–750 MYA). |
| **Domain Match** | `⬛` | **Jet Black** (`#475569`) | **Domain Eukaryota** (cellular life root >1000 MYA). |

### 🏳️ The Surrender / Reveal Indicator (`⬜` White Square)
- If you solve the puzzle, your score string ends on **`🟩` (Victory)**:
  ```
  Phylogenle #1026 🧬
  Solved in 5 guesses!
  🟦🟥🟧🟨🟩
  ```
- If you press **"Give Up"** to surrender and reveal the secret answer, the share string ends with a **`⬜` White Square (White Flag of Surrender)**:
  ```
  Phylogenle #1026 🧬
  Revealed
  🟦🟥🟧🟨⬜
  ```

---

## 🔬 Scientific Data Sources & Provenance

Phylogenle's dataset is rigorously calibrated against peer-reviewed molecular biology and taxonomy databases:

### 1. NCBI Taxonomy Database (National Center for Biotechnology Information / NIH)
- **Source:** [`taxdump.tar.gz`](https://ftp.ncbi.nih.gov/pub/taxonomy/) (`names.dmp`, `nodes.dmp`)
- **What it provides:** 
  - Official Linnaean hierarchy, verified Taxonomic IDs (TaxIDs), and phylogenetic lineage paths from cellular life (TaxID `1`) down to species leaves.
  - Binomial scientific names and verified English vernacular common names.
- **Filtering Applied:**
  - **Universal Tree of Life Scope:** Encompasses all kingdoms and domains of life: Animals, Plants, Fungi, Bacteria, Archaea, Protists, and Viruses.
  - Sauropsid clade classification to properly differentiate non-avian reptiles from birds and invertebrates.

### 2. TimeTree 5 (The Molecular Scale of Life)
- **Source:** [TimeTree.org](http://www.timetree.org/) (Center for Biodiversity, Temple University & Penn State; Kumar, Stecher, Suleski, Hedges et al.)
- **What it provides:**
  - Fossil-calibrated divergence time estimates (in Millions of Years Ago - MYA) compiled from thousands of peer-reviewed molecular evolution studies.
- **Node Calibration Pipeline:**
  - Over **1.6 million pairwise divergence records** were mapped to their NCBI Lowest Common Ancestor (LCA) nodes.
  - For each internal ancestral node $N_k$, the statistical **median** of all molecular divergence estimates was computed:
    $$\text{NodeTime}(N_k) = \text{Median}(\{ T(A, B) \mid \text{LCA}(A, B) = N_k \})$$
  - Deep evolutionary anchors (LUCA / root ~4000 MYA, cellular organisms ~3800 MYA, Eukaryota ~1600 MYA, Opisthokonta ~1200 MYA, Viridiplantae ~1100 MYA, Fungi ~1000 MYA, Metazoa ~750 MYA) calibrate all high-level ancestral nodes.
  - For fine-grained sub-clades without direct fossil calibration papers, **monotonic ancestral decay** was applied:
    $$\text{NodeTime}(\text{Child}) = \text{Round}(\text{NodeTime}(\text{Parent}) \times 0.72, 1)$$
  - Strict cladistic monotonicity is guaranteed: $\text{Time}(\text{Species}) < \text{Time}(\text{Genus}) < \text{Time}(\text{Family}) < \text{Time}(\text{Order}) < \text{Time}(\text{Class}) < \text{Time}(\text{Phylum}) < \text{Time}(\text{Kingdom}) < \text{Time}(\text{Domain})$.

### 3. Wikipedia REST API (`en.wikipedia.org`)
- **Endpoint:** `https://en.wikipedia.org/api/rest_v1/page/summary/{title}`
- **What it provides:** Real-time hover tooltips, summary snippets, and links to Wikipedia articles for both guessed organisms and ancestral clades.

---

## 📊 Dataset Overview

- **Active Playable Species:** **29,748 species across all life**
- **Calibrated Internal LCA Nodes:** **44,507 nodes**
- **Clade Breakdown:**
  - 🐾 **Mammals:** 4,343 species
  - 🦅 **Birds:** 4,651 species
  - 🦎 **Reptiles:** 2,593 species
  - 🐸 **Amphibians:** 3,402 species
  - 🐟 **Fishes:** 9,862 species
  - 🐙 **Invertebrates:** 2,941 species
  - 🌿 **Plants:** 1,862 species
  - 🍄 **Fungi:** 55 species
  - 🦠 **Bacteria:** 20 species
  - 🔬 **Protists:** 17 species
  - 🧬 **Viruses:** 2 species
- **Promoted Candidates Log:** 100% of the 3,683 evaluated candidates (plants, fungi, bacteria, sister species, subspecies, and parasites) are fully active in [`EXCLUDED_SPECIES_REVIEW.md`](EXCLUDED_SPECIES_REVIEW.md).
- **Original Baseline Guarantee:** 100% of the 344 original species from [`species_list_ORIGINAL_UNTOUCHED.json`](species_list_ORIGINAL_UNTOUCHED.json) remain present and untouched.

---

## ⚡ Global Phylogeny Tree Architecture

Instead of generating $O(N^2)$ individual JSON shard files (which would require 27,000 files and ~29.6 GB of disk space), Phylogenle stores the entire animal tree of life in a single structured file:

### [`data/phylogeny_tree.json`](data/phylogeny_tree.json)
- **`species`:** Maps each species string to an array of NCBI TaxIDs from root down to leaf:
  ```json
  "lion (panthera leo)": [1, 131567, 2759, 33154, 33208, 6072, 33213, 33511, 7711, ..., 33554, 379583, 9681, 9688, 9689]
  ```
- **`nodes`:** Maps each TaxID to its calibrated divergence time, rank, and clade name:
  ```json
  "33554": { "rank": "Order", "name": "Carnivora", "time": 55.0 },
  "379583": { "rank": "Order", "name": "Feliformia", "time": 37.0 },
  "9681": { "rank": "Family", "name": "Felidae", "time": 13.6 }
  ```
- **Runtime LCA Lookup:** Finding the LCA between any guess and target in [script.js](script.js) is a simple linear array walk from index `0` until TaxIDs diverge. Lookup takes **~0.4 microseconds** in browser memory with zero network latency.

For technical architecture details, see [`DATA_ARCHITECTURE_AND_LCA_GUIDE.md`](DATA_ARCHITECTURE_AND_LCA_GUIDE.md).

---

## ➕ Adding New Species

Phylogenle includes an automated CLI ingestion tool: **`add_species.py`**. When new animal species trickle in, you can add them with one command:

```bash
# Method 1: Common and Scientific name arguments
./venv/bin/python3 add_species.py "Dumbo Octopus" "Grimpoteuthis discoveryi"

# Method 2: Combined string
./venv/bin/python3 add_species.py "Capybara (Hydrochoerus hydrochaeris)"

# Method 3: Interactive prompt
./venv/bin/python3 add_species.py
```

### What `add_species.py` Does Automatically:
1. Validates the scientific name against NCBI Taxonomy.
2. Verifies the organism is within Kingdom Metazoa (Animalia).
3. Retrieves the complete ancestral TaxID lineage path.
4. Interpolates and calibrates any newly introduced internal nodes.
5. Updates `data/phylogeny_tree.json` (formatted cleanly line-by-line).
6. Updates `data/species_list.json` (autocomplete pool).
7. Updates `data/species_taxonomy_catalog.json` (metadata directory).
8. Inserts the entry into `species_catalog.md` under its clade and order table.

---

## 🗄️ Archive Directory Structure

All legacy files not needed by the active global tree engine have been cleanly archived:

- **[`archive/old_species_shards/`](archive/old_species_shards/):** Contains the 508 individual legacy species JSON shards (e.g. `lion_(panthera_leo).json`, etc.) from the pre-tree architecture.
- **[`archive/legacy_scripts/`](archive/legacy_scripts/):** Contains legacy one-off scrapers, shard generators, and test dumps (`expand_dataset.py`, `generate_shards.py`, `test_timetree.py`, `ajax_*.html`, etc.).

---

## 🛠️ Local Development

To run Phylogenle locally:

```bash
# Clone the repository
git clone https://github.com/amitjoshi2724/phylogenle.git
cd phylogenle

# Start a local static HTTP server (Python 3)
python3 -m http.server 8089

# Open in your browser
open http://localhost:8089/
```

---

## 📜 Credits & License

- **Creator & Lead Developer:** **Amit Joshi** ([@amitjoshi2724](https://github.com/amitjoshi2724))
- **Firebase Project:** `phylogenle-amitjoshi2724`
- **License:** MIT License — free for educational and non-commercial use.
