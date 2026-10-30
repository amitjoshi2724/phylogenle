# 🧬 Comprehensive Audit: Collapsed Biological Taxa in Baseline 344

> **Audit Date:** 2026-10-30  
> **Status:** Persistent Audit Artifact (`docs/AUDIT_COLLAPSED_ORGANISMS.json`)  
> **Total Discrepancies Audited:** **21 organisms**  

## 1. Executive Summary

This audit identifies every instance in the baseline 344 species list where an iconic umbrella animal name (e.g., *Fiddler Crab*, *Barn Owl*, *Electric Eel*, *Black Widow Spider*, *Leafcutter Ant*) was arbitrarily collapsed onto a single species binomial, preventing the broader animal group from being recognized properly.

## 2. Complete Itemized Audit Table

| Baseline Entry | Specific Binomial | Restored Distinct Common Name | Umbrella Common Name | Umbrella Scientific | Rank | Wikipedia Article | Views |
| :--- | :--- | :--- | :--- | :--- | :---: | :--- | :---: |
| **Fiddler Crab (Uca pugilator)** | *Uca pugilator* | **Atlantic Sand Fiddler Crab** | **Fiddler Crab** | *Ocypodidae* | family | `Fiddler_crab` | 168,626 |
| **Barn Owl (Tyto alba)** | *Tyto alba* | **Western Barn Owl** | **Barn Owl** | *Tyto* | genus | `Barn_owl` | 387,592 |
| **Electric Eel (Electrophorus electricus)** | *Electrophorus electricus* | **Greater Electric Eel** | **Electric Eel** | *Electrophorus* | genus | `Electric_eel` | 629,695 |
| **Leafcutter Ant (Atta cephalotes)** | *Atta cephalotes* | **Cephalotes Leafcutter Ant** | **Leafcutter Ant** | *Atta* | genus | `Leafcutter_ant` | 200,569 |
| **Goliath Beetle (Goliathus goliatus)** | *Goliathus goliatus* | **Royal Goliath Beetle** | **Goliath Beetle** | *Goliathus* | genus | `Goliathus` | 111,366 |
| **Black Widow Spider (Latrodectus mactans)** | *Latrodectus mactans* | **Southern Black Widow** | **Black Widow Spider** | *Latrodectus* | genus | `Latrodectus` | 935,454 |
| **California Sea Lion (Zalophus californianus)** | *Zalophus californianus* | **California Sea Lion** | **Sea Lion** | *Otariinae* | subfamily | `Sea_lion` | 912,072 |
| **Sea Walnut Comb Jelly (Mnemiopsis leidyi)** | *Mnemiopsis leidyi* | **Sea Walnut** | **Comb Jelly** | *Ctenophora* | phylum | `Ctenophora` | 482,694 |
| **Green Spotted Puffer (Tetraodon nigroviridis)** | *Tetraodon nigroviridis* | **Green Spotted Puffer** | **Pufferfish** | *Tetraodontidae* | family | `Tetraodontidae` | 542,342 |
| **Central Bearded Dragon (Pogona vitticeps)** | *Pogona vitticeps* | **Central Bearded Dragon** | **Bearded Dragon** | *Pogona* | genus | `Pogona` | 400,123 |
| **African Clawed Frog (Xenopus laevis)** | *Xenopus laevis* | **African Clawed Frog** | **Clawed Frog** | *Xenopus* | genus | `Xenopus` | 72,234 |
| **Macaque (Macaca mulatta)** | *Macaca mulatta* | **Rhesus Macaque** | **Macaque** | *Macaca* | genus | `Macaque` | 598,859 |
| **Lynx (Lynx lynx)** | *Lynx lynx* | **Eurasian Lynx** | **Lynx** | *Lynx* | genus | `Lynx` | 1,131,565 |
| **Panda (Ailuropoda melanoleuca)** | *Ailuropoda melanoleuca* | **Giant Panda** | **Giant Panda** | *Ailuropoda* | genus | `Giant_panda` | 2,542,645 |
| **Raccoon (Procyon lotor)** | *Procyon lotor* | **Common Raccoon** | **Raccoon** | *Procyon* | genus | `Raccoon` | 2,270,162 |
| **Hyena (Crocuta crocuta)** | *Crocuta crocuta* | **Spotted Hyena** | **Hyena** | *Hyaenidae* | family | `Hyena` | 1,480,798 |
| **Hippopotamus (Hippopotamus amphibius)** | *Hippopotamus amphibius* | **Common Hippopotamus** | **Hippopotamus** | *Hippopotamidae* | family | `Hippopotamus` | 1,780,359 |
| **Kangaroo (Macropus rufus)** | *Macropus rufus* | **Red Kangaroo** | **Kangaroo** | *Macropus* | genus | `Kangaroo` | 2,124,308 |
| **Seven-spot Ladybird (Coccinella septempunctata)** | *Coccinella septempunctata* | **Seven-spot Ladybird** | **Ladybird** | *Coccinellidae* | family | `Coccinellidae` | 976,980 |
| **Wandering Albatross (Diomedea exulans)** | *Diomedea exulans* | **Wandering Albatross** | **Albatross** | *Diomedeidae* | family | `Albatross` | 924,227 |
| **Giant Clam (Tridacna gigas)** | *Tridacna gigas* | **Giant Clam** | **Giant Clam** | *Tridacna* | genus | `Giant_clam` | 216,856 |

