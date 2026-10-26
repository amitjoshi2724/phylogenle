# 🧬 Tree Visualization, Taxonomic Architecture & Biology Fixes

> **Target Issues:**
> 1. Tree Visualization Inversion (Gnathostomata displayed above Chordata; Euteleostomi spine branching).
> 2. Root Wikipedia Link & Domain Black Square (`⬛`).
> 3. True 3-Domain Taxonomy (Ingesting Domain *Archaea* & clarifying non-cellular *Viruses*).
> 4. Multi-Common-Name Synonym Engine (e.g. *Naso Tang* for *Orangespine Unicornfish*).

---

## 1. Issue 1: Tree Visualization Inversion & Spine Topology

### The Problem in the Screenshot
In today's puzzle (target: *Orangespine Unicornfish* / *Naso lituratus*), the tree rendered:
- Top: `⬛ root`
- Child: `🟦 Gnathostomata`
- Child of Gnathostomata: `🟦 Chordata` (!?)
- Child of Chordata: `🟦 Euteleostomi`
- Children of Euteleostomi: `African Bush Viper`, `Human`, `Saltwater Crocodile`, `Grey Crow`, and `Actinopteri`.

### Root Cause Analysis
1. **The Time-Sorting Inversion Bug:**
   In `script.js` line 1432, `updateTree()` gathered all trunk nodes into `trunkMap` and sorted them **solely by divergence time (`timeB - timeA`)**:
   ```javascript
   const trunkList = Array.from(trunkMap.values()).sort((a, b) => {
       const tA = a.time === -1 ? Infinity : a.time;
       const tB = b.time === -1 ? Infinity : b.time;
       return tB - tA; // Sorted purely by float time!
   });
   ```
   In `data/phylogeny_tree.json`:
   - Node 7776 (`Gnathostomata`) had `time: 462.0 MYA`.
   - Node 7711 (`Chordata`) had `time: 445.7 MYA`.
   - Node 117571 (`Euteleostomi`) had `time: 429.0 MYA`.

   Because $462.0 > 445.7$, the sorting code placed `Gnathostomata` **BEFORE** `Chordata`!  
   Then lines 1450–1458 linearly chained them: `trunkList[i].children.push(trunkList[i + 1])`.  
   This mathematically forced `Chordata` to become a child of its own sub-clade `Gnathostomata`!

2. **Why are Humans, Vipers, Crocodiles, and Crows under `Euteleostomi`?**
   - In evolutionary biology, humans and all land vertebrates (Tetrapods / Sarcopterygians) diverged from ray-finned fish (*Naso*) at **Euteleostomi** (~429 MYA — the common ancestor of all bony vertebrates).
   - Scientifically, the pairwise LCA between any land vertebrate and a teleost fish **is indeed Euteleostomi**.
   - However, because `Euteleostomi` was assigned `rank: "Phylum"` in the tree dataset, it received a blue square (`🟦`), making it look like an erroneous rival phylum to Chordata rather than a bony-vertebrate clade within Chordata.

### The Permanent Fix
1. **Order Trunk Nodes by Lineage Depth, NOT by Floating Time:**
   The target organism's ancestral lineage (`targetLin`) is **already in strict biological parent-to-child order**:
   `root (idx 0) -> cellular organisms (idx 1) -> Eukaryota (idx 2) -> Metazoa (idx 4) -> Chordata (idx 8) -> Vertebrata (idx 10) -> Gnathostomata (idx 11) -> Euteleostomi (idx 13) -> Actinopteri (idx 15) -> Clupeocephala (idx 19) -> Acanthuridae (idx 29) -> Naso (idx 31)`

   Sorting `trunkList` by its **index along `targetLin`** guarantees:
   - `Chordata` (idx 8) is **ALWAYS** above `Gnathostomata` (idx 11).
   - `Gnathostomata` (idx 11) is **ALWAYS** above `Euteleostomi` (idx 13).
   - Inversions are topologically impossible regardless of minor divergence time calibration noise.

2. **Strict Time Monotonicity:**
   Parent divergence times must be $\ge$ child divergence times ($T_{\text{parent}} \ge T_{\text{child}}$). Any ancestor node whose time is lower than its child is clamped to be at least equal to the child.

---

## 2. Issue 2: Root Wikipedia Redirect & Domain Square Color

### The Problem
- Clicking or hovering on `root` in the tree redirected to Wikipedia's `Root` article (the botanical plant root!).
- The root square color needed verification to guarantee it is the domain-level black square (`⬛`).

