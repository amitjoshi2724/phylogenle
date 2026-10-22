# 🧬 Phylogenle: Comprehensive Biodiversity Expansion Architecture & Blueprint

**Document Version:** 2.0 (Unbounded Maximum Harvesting Edition)  
**Target Database Expansion:** 344 ➔ **1,000+ Fully Calibrated Species**  
**Core Directive:** **NO UPPER BOUND ON CLUSTER SIZE.** Grab *every* recognizable, valid organism available from authoritative biodiversity sources. Eliminate artificial caps and capture the full breadth of animal diversity so players can explore deep phylogenetic branches without hitting dead ends.

---

## 1. Core Principles: Comprehensive Depth, Zero Artificial Ceilings

### Why Previous Limits Were Removed
- **No Upper Bound:** Previous drafts suggested 3–8 species per cluster. This has been completely eliminated. If a family or genus has 15, 25, or 40 recognizable species (e.g., hummingbirds, butterflies, sharks, raptors, cetaceans, canids, wild cats), **we ingest every single one of them**.
- **Minimum Cluster Threshold ($\ge 3$):** While there is no maximum, every family or genus must have at least 3 species to eliminate solitary "island species" where a player deduces a family but has no sister species to guess.
- **Cultural & Educational Recognition Filter:** Every candidate must be a recognizable wild or domesticated animal with an established common name, supported by iNaturalist research-grade observation frequency and English Wikipedia pageviews. No unpronounceable micro-nematodes or microscopic mites.
- **100% Cladistic & Temporal Integrity:** Every single species is cross-referenced with local NCBI Taxonomy (`NCBITaxa()`) and peer-reviewed TimeTree 5 divergence times.

---

## 2. Shifted 8-Tier Taxonomic Color & Square Emoji System

As requested, the rank colors and share squares have been shifted to an intuitive, high-contrast spectrum using solid square emojis:

```
[EXACT / HOT]                                                                        [DISTANT / COLD]
🟩 Species  ➔  🟨 Genus  ➔  🟧 Family  ➔  🟥 Order  ➔  🟪 Class  ➔  🟦 Phylum  ➔  🟫 Kingdom  ➔  ⬛ Nothing
 (0 MYA)       (~5 MYA)     (~30 MYA)     (~80 MYA)    (~310 MYA)    (~550 MYA)    (~680 MYA)     (Out of Tree)
```

| Rank / Closeness | Square Emoji | Color Name | Hex Accent | Meaning |
| :--- | :---: | :--- | :--- | :--- |
| **Species (Exact)** | `🟩` | Emerald Green | `#10b981` | Direct match! You deduced the secret organism (0 MYA). |
| **Genus** | `🟨` | Golden Yellow | `#eab308` | Direct sister species in the same genus (~2–10 MYA). |
| **Family** | `🟧` | Vibrant Orange | `#f97316` | Same family (e.g., Felidae, Canidae, Trochilidae) (~15–35 MYA). |
| **Order** | `🟥` | Crimson Red | `#ef4444` | Same order (e.g., Carnivora, Primates, Lepidoptera) (~60–90 MYA). |
| **Class** | `🟪` | Royal Purple | `#a855f7` | Same class (e.g., Mammals, Birds, Reptiles, Insects) (~150–320 MYA). |
| **Phylum** | `🟦` | Sapphire Blue | `#3b82f6` | Same phylum (e.g., Chordates, Arthropods, Mollusks) (~520–580 MYA). |
| **Kingdom** | `🟫` | Earth Brown | `#8b5cf6` / `#854d0e` | Animalia root (shared common ancestor >650 MYA). |
| **Nothing Match** | `⬛` | Jet Black | `#1e293b` | Complete miss / unrelated / out-of-tree organism. |

### Incorporating the White Square (`⬜`)
The Unicode standard provides the **White Large Square (`⬜`)**. Here are the three most natural, powerful ways to incorporate it into Phylogenle:

1. **Option A: The Surrender / "Gave Up" Flag in the Share Grid (Recommended):**
   - In Wordle, winning lines end in `🟩`. In Phylogenle, if a player gives up and reveals the organism, the share sequence ends with a **White Square (`⬜`)** representing waving the white surrender flag!
   - Solved in 4: `🟦🟥🟧🟩` (Victory!)
   - Gave up on 4th guess: `🟦🟥🟧🟫⬜` (Revealed!)
2. **Option B: Domain (Eukaryota / Universal Life Root):**
   - Above Kingdom (`🟫`) sits Domain (`⬜` Eukaryota >1000 MYA), while `⬛` is absolute zero relation.
3. **Option C: Empty / Unused Attempt Slots:**
   - If playing in standard daily view, unused guess slots render as `⬜` tiles.

---

## 3. Authoritative Scraping Sources: Maximizing Pool to 1,000+

Rather than manual guessing, an automated multi-threaded harvester will ingest from 5 global sources:

### A. iNaturalist Research-Grade API (`api.inaturalist.org/v1/observations/species_counts`)
- **Query:** Top 5,000 research-grade observed species globally across Aves, Mammalia, Reptilia, Amphibia, Actinopterygii, Chondrichthyes, Insecta, Arachnida, Malacostraca, and Cephalopoda.
- **Why:** Real wild observations by millions of naturalists ensure only recognizable, living, real-world species enter the dictionary.

### B. Wikidata SPARQL Knowledge Graph (`query.wikidata.org`)
- **Query:** All animal taxa (`wdt:P31 wd:Q16521` in `wdt:P171* wd:Q729`) with over 20 Wikipedia language sitelinks.
- **Why:** Filters out obscure academic citations and selects culturally prominent animals with rich English Wikipedia articles for in-game hover cards.

### C. IUCN Red List Global Species API (`apiv3.iucnredlist.org`)
- **Query:** All Critically Endangered, Endangered, and Vulnerable mammals, birds, reptiles, and sharks.
- **Why:** Captures famous global conservation icons (e.g., Axolotl, Pangolin, Vaquita, Kakapo, Mountain Gorilla, Gharial).

### D. Comprehensive Wikipedia Clade Tables
- Systematic extraction of complete clade tables:
  - Complete list of Hummingbirds (*Trochilidae* — all 30+ famous species)
  - Complete list of Swallowtails, Monarchs, and Silk Moths (*Papilionidae, Nymphalidae, Saturniidae*)
  - Complete list of Birds of Prey, Owls, and Falcons (*Accipitriformes, Strigiformes, Falconiformes*)
  - Complete list of Whales, Dolphins, and Porpoises (*Cetacea*)
  - Complete list of Sharks and Rays (*Selachimorpha, Batoidea*)
  - Complete list of Wild Canids, Felids, Bears, and Mustelids (*Carnivora*)

---

## 4. Unbounded Deep-Dive Clade Targets

| Clade | Current Pool | Target Pool | Comprehensive Harvesting Scope |
| :--- | :---: | :---: | :--- |
| **Mammalia** | 148 | **~350+** | All Primates (apes, baboons, lemurs, tamarins, marmosets), all Carnivora (cats, dogs, bears, seals, otters, weasels, hyenas, civets), all Cetaceans (baleen whales, toothed whales, dolphins, porpoises), all Ungulates (deer, antelopes, cattle, horses, rhinos, tapirs), all Marsupials (kangaroos, wallabies, possums, bandicoots, quolls). |
| **Aves (Birds)** | 57 | **~250+** | All Hummingbirds, all Birds of Prey (eagles, hawks, harriers, kites), all Owls (horned, barn, screech, snowy), all Waterfowl (ducks, geese, swans), all Parrots (macaws, cockatoos, lories, parakeets), all Seabirds (albatrosses, petrels, puffins, penguins), all Ratites (ostrich, emu, rhea, kiwi, cassowary), Corvid songbirds. |
| **Reptiles** | 32 | **~120+** | All venomous snakes (cobras, mambas, vipers, rattlesnakes, taipans, kraits), all constrictors (anacondas, boas, pythons), all crocodilians (crocodiles, alligators, caimans, gharials), all sea turtles and tortoises, monitor lizards, chameleons, geckos, iguanas. |
| **Fishes** | 33 | **~130+** | All major Sharks (Great White, Tiger, Bull, Hammerheads, Mako, Thresher, Basking, Whale, Greenland, Nurse, Leopard), all major Rays and Skates, pelagic game fish (tunas, billfish, marlins, swordfish), reef fish (angelfish, clownfish, tangs, butterflyfish), deep sea oddities (anglerfish, gulper eel, coelacanth). |
| **Invertebrates** | 58 | **~150+** | Cephalopods (all octopuses, squids, cuttlefish, nautilus), Crustaceans (crabs, lobsters, shrimp, mantis shrimp), Insects (butterflies, moths, beetles, ants, bees, wasps, dragonflies, praying mantises), Arachnids (tarantulas, true spiders, scorpions), Cnidarians (jellyfish, anemones, corals), Echinoderms. |
| **Amphibians** | 16 | **~50+** | Poison dart frogs, tree frogs, true toads, bullfrogs, glass frogs, axolotls, newts, giant salamanders, fire salamanders, hellbenders, caecilians. |
| **TOTAL POOL** | **344** | **1,000+** | **Comprehensive, fully interconnected phylogenetic web.** |

---

## 5. Automated Execution Pipeline

1. **`scripts/harvest_all.py`**: Automated async scraping of iNaturalist + Wikidata + Wikipedia.
2. **`scripts/filter_validate.py`**: Validation through `ete3.NCBITaxa()` ensuring exact TaxID matches and active Wikipedia summaries.
3. **`scripts/generate_all_shards.py`**: Automated node-level LCA grouping with TimeTree 5 calibration. Generates all symmetric pairwise JSON shards in `/data/` in seconds.
4. **`scripts/update_catalog.py`**: Auto-generates updated `species_list.json` and human-readable `species_catalog.md`.

---
*Blueprint approved for execution in Phylogenle codebase — Saved at: `/Users/amitjoshi2724/Desktop/phylogenle/SPECIES_EXPANSION_PLAN.md`*