## 3. Detailed Per-Organism Diagnostic Rationale

### 1. Fiddler Crab (Uca pugilator)
- **Specific Species:** *Uca pugilator* $\rightarrow$ **Atlantic Sand Fiddler Crab**
- **True Umbrella Taxon:** Family *Ocypodidae* (Fiddler Crab)
- **Wikipedia Endpoint:** `Fiddler_crab` (168,626 views)
- **Diagnostic Rationale:** Uca pugilator is strictly the Atlantic sand fiddler crab. Calling it 'Fiddler Crab' collapsed all ~100 fiddler crab species in family Ocypodidae onto one species.

### 2. Barn Owl (Tyto alba)
- **Specific Species:** *Tyto alba* $\rightarrow$ **Western Barn Owl**
- **True Umbrella Taxon:** Genus *Tyto* (Barn Owl)
- **Wikipedia Endpoint:** `Barn_owl` (387,592 views)
- **Diagnostic Rationale:** Tyto alba is specifically the Western barn owl. Calling it 'Barn Owl' collapsed genus Tyto (18 owl species) into this single binomial.

### 3. Electric Eel (Electrophorus electricus)
- **Specific Species:** *Electrophorus electricus* $\rightarrow$ **Greater Electric Eel**
- **True Umbrella Taxon:** Genus *Electrophorus* (Electric Eel)
- **Wikipedia Endpoint:** `Electric_eel` (629,695 views)
- **Diagnostic Rationale:** Electrophorus electricus is one of 3 distinct electric eel species (alongside E. voltai and E. varii). Genus Electrophorus holds 630k pageviews.

### 4. Leafcutter Ant (Atta cephalotes)
- **Specific Species:** *Atta cephalotes* $\rightarrow$ **Cephalotes Leafcutter Ant**
- **True Umbrella Taxon:** Genus *Atta* (Leafcutter Ant)
- **Wikipedia Endpoint:** `Leafcutter_ant` (200,569 views)
- **Diagnostic Rationale:** Atta cephalotes is just one species of leafcutter ant. The broad group 'Leafcutter Ant' spans genera Atta and Acromyrmex (47 species).

### 5. Goliath Beetle (Goliathus goliatus)
- **Specific Species:** *Goliathus goliatus* $\rightarrow$ **Royal Goliath Beetle**
- **True Umbrella Taxon:** Genus *Goliathus* (Goliath Beetle)
- **Wikipedia Endpoint:** `Goliathus` (111,366 views)
- **Diagnostic Rationale:** Goliathus goliatus is specifically the royal goliath beetle. Genus Goliathus contains 5 massive beetle species.

