# 🧬 Phylogenle: Systematic Biodiversity Expansion Architecture & Blueprint

**Document Version:** 1.0  
**Target Database Expansion:** 344 ➔ ~600–700 Curated Species  
**Objective:** Replace ad-hoc manual additions with an automated, data-driven pipeline that scrapes authoritative biological databases to eliminate "island species" and establish rich sister-species clusters.

---

## 1. Problem Statement & Design Principles

### Why Ad-Hoc / "LLM Memory" Additions Fail
1. **Isolated "Island" Taxa:** Adding a single organism (e.g., only 1 hummingbird or 1 butterfly) breaks gameplay. When a player deduces the Family (e.g., *Trochilidae*), their logical next move is to guess another hummingbird. If no sister species exist in the dictionary, the game feels incomplete and frustrating.
2. **Recognition Imbalance:** Uncurated taxonomy queries risk adding obscure micro-organisms (e.g., microscopic nematodes or deep-sea mites with no common names) that normal players cannot guess.
3. **Nomenclature Inconsistencies:** Outdated synonyms or disputed common names break autocomplete and Wikipedia linking.

### Core Architectural Principles
- **The "No Island Species" Rule:** Every organism in the game must belong to a cluster of at least **3 to 8 recognizable species** within the same Family or Genus.
- **Cultural & Educational Recognition:** Every candidate must pass a popularity filter (Wikipedia pageviews / iNaturalist observation counts).
- **100% Cladistic & Temporal Integrity:** Every species must have a verified NCBI TaxID and peer-reviewed divergence time from TimeTree 5.

---

## 2. Authoritative Data Sources for Scraping & Ingestion

Instead of manual guessing, we will extract candidates programmatically from 5 authoritative biodiversity platforms:

