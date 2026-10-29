# 🧬 Comprehensive Algorithmic Audit: Original 344 Baseline Discrepancies

> **Audit Methodology:** 100% algorithmic audit of all 344 original baseline organisms against live MediaWiki and Wikimedia REST APIs.  
> **Organisms Audited:** 344 / 344  
> **Discrepancies Identified:** **33 organisms** in the 344 baseline suffer from this taxonomic/vernacular mismatch.  

## 1. Complete List of All Detected Discrepancies

Every organism below represents an instance where the 344 baseline used a common name or iconic animal concept, but assigned a single binomial whose specific article receives only a fraction of the topic's true Wikipedia viewership:

| Common Name | Baseline Binomial | Current Article | Current Views | True Concept Article | True Topic Views | Missing Pageviews | Ratio |
| :--- | :--- | :--- | :---: | :--- | :---: | :---: | :---: |
| **Burrowing Owl** | *Athene cunicularia* | `Burrowing owl` | 329,233 | **[`Athena`](https://en.wikipedia.org/wiki/Athena)** | **2,735,980** | **+2,406,747** | 8.3x |
| **Elephant** | *Loxodonta africana* | `African bush elephant` | 729,583 | **[`Elephant`](https://en.wikipedia.org/wiki/Elephant)** | **2,715,467** | **+1,985,884** | 3.7x |
| **Thorny Devil** | *Moloch horridus* | `Thorny devil` | 196,169 | **[`Moloch`](https://en.wikipedia.org/wiki/Moloch)** | **2,005,210** | **+1,809,041** | 10.2x |
| **Gorilla** | *Gorilla gorilla* | `Western gorilla` | 341,207 | **[`Gorilla`](https://en.wikipedia.org/wiki/Gorilla)** | **2,147,386** | **+1,806,179** | 6.3x |
| **Opossum** | *Didelphis virginiana* | `Virginia opossum` | 483,569 | **[`Opossum`](https://en.wikipedia.org/wiki/Opossum)** | **1,990,819** | **+1,507,250** | 4.1x |
| **Kiwi** | *Apteryx mantelli* | `North Island brown kiwi` | 62,256 | **[`Kiwi (bird)`](https://en.wikipedia.org/wiki/Kiwi_%28bird%29)** | **1,178,121** | **+1,115,865** | 18.9x |
| **Sloth** | *Bradypus tridactylus* | `Pale-throated sloth` | 44,650 | **[`Sloth`](https://en.wikipedia.org/wiki/Sloth)** | **1,142,165** | **+1,097,515** | 25.6x |
| **Rat** | *Rattus norvegicus* | `Brown rat` | 561,222 | **[`Rat`](https://en.wikipedia.org/wiki/Rat)** | **1,586,823** | **+1,025,601** | 2.8x |
| **Hedgehog** | *Erinaceus europaeus* | `European hedgehog` | 187,961 | **[`Hedgehog`](https://en.wikipedia.org/wiki/Hedgehog)** | **1,198,254** | **+1,010,293** | 6.4x |
| **Seal** | *Phoca vitulina* | `Harbor seal` | 327,638 | **[`Pinniped`](https://en.wikipedia.org/wiki/Pinniped)** | **1,280,030** | **+952,392** | 3.9x |
| **Buff-tailed Bumblebee** | *Bombus terrestris* | `Bombus terrestris` | 111,183 | **[`Bumblebee`](https://en.wikipedia.org/wiki/Bumblebee)** | **1,057,674** | **+946,491** | 9.5x |
| **Chambered Nautilus** | *Nautilus pompilius* | `Chambered nautilus` | 128,352 | **[`Nautilus`](https://en.wikipedia.org/wiki/Nautilus)** | **858,051** | **+729,699** | 6.7x |
| **Porcupine** | *Erethizon dorsatum* | `North American porcupine` | 234,572 | **[`Porcupine`](https://en.wikipedia.org/wiki/Porcupine)** | **932,169** | **+697,597** | 4.0x |
| **Red Lionfish** | *Pterois volitans* | `Red lionfish` | 89,795 | **[`Lionfish`](https://en.wikipedia.org/wiki/Lionfish)** | **741,145** | **+651,350** | 8.3x |
| **Great Barracuda** | *Sphyraena barracuda* | `Great barracuda` | 113,177 | **[`Barracuda`](https://en.wikipedia.org/wiki/Barracuda)** | **733,646** | **+620,469** | 6.5x |
| **Baboon** | *Papio anubis* | `Olive baboon` | 143,616 | **[`Baboon`](https://en.wikipedia.org/wiki/Baboon)** | **708,763** | **+565,147** | 4.9x |
| **Black-tailed Prairie Dog** | *Cynomys ludovicianus* | `Black-tailed prairie dog` | 118,320 | **[`Prairie dog`](https://en.wikipedia.org/wiki/Prairie_dog)** | **663,084** | **+544,764** | 5.6x |
| **Electric Eel** | *Electrophorus electricus* | `Electrophorus electricus` | 108,571 | **[`Electric eel`](https://en.wikipedia.org/wiki/Electric_eel)** | **628,719** | **+520,148** | 5.8x |
| **Ocellaris Clownfish** | *Amphiprion ocellaris* | `Ocellaris clownfish` | 164,800 | **[`Clownfish`](https://en.wikipedia.org/wiki/Clownfish)** | **632,287** | **+467,487** | 3.8x |
| **Slow Loris** | *Nycticebus coucang* | `Sunda slow loris` | 42,464 | **[`Slow loris`](https://en.wikipedia.org/wiki/Slow_loris)** | **454,277** | **+411,813** | 10.7x |
| **Arapaima** | *Arapaima gigas* | `Arapaima gigas` | 196,262 | **[`Arapaima`](https://en.wikipedia.org/wiki/Arapaima)** | **603,950** | **+407,688** | 3.1x |
| **Turkey** | *Meleagris gallopavo* | `Wild turkey` | 500,756 | **[`Turkey (bird)`](https://en.wikipedia.org/wiki/Turkey_%28bird%29)** | **855,369** | **+354,613** | 1.7x |
| **Caecilian** | *Gymnopis multiplicata* | `Gymnopis multiplicata` | 2,826 | **[`Caecilian`](https://en.wikipedia.org/wiki/Caecilian)** | **348,203** | **+345,377** | 123.2x |
| **Spider Monkey** | *Ateles geoffroyi* | `Geoffroy's spider monkey` | 76,636 | **[`Spider monkey`](https://en.wikipedia.org/wiki/Spider_monkey)** | **415,780** | **+339,144** | 5.4x |
| **Green Iguana** | *Iguana iguana* | `Green iguana` | 310,036 | **[`Iguana`](https://en.wikipedia.org/wiki/Iguana)** | **583,908** | **+273,872** | 1.9x |
| **Central Bearded Dragon** | *Pogona vitticeps* | `Central bearded dragon` | 130,875 | **[`Pogona`](https://en.wikipedia.org/wiki/Pogona)** | **399,679** | **+268,804** | 3.1x |
| **Tree Kangaroo** | *Dendrolagus matschiei* | `Matschie's tree-kangaroo` | 47,520 | **[`Tree-kangaroo`](https://en.wikipedia.org/wiki/Tree-kangaroo)** | **300,140** | **+252,620** | 6.3x |
| **Periodical Cicada** | *Magicicada septendecim* | `Magicicada septendecim` | 52,279 | **[`Periodical cicadas`](https://en.wikipedia.org/wiki/Periodical_cicadas)** | **256,266** | **+203,987** | 4.9x |
| **African Malaria Mosquito** | *Anopheles gambiae* | `Anopheles gambiae` | 45,189 | **[`Anopheles`](https://en.wikipedia.org/wiki/Anopheles)** | **243,388** | **+198,199** | 5.4x |
| **Howler Monkey** | *Alouatta palliata* | `Mantled howler` | 53,292 | **[`Howler monkey`](https://en.wikipedia.org/wiki/Howler_monkey)** | **241,829** | **+188,537** | 4.5x |
| **Leafcutter Ant** | *Atta cephalotes* | `Atta cephalotes` | 26,128 | **[`Leafcutter ant`](https://en.wikipedia.org/wiki/Leafcutter_ant)** | **200,304** | **+174,176** | 7.7x |
| **Roman Snail** | *Helix pomatia* | `Helix pomatia` | 124,485 | **[`Helix`](https://en.wikipedia.org/wiki/Helix)** | **255,406** | **+130,921** | 2.1x |
| **Eastern Box Turtle** | *Terrapene carolina* | `Common box turtle` | 84,245 | **[`Eastern box turtle`](https://en.wikipedia.org/wiki/Eastern_box_turtle)** | **174,912** | **+90,667** | 2.1x |

## 2. Genus-Level Articles (8 organisms)

These organisms have dedicated Wikipedia articles at the **Genus** level that represent the entire animal group:

- **Thorny Devil** (Genus *Moloch*): Article [`Moloch`](https://en.wikipedia.org/wiki/Moloch) has **2,005,210 views** vs `196,169` on *Moloch horridus* (+1,809,041 missing views)
- **Gorilla** (Genus *Gorilla*): Article [`Gorilla`](https://en.wikipedia.org/wiki/Gorilla) has **2,147,386 views** vs `341,207` on *Gorilla gorilla* (+1,806,179 missing views)
- **Chambered Nautilus** (Genus *Nautilus*): Article [`Nautilus`](https://en.wikipedia.org/wiki/Nautilus) has **858,051 views** vs `128,352` on *Nautilus pompilius* (+729,699 missing views)
- **Arapaima** (Genus *Arapaima*): Article [`Arapaima`](https://en.wikipedia.org/wiki/Arapaima) has **603,950 views** vs `196,262` on *Arapaima gigas* (+407,688 missing views)
- **Green Iguana** (Genus *Iguana*): Article [`Iguana`](https://en.wikipedia.org/wiki/Iguana) has **583,908 views** vs `310,036` on *Iguana iguana* (+273,872 missing views)
- **Central Bearded Dragon** (Genus *Pogona*): Article [`Pogona`](https://en.wikipedia.org/wiki/Pogona) has **399,679 views** vs `130,875` on *Pogona vitticeps* (+268,804 missing views)
- **African Malaria Mosquito** (Genus *Anopheles*): Article [`Anopheles`](https://en.wikipedia.org/wiki/Anopheles) has **243,388 views** vs `45,189` on *Anopheles gambiae* (+198,199 missing views)
- **Roman Snail** (Genus *Helix*): Article [`Helix`](https://en.wikipedia.org/wiki/Helix) has **255,406 views** vs `124,485` on *Helix pomatia* (+130,921 missing views)

## 3. Higher Taxon / Vernacular Concept Articles (25 organisms)

These organisms represent broad vernacular groups, families, or suborders on Wikipedia:

- **Burrowing Owl**: Article [`Athena`](https://en.wikipedia.org/wiki/Athena) has **2,735,980 views** vs `329,233` on *Athene cunicularia* (+2,406,747 missing views)
- **Elephant**: Article [`Elephant`](https://en.wikipedia.org/wiki/Elephant) has **2,715,467 views** vs `729,583` on *Loxodonta africana* (+1,985,884 missing views)
- **Opossum**: Article [`Opossum`](https://en.wikipedia.org/wiki/Opossum) has **1,990,819 views** vs `483,569` on *Didelphis virginiana* (+1,507,250 missing views)
- **Kiwi**: Article [`Kiwi (bird)`](https://en.wikipedia.org/wiki/Kiwi_%28bird%29) has **1,178,121 views** vs `62,256` on *Apteryx mantelli* (+1,115,865 missing views)
- **Sloth**: Article [`Sloth`](https://en.wikipedia.org/wiki/Sloth) has **1,142,165 views** vs `44,650` on *Bradypus tridactylus* (+1,097,515 missing views)
- **Rat**: Article [`Rat`](https://en.wikipedia.org/wiki/Rat) has **1,586,823 views** vs `561,222` on *Rattus norvegicus* (+1,025,601 missing views)
- **Hedgehog**: Article [`Hedgehog`](https://en.wikipedia.org/wiki/Hedgehog) has **1,198,254 views** vs `187,961` on *Erinaceus europaeus* (+1,010,293 missing views)
- **Seal**: Article [`Pinniped`](https://en.wikipedia.org/wiki/Pinniped) has **1,280,030 views** vs `327,638` on *Phoca vitulina* (+952,392 missing views)
- **Buff-tailed Bumblebee**: Article [`Bumblebee`](https://en.wikipedia.org/wiki/Bumblebee) has **1,057,674 views** vs `111,183` on *Bombus terrestris* (+946,491 missing views)
- **Porcupine**: Article [`Porcupine`](https://en.wikipedia.org/wiki/Porcupine) has **932,169 views** vs `234,572` on *Erethizon dorsatum* (+697,597 missing views)
- **Red Lionfish**: Article [`Lionfish`](https://en.wikipedia.org/wiki/Lionfish) has **741,145 views** vs `89,795` on *Pterois volitans* (+651,350 missing views)
- **Great Barracuda**: Article [`Barracuda`](https://en.wikipedia.org/wiki/Barracuda) has **733,646 views** vs `113,177` on *Sphyraena barracuda* (+620,469 missing views)
- **Baboon**: Article [`Baboon`](https://en.wikipedia.org/wiki/Baboon) has **708,763 views** vs `143,616` on *Papio anubis* (+565,147 missing views)
- **Black-tailed Prairie Dog**: Article [`Prairie dog`](https://en.wikipedia.org/wiki/Prairie_dog) has **663,084 views** vs `118,320` on *Cynomys ludovicianus* (+544,764 missing views)
- **Electric Eel**: Article [`Electric eel`](https://en.wikipedia.org/wiki/Electric_eel) has **628,719 views** vs `108,571` on *Electrophorus electricus* (+520,148 missing views)
- **Ocellaris Clownfish**: Article [`Clownfish`](https://en.wikipedia.org/wiki/Clownfish) has **632,287 views** vs `164,800` on *Amphiprion ocellaris* (+467,487 missing views)
- **Slow Loris**: Article [`Slow loris`](https://en.wikipedia.org/wiki/Slow_loris) has **454,277 views** vs `42,464` on *Nycticebus coucang* (+411,813 missing views)
- **Turkey**: Article [`Turkey (bird)`](https://en.wikipedia.org/wiki/Turkey_%28bird%29) has **855,369 views** vs `500,756` on *Meleagris gallopavo* (+354,613 missing views)
- **Caecilian**: Article [`Caecilian`](https://en.wikipedia.org/wiki/Caecilian) has **348,203 views** vs `2,826` on *Gymnopis multiplicata* (+345,377 missing views)
- **Spider Monkey**: Article [`Spider monkey`](https://en.wikipedia.org/wiki/Spider_monkey) has **415,780 views** vs `76,636` on *Ateles geoffroyi* (+339,144 missing views)
- **Tree Kangaroo**: Article [`Tree-kangaroo`](https://en.wikipedia.org/wiki/Tree-kangaroo) has **300,140 views** vs `47,520` on *Dendrolagus matschiei* (+252,620 missing views)
- **Periodical Cicada**: Article [`Periodical cicadas`](https://en.wikipedia.org/wiki/Periodical_cicadas) has **256,266 views** vs `52,279` on *Magicicada septendecim* (+203,987 missing views)
- **Howler Monkey**: Article [`Howler monkey`](https://en.wikipedia.org/wiki/Howler_monkey) has **241,829 views** vs `53,292` on *Alouatta palliata* (+188,537 missing views)
- **Leafcutter Ant**: Article [`Leafcutter ant`](https://en.wikipedia.org/wiki/Leafcutter_ant) has **200,304 views** vs `26,128` on *Atta cephalotes* (+174,176 missing views)
- **Eastern Box Turtle**: Article [`Eastern box turtle`](https://en.wikipedia.org/wiki/Eastern_box_turtle) has **174,912 views** vs `84,245` on *Terrapene carolina* (+90,667 missing views)