### 6. Black Widow Spider (Latrodectus mactans)
- **Specific Species:** *Latrodectus mactans* $\rightarrow$ **Southern Black Widow**
- **True Umbrella Taxon:** Genus *Latrodectus* (Black Widow Spider)
- **Wikipedia Endpoint:** `Latrodectus` (935,454 views)
- **Diagnostic Rationale:** Latrodectus mactans is the southern black widow. The worldwide 'Black widow spider' article covers genus Latrodectus (34 species, 935k views).

### 7. California Sea Lion (Zalophus californianus)
- **Specific Species:** *Zalophus californianus* $\rightarrow$ **California Sea Lion**
- **True Umbrella Taxon:** Subfamily *Otariinae* (Sea Lion)
- **Wikipedia Endpoint:** `Sea_lion` (912,072 views)
- **Diagnostic Rationale:** Zalophus californianus is specifically the California sea lion. The general animal concept 'Sea Lion' (subfamily Otariinae) has 912k views.

### 8. Sea Walnut Comb Jelly (Mnemiopsis leidyi)
- **Specific Species:** *Mnemiopsis leidyi* $\rightarrow$ **Sea Walnut**
- **True Umbrella Taxon:** Phylum *Ctenophora* (Comb Jelly)
- **Wikipedia Endpoint:** `Ctenophora` (482,694 views)
- **Diagnostic Rationale:** Mnemiopsis leidyi is specifically the sea walnut / warty comb jelly. 'Comb Jelly' is the entire phylum Ctenophora (483k views).

### 9. Green Spotted Puffer (Tetraodon nigroviridis)
- **Specific Species:** *Tetraodon nigroviridis* $\rightarrow$ **Green Spotted Puffer**
- **True Umbrella Taxon:** Family *Tetraodontidae* (Pufferfish)
- **Wikipedia Endpoint:** `Tetraodontidae` (542,342 views)
- **Diagnostic Rationale:** Tetraodon nigroviridis is specifically the green spotted puffer. 'Pufferfish' is the worldwide family Tetraodontidae (542k views).

### 10. Central Bearded Dragon (Pogona vitticeps)
- **Specific Species:** *Pogona vitticeps* $\rightarrow$ **Central Bearded Dragon**
- **True Umbrella Taxon:** Genus *Pogona* (Bearded Dragon)
- **Wikipedia Endpoint:** `Pogona` (400,123 views)
- **Diagnostic Rationale:** Pogona vitticeps is the central bearded dragon. Genus Pogona covers all 6 bearded dragon species (400k views).

### 11. African Clawed Frog (Xenopus laevis)
- **Specific Species:** *Xenopus laevis* $\rightarrow$ **African Clawed Frog**
- **True Umbrella Taxon:** Genus *Xenopus* (Clawed Frog)
- **Wikipedia Endpoint:** `Xenopus` (72,234 views)
- **Diagnostic Rationale:** Xenopus laevis is the African clawed frog. Genus Xenopus represents all clawed frogs.

### 12. Macaque (Macaca mulatta)
- **Specific Species:** *Macaca mulatta* $\rightarrow$ **Rhesus Macaque**
- **True Umbrella Taxon:** Genus *Macaca* (Macaque)
- **Wikipedia Endpoint:** `Macaque` (598,859 views)
- **Diagnostic Rationale:** Macaca mulatta is specifically the rhesus macaque. Genus Macaca encompasses 23 species (599k views).

### 13. Lynx (Lynx lynx)
- **Specific Species:** *Lynx lynx* $\rightarrow$ **Eurasian Lynx**
- **True Umbrella Taxon:** Genus *Lynx* (Lynx)
- **Wikipedia Endpoint:** `Lynx` (1,131,565 views)
- **Diagnostic Rationale:** Lynx lynx is specifically the Eurasian lynx. Genus Lynx encompasses all 4 lynx species (1.13M views).