### A. iNaturalist Research API (`api.inaturalist.org/v1`)
* **Endpoint:** `GET /observations/species_counts?taxon_id=35521&quality_grade=research`
* **Purpose:** Queries the most observed wild animals in the world.
* **Why it matters:** 
  - Guarantees that every species has an official, widely used English common name.
  - Ensures every animal is something real people observe and recognize (e.g., Blue Morpho, Anna's Hummingbird, Red-tailed Hawk).

### B. Wikidata SPARQL Knowledge Graph (`query.wikidata.org`)
* **Query Mechanism:** SPARQL endpoint querying instances of Taxon (`wdt:P31 wd:Q16521`) within Kingdom Animalia (`wdt:P171* wd:Q729`).
* **Filtering Criteria:**
  - Must have an English Wikipedia sitelink (`wikibase:sitelinks > 15`).
  - Must have a verified NCBI TaxID property (`wdt:P685`).
  - Sorted by monthly pageview count to filter out obscure scientific papers.

### C. IUCN Red List Global Database API (`apiv3.iucnredlist.org`)
* **Purpose:** Harvests high-profile, globally iconic species across conservation categories (Critically Endangered, Vulnerable, Least Concern).
* **Why it matters:** Captures charismatic megafauna and famous conservation icons that players frequently search for (e.g., Axolotl, Snow Leopard, Vaquita, Leatherback Sea Turtle, Kakapo).

### D. Wikipedia Zoology Portals & Featured Lists
* **Scraping Targets:**
  - Wikipedia: *List of birds by common name* / *List of hummingbird species*
  - Wikipedia: *List of butterflies of North America and Europe*
  - Wikipedia: *List of canids / List of felids / List of cetaceans*
  - Wikipedia: *List of sharks / List of snakes*
* **Extraction:** Programmatic regex/BeautifulSoup parser pulling `Common Name (Scientific Name)`.

### E. Local NCBI Taxonomy & TimeTree Calibration (Already in Repository)
* **Local NCBI Taxdump (`taxdump.tar.gz`):** Offline tree traversal via `ete3` to verify lineages, ranks (Kingdom, Phylum, Class, Order, Family, Genus), and Lowest Common Ancestor (LCA) nodes.
* **TimeTree 5 (`timetree.org`):** Automated retrieval of median evolutionary divergence times in Millions of Years Ago (MYA).

---

## 3. High-Priority Taxonomic Expansion Clusters

The table below outlines the 10 core biodiversity clusters scheduled for expansion to achieve balanced gameplay:

| Clade / Cluster | Current Count | Target Count | High-Priority Species to Harvest & Ingest |
| :--- | :---: | :---: | :--- |
| **1. Hummingbirds**<br>*(Trochilidae)* | 1 | **5** | • Anna's Hummingbird (*Calypte anna*)<br>• Rufous Hummingbird (*Selasphorus rufus*)<br>• Bee Hummingbird (*Mellisuga helenae*) [World's smallest bird]<br>• Sword-billed Hummingbird (*Ensifera ensifera*) |
| **2. Butterflies & Moths**<br>*(Lepidoptera)* | 4 | **12** | • Blue Morpho (*Morpho peleides*)<br>• Painted Lady (*Vanessa cardui*)<br>• Peacock Butterfly (*Aglais io*)<br>• Zebra Longwing (*Heliconius charithonia*)<br>• Eastern Tiger Swallowtail (*Papilio glaucus*)<br>• Luna Moth (*Actias luna*)<br>• Death's-head Hawkmoth (*Acherontia atropos*)<br>• Peppered Moth (*Biston betularia*) |
| **3. Birds of Prey & Owls**<br>*(Accipitriformes, Falconiformes, Strigiformes)* | 12 | **22** | • Harpy Eagle (*Harpia harpyja*)<br>• Golden Eagle (*Aquila chrysaetos*)<br>• Gyrfalcon (*Falco rusticolus*)<br>• Red-tailed Hawk (*Buteo jamaicensis*)<br>• Cooper's Hawk (*Accipiter cooperii*)<br>• Great Horned Owl (*Bubo virginianus*)<br>• Snowy Owl (*Bubo scandiacus*)<br>• Eurasian Eagle-Owl (*Bubo bubo*)<br>• Burrowing Owl (*Athene cunicularia*)<br>• Secretarybird (*Sagittarius serpentarius*) |
| **4. Whales, Dolphins & Porpoises**<br>*(Cetacea)* | 9 | **18** | • Sperm Whale (*Physeter macrocephalus*)<br>• Narwhal (*Monodon monoceros*)<br>• Spinner Dolphin (*Stenella longirostris*)<br>• Amazon River Dolphin (*Inia geoffrensis*)<br>• Long-finned Pilot Whale (*Globicephala melas*)<br>• False Killer Whale (*Pseudorca crassidens*)<br>• Vaquita (*Phocoena sinus*)<br>• Commerson's Dolphin (*Cephalorhynchus commersonii*) |
| **5. Bears & Canids**<br>*(Ursidae & Canidae)* | 13 | **22** | • Grizzly / Brown Bear (*Ursus arctos*)<br>• Polar Bear (*Ursus maritimus*)<br>• Gray Fox (*Urocyon cinereoargenteus*)<br>• Golden Jackal (*Canis aureus*)<br>• Maned Wolf (*Chrysocyon brachyurus*)<br>• Raccoon Dog / Tanuki (*Nyctereutes procyonoides*)<br>• Bush Dog (*Speothos venaticus*) |
| **6. Wild Felines**<br>*(Felidae)* | 13 | **20** | • Snow Leopard (*Panthera uncia*)<br>• Bobcat (*Lynx rufus*)<br>• Canada Lynx (*Lynx canadensis*)<br>• Eurasian Lynx (*Lynx lynx*)<br>• Pallas's Cat (*Otocolobus manul*)<br>• Sand Cat (*Felis margarita*)<br>• Black-footed Cat (*Felis nigripes*) |
| **7. Snakes**<br>*(Serpentes)* | 9 | **18** | • Black Mamba (*Dendroaspis polylepis*)<br>• Inland Taipan (*Oxyuranus microlepidotus*)<br>• Timber Rattlesnake (*Crotalus horridus*)<br>• Cottonmouth / Water Moccasin (*Agkistrodon piscivorus*)<br>• Copperhead (*Agkistrodon contortrix*)<br>• Boa Constrictor (*Boa constrictor*)<br>• Ball Python (*Python regius*)<br>• Eastern Milk Snake (*Lampropeltis triangulum*)<br>• Green Tree Python (*Morelia viridis*) |
| **8. Sharks & Rays**<br>*(Chondrichthyes)* | 7 | **16** | • Tiger Shark (*Galeocerdo cuvier*)<br>• Bull Shark (*Carcharhinus leucas*)<br>• Shortfin Mako Shark (*Isurus oxyrinchus*)<br>• Thresher Shark (*Alopias vulpinus*)<br>• Basking Shark (*Cetorhinus maximus*)<br>• Greenland Shark (*Somniosus microcephalus*)<br>• Leopard Shark (*Triakis semifasciata*)<br>• Spotted Eagle Ray (*Aetobatus narinari*)<br>• Southern Stingray (*Hypanus americanus*) |
| **9. Cephalopods & Marine Mollusks**<br>*(Cephalopoda)* | 8 | **15** | • Mimic Octopus (*Thaumoctopus mimicus*)<br>• Dumbo Octopus (*Grimpoteuthis*)<br>• Humboldt Squid (*Dosidicus gigas*)<br>• Bigfin Reef Squid (*Sepioteuthis lessoniana*)<br>• Flamboyant Cuttlefish (*Metasepia pfefferi*)<br>• Striped Pyjama Squid (*Sepioloidea lineolata*) |
| **10. Primates**<br>*(Primates)* | 20 | **28** | • Hamadryas Baboon (*Papio hamadryas*)<br>• Olive Baboon (*Papio anubis*)<br>• White-faced Capuchin (*Cebus capucinus*)<br>• Cotton-top Tamarin (*Saguinus oedipus*)<br>• Ring-tailed Lemur (*Lemur catta*)<br>• Coquerel's Sifaka (*Propithecus coquereli*)<br>• Mouse Lemur (*Microcebus murinus*) |

