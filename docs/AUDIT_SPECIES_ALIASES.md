# 🧬 Comprehensive Audit & Registry: Species Aliases Coverage

> **Audit Date:** 2026-10-31  
> **Total Catalog Species:** 29,564  
> **Total Verified Non-Primary Aliases in Registry:** 9,801  

## 1. Executive Summary & Coverage Metrics

| Metric | Value |
| :--- | :---: |
| **Total Verified Aliases (`species_aliases.json`)** | **9,801** |
| **Species with Verified Aliases (Catalog-Wide)** | **4,599 (15.6%)** |
| **Top 1,000 Species with Aliases (🐾 Easy Tier)** | **742 / 1,000 (74.2%)** |
| **Dangling Alias Targets (Not in `species_list.json`)** | **0** |
| **Primary-Name Shadowing Collisions** | **0** |

## 2. Key Spotlight Organisms & Verified Harvested Aliases

| Organism | Scientific Name | Verified Harvested Aliases |
| :--- | :--- | :--- |
| **Bobcat** | *Lynx rufus* | Bay Lynx; Bob Cats; Felis Rufus; North American Wildcat; Red Lynx |
| **Lion** | *Panthera leo* | Abyssinian Lion; African Lion; Asiatic Lion; Central African Lion; Ceylon Lion; Congo Lion; East-Central African Lion; Ethiopian Lion |
| **American Black Bear** | *Ursus americanus* | Black Bear; California Black Bear; Cinnamon Bear; Eastern Black Bear; Euarctos Americanus; Kenai Black Bear; Kermode Bear; New Mexico Black Bear |
| **Wolf** | *Canis lupus* | Arctic Wolf; Gray Wolf; Grey Wolf; Timber Wolf; Tundra Wolf |
| **Capybara** | *Hydrochoerus hydrochaeris* | Carpincho; Chiguire; Greater Capybara; True Capybara; Water Hog |
| **Portuguese Man O' War** | *Physalia physalis* | Bluebottle; Floating Terror; Man O' War; Man-Of-War; Portuguese Battleship; Portuguese Man O' War; Portuguese Man Of War |
| **American Bison** | *Bison bison* | American Buffalo; Bison; Bos Bison; Buffalo; Buffalo Trails; North American Bison; Plains Bison; Plains Buffalo |
| **Wolverine** | *Gulo gulo* | Beaver Eater; Carcajou; Glutton; Quickhatch; Skunk Bear |
| **Platypus** | *Ornithorhynchus anatinus* | Duck-Billed Platypus; Duckbill; Duckbill Platypus; Duckmole; Watermole |
| **Giant Panda** | *Ailuropoda melanoleuca* | Black Panda; Coon Bear; Giant Panda Bear; Great Panda; Greater Panda; Panda Bear; Parti-Coloured Bear |

## 3. Downstream Gameplay & CSV Synchronization

1. **Live Autocomplete (`script.js`):**
   - Typing any of the harvested aliases (e.g. `red lynx`, `bay lynx`, `north american wildcat`) immediately resolves to `Bobcat (Lynx rufus)`.
2. **Guess Submission Engine:**
   - Submitting a regional or alternate name matches `speciesAliases[guess.toLowerCase()]` and scores full credit.
3. **Ranking CSVs (`docs/species_ranking_by_vwiki.csv`):**
   - The `Alternative Names / Aliases` column is compiled from `data/species_aliases.json` via Step 4 of `rank_species_popularity.py`.