### 14. Panda (Ailuropoda melanoleuca)
- **Specific Species:** *Ailuropoda melanoleuca* $\rightarrow$ **Giant Panda**
- **True Umbrella Taxon:** Genus *Ailuropoda* (Giant Panda)
- **Wikipedia Endpoint:** `Giant_panda` (2,542,645 views)
- **Diagnostic Rationale:** Ailuropoda melanoleuca was called 'Panda', conflicting with Red Panda (Ailurus fulgens). Restores Giant Panda and genus Ailuropoda.

### 15. Raccoon (Procyon lotor)
- **Specific Species:** *Procyon lotor* $\rightarrow$ **Common Raccoon**
- **True Umbrella Taxon:** Genus *Procyon* (Raccoon)
- **Wikipedia Endpoint:** `Raccoon` (2,270,162 views)
- **Diagnostic Rationale:** Procyon lotor is specifically the North American / common raccoon. Genus Procyon represents all 3 raccoon species (2.27M views).

### 16. Hyena (Crocuta crocuta)
- **Specific Species:** *Crocuta crocuta* $\rightarrow$ **Spotted Hyena**
- **True Umbrella Taxon:** Family *Hyaenidae* (Hyena)
- **Wikipedia Endpoint:** `Hyena` (1,480,798 views)
- **Diagnostic Rationale:** Crocuta crocuta is the spotted hyena. Family Hyaenidae represents all 4 hyena species (1.48M views).

### 17. Hippopotamus (Hippopotamus amphibius)
- **Specific Species:** *Hippopotamus amphibius* $\rightarrow$ **Common Hippopotamus**
- **True Umbrella Taxon:** Family *Hippopotamidae* (Hippopotamus)
- **Wikipedia Endpoint:** `Hippopotamus` (1,780,359 views)
- **Diagnostic Rationale:** Hippopotamus amphibius is the common hippopotamus. Family Hippopotamidae covers both common and pygmy hippos (1.78M views).

### 18. Kangaroo (Macropus rufus)
- **Specific Species:** *Macropus rufus* $\rightarrow$ **Red Kangaroo**
- **True Umbrella Taxon:** Genus *Macropus* (Kangaroo)
- **Wikipedia Endpoint:** `Kangaroo` (2,124,308 views)
- **Diagnostic Rationale:** Macropus rufus is specifically the red kangaroo. Genus Macropus / Kangaroo already exists as umbrella; species name must be Red Kangaroo.

### 19. Seven-spot Ladybird (Coccinella septempunctata)
- **Specific Species:** *Coccinella septempunctata* $\rightarrow$ **Seven-spot Ladybird**
- **True Umbrella Taxon:** Family *Coccinellidae* (Ladybird)
- **Wikipedia Endpoint:** `Coccinellidae` (976,980 views)
- **Diagnostic Rationale:** Coccinella septempunctata is the seven-spot ladybird. Family Coccinellidae represents all ladybirds / ladybugs (977k views).

### 20. Wandering Albatross (Diomedea exulans)
- **Specific Species:** *Diomedea exulans* $\rightarrow$ **Wandering Albatross**
- **True Umbrella Taxon:** Family *Diomedeidae* (Albatross)
- **Wikipedia Endpoint:** `Albatross` (924,227 views)
- **Diagnostic Rationale:** Diomedea exulans is the wandering albatross. Family Diomedeidae represents all 22 albatross species (924k views).

### 21. Giant Clam (Tridacna gigas)
- **Specific Species:** *Tridacna gigas* $\rightarrow$ **Giant Clam**
- **True Umbrella Taxon:** Genus *Tridacna* (Giant Clam)
- **Wikipedia Endpoint:** `Giant_clam` (216,856 views)
- **Diagnostic Rationale:** Tridacna gigas is the largest giant clam. Genus Tridacna represents all 12 giant clam species.