---

## 4. Technical Ingestion Pipeline Architecture

```mermaid
graph TD
    A["iNaturalist & Wikidata APIs / Web Scrapers"] --> B["harvest_candidates.py<br>(Raw Candidate List)"]
    B --> C["Taxonomic & Common Name Validation<br>(NCBI Taxdump + Wikipedia Check)"]
    C --> D["Cluster Balancer & Filter<br>(Enforce 3-8 species per family)"]
    D --> E["LCA Node Grouping<br>(~350 Unique Ancestor Nodes)"]
    E --> F["TimeTree 5 Divergence Calibration<br>(Pairwise Median Times in MYA)"]
    F --> G["Shard Generation Engine<br>(Symmetric JSON Shards in /data/)"]
    G --> H["species_list.json & species_catalog.md Sync"]
```

### Step-by-Step Implementation Workflow:

1. **Candidate Harvester (`scripts/harvest_candidates.py`):**
   - Automatically hits iNaturalist and Wikipedia list pages.
   - Extracts formatted pairs: `Common Name (Genus species)`.
   - Filters by minimum Wikipedia article length and observation thresholds.

2. **Taxonomic Validator (`scripts/validate_candidates.py`):**
   - Resolves every scientific name against `NCBITaxa()`.
   - Verifies the organism is an accepted species (rejects subspecies or fossil-only extinct taxa unless explicitly curated).
   - Validates that a clean Wikipedia article exists with a valid thumbnail for tooltip preview.

3. **Cluster Balancer (`scripts/balance_clusters.py`):**
   - Checks the distribution across Orders and Families.
   - Flags any single-species "islands" and pulls sibling species from the same genus/family to reach minimum cluster depth.

4. **Tree Node Calibrator & Shard Generator (`scripts/build_shards.py`):**
   - Groups all species pairs by their Lowest Common Ancestor (LCA) node.
   - For any uncalibrated node, queries TimeTree API with reciprocal caching.
   - Generates all `.json` shard files with symmetrical divergence times:
     $$\text{Divergence}(A, B) \equiv \text{Divergence}(B, A)$$
   - Updates `data/species_list.json`, `data/time_cache.json`, and `species_catalog.md`.

---

## 5. Review & Sign-Off Checklist

Before running the batch ingestion pipeline, review and approve:
- [ ] **Cluster Targets:** Are the 10 selected groups balanced to your satisfaction?
- [ ] **Exclusions:** Are there specific groups you want excluded (e.g. plants, fungi, bacteria remain excluded to keep game strictly animal-focused)?
- [ ] **Target Pool Size:** Is 550–650 species the desired final database size?
- [ ] **Square Emoji Scheme:** Selection of preferred emoji square mapping for the share grid.

---
*Generated for Phylogenle development — Path: `/Users/amitjoshi2724/Desktop/phylogenle/SPECIES_EXPANSION_PLAN.md`*