### Root Cause
- In `script.js`, node click/hover handlers used `d.data.wikiTitle || d.data.name` directly. For the root node, `query` was `"root"`, which resolves on Wikipedia to the plant organ.

### The Fix
1. **Wikipedia Target Remapping:**
   When node name/wikiTitle is `"root"` or `"cellular organisms"`, remap the Wikipedia target to **`Last_universal_common_ancestor`** (LUCA) or **`Tree_of_life_(biology)`**.
2. **Display & Styling:**
   - Label: `Root (LUCA)`
   - Rank: `Domain`
   - Emoji: `⬛` (Black Square)
   - Tooltip: Summary of the Last Universal Common Ancestor of all cellular life.

---

## 3. Issue 3: The True 3 Domains of Life (Ingesting Archaea)

### The Problem
- The current tree dataset contained **Bacteria** (Domain `⬛`) and **Eukaryota** (Domain `⬛`), but **Archaea was completely missing**.
- Non-cellular *Viruses* were listed alongside Domains, while the foundational 3rd domain of cellular life was excluded.

### The Biological Standard (Woese 3-Domain System)
All cellular life on Earth belongs to three primary domains:
1. **Domain Bacteria** (Eubacteria)
2. **Domain Archaea** (Archaebacteria / Extremophiles / Methanogens)
3. **Domain Eukaryota** (Animals, Plants, Fungi, Protists)
*(+ Non-cellular biological entities / Viruses as Acytota)*

### The Fix
1. Ingest **Domain Archaea** (NCBI taxid `2157`, divergence time ~3,500 MYA) as a direct descendant of `cellular organisms (131567)` alongside Bacteria and Eukaryota.
2. Ingest iconic, high-profile Archaea species into `species_list.json` and `phylogeny_tree.json`:
   - *Human Gut Methanogen (Methanobrevibacter smithii)* — taxid 2172
   - *Extreme Halophile Archaea (Halobacterium salinarum)* — taxid 2242
   - *Hydrothermal Vent Hyperthermophile (Pyrolobus fumarii)* — taxid 70258
   - *Acidophilic Thermophile (Sulfolobus solfataricus)* — taxid 2287
   - *Asgard Archaea (Lokiarchaeum ossiferum)* — taxid 2593649
   - *Radiation-Resistant Archaea (Thermococcus gammatolerans)* — taxid 563141
3. Update `build_taxonomic_catalog.py` so the catalog hierarchy formally displays **Bacteria**, **Archaea**, and **Eukaryota**.

---

## 4. Issue 4: Alternative Common Names & Synonyms Engine

### The Problem
Today's secret target was *Naso lituratus*, which is globally known as **Naso Tang**, **Orangespine Unicornfish**, **Orange-spine Unicornfish**, **Smoothhead Unicornfish**, and **Clown Tang**.
Because `species_list.json` only contained the exact string `"Orangespine Unicornfish (Naso lituratus)"`, typing `"Naso Tang"` returned zero autocomplete suggestions and was rejected on submission!

This affects dozens of famous organisms:
- *Naso Tang* vs *Orangespine Unicornfish* (*Naso lituratus*)
- *Mountain Lion* / *Puma* / *Panther* vs *Cougar* (*Puma concolor*)
- *Killer Whale* vs *Orca* (*Orcinus orca*)
- *Grizzly Bear* / *Kodiak Bear* vs *Brown Bear* (*Ursus arctos*)
- *Domestic Dog* vs *Dog* (*Canis lupus familiaris*)
- *American Bison* vs *Buffalo* (*Bison bison*)
- *Wapiti* vs *Elk* (*Cervus canadensis*)
- *Caribou* vs *Reindeer* (*Rangifer tarandus*)
- *Ratel* vs *Honey Badger* (*Mellivora capensis*)
- *Duck-billed Platypus* vs *Platypus* (*Ornithorhynchus anatinus*)

### The Fix: Multi-Synonym Registry (`data/species_aliases.json`)
1. Create `data/species_aliases.json` mapping all common colloquial and regional names to their canonical species in `species_list.json`.
2. **Autocomplete Integration:**
   When searching, the autocomplete checks both canonical titles and aliases. Typing `"Naso Tang"` returns:
   `Orangespine Unicornfish (Naso lituratus) — aka Naso Tang`
3. **Direct Submission Resolution:**
   If a user types an exact alias (e.g. `"Naso Tang"` or `"Mountain Lion"`) and presses Enter, `handleGuess()` automatically resolves it to the canonical species.
