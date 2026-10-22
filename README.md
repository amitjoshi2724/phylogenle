# 🧬 Phylogenle (`phylogenle-amitjoshi2724`)

> **The Daily Evolutionary Biology & Phylogenetic Cladistics Puzzle**  
> *Deduce the mystery organism through millions of years of evolutionary divergence.*

Developed by **Amit Joshi** ([@amitjoshi2724](https://github.com/amitjoshi2724))  
🌐 **Live Game:** [https://amitjoshi2724.github.io/phylogenle/](https://amitjoshi2724.github.io/phylogenle/)

---

## 🎮 How to Play

Each day at midnight, a secret organism is selected deterministically. Your goal is to deduce the target organism in as few guesses as possible using evolutionary divergence and cladistic lineage.

Whenever you submit a guess, Phylogenle calculates two real-world evolutionary metrics:

1. **`Diverged: ... MYA` (TMRCA):**  
   The estimated **Time to Most Recent Common Ancestor** measured in Millions of Years Ago (MYA). The smaller the number, the closer your guess is on the Tree of Life to the mystery organism.
   - *Example:* Guessing **Tiger** when the secret is **Lion** will reveal `Diverged: 3.8 MYA`.
   - *Example:* Guessing **Blue Whale** when the secret is **Chimpanzee** will reveal `Diverged: 94.0 MYA`.

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
| **Species (Exact)** | `🟩` | **Emerald Green** (`#10b981`) | **Exact Match (0 MYA)!** You found the daily secret organism. |
| **Genus Match** | `🟨` | **Golden Yellow** (`#eab308`) | **Direct sister species** in the same genus (e.g. *Lion* vs *Tiger*, *Dog* vs *Wolf*). |
| **Family Match** | `🟧` | **Vibrant Orange** (`#f97316`) | **Same family** (e.g. *Felidae*: Cat vs Cheetah, *Canidae*: Wolf vs Fox). |
| **Order Match** | `🟥` | **Crimson Red** (`#ef4444`) | **Same order** (e.g. *Carnivora*: Dog vs Bear, *Primates*: Human vs Lemur). |
| **Class Match** | `🟪` | **Royal Purple** (`#a855f7`) | **Same class** (e.g. *Mammalia*, *Aves*, *Reptilia*, *Insecta*). |
| **Phylum Match** | `🟦` | **Sapphire Blue** (`#3b82f6`) | **Same phylum** (e.g. *Chordata*, *Arthropoda*, *Mollusca*). |
| **Kingdom Match** | `🟫` | **Earth Brown** (`#a16207`) | **Root of Kingdom Animalia** (Metazoa root ~650–800 MYA). |
| **Domain Match** | `⬛` | **Jet Black** (`#475569`) | **Domain Eukaryota** (shared cellular life root >1000 MYA). |

### 🏳️ The Surrender / Reveal Indicator (`⬜` White Square)
- If you solve the puzzle, your score string ends on **`🟩` (Victory)**:
  ```
  Phylogenle #1026 🧬
  Solved in 5 guesses!
  🟦🟥🟧🟨🟩
  ```
- If you press **"Give Up"** to forfeit and reveal the secret answer, the share string ends with a **`⬜` White Square (White Flag of Surrender)**:
  ```
  Phylogenle #1026 🧬
  Revealed
  🟦🟥🟧🟨⬜
  ```

---

## ✨ Features

- **🌳 Real-Time D3.js Phylogenetic Tree:**  
  Every guess is dynamically placed onto an interactive cladogram on the right side of the screen. Nodes reflect divergence timelines, with vertical label staggering and zoom/pan controls.
- **📖 Instant Wikipedia Tooltip Cards:**  
  Hover over or click any organism or clade node on the board or tree to read its live Wikipedia summary without leaving the game.
- **📅 Interactive Archive & Calendar Suite:**  
  Play any past daily challenge! Includes:
  - 42-cell calendar grid with month/year navigation.
  - Searchable list view with status filters (All, Solved, Unplayed).
  - **Testing & Reset Toolbar:** Reset any specific date or wipe cached archive records to replay updated puzzles.
- **☁️ Dual-Layer Local & Cloud Synchronization:**  
  Seamless offline-first play with `localStorage`, backed by real-time Google Cloud Firestore profile synchronization when logged in with Google Auth.
- **♾️ Endless Practice Mode:**  
  Switch instantly between the Daily Challenge and Unlimited Practice Mode to train taxonomy recognition with randomized mystery organisms.

---

## 🔬 Scientific Data & Methodology

Every divergence time and taxonomic classification in Phylogenle is calibrated against real-world scientific datasets:
1. **TimeTree 5 (`timetree.org`):** Node-level median divergence times synthesized from thousands of peer-reviewed molecular phylogenetics studies.
2. **NCBI Taxonomy (`ncbi.nlm.nih.gov/taxonomy`):** Strict cladistic parentage, verified TaxIDs, and rank resolution (`Superkingdom` through `Species`).
3. **Curated Active Catalog:** 344+ species spanning Mammals, Birds, Reptiles, Amphibians, Fishes, and Invertebrates (see [`species_catalog.md`](species_catalog.md)).
4. **Planned Pool Expansion:** Scaling to 1,000+ species via automated scraping of iNaturalist research-grade observations and Wikidata knowledge graphs (see [`SPECIES_EXPANSION_PLAN.md`](SPECIES_EXPANSION_PLAN.md)).

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
