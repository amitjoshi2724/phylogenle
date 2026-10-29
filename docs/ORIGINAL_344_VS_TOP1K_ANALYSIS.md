# 🧬 Analysis: Original 344 Species vs. Top 1,000 Vwiki Rankings

> **Analysis Date:** 2026-10-29  
> **Dataset:** `species_ranking_by_vwiki.csv` (empirical Wikimedia pageviews)  
> **Baseline:** 344 Original Untouched Organisms  

## 1. Executive Summary

### Comparison by Evaluation Mode:
- **Option 3 Gameplay Perspective (Live in Game):** **266 / 344 (77.3%)** in Top 1,000
- **Strict Species-Only Perspective:** **249 / 344 (72.4%)** in Top 1,000

### Option 3 Tier Distribution:
- **Inside Top 1,000 (🐾 Easy Tier):** **266 / 344 (77.3%)**
- **Inside Top 2,000 (🌿 Normal Tier):** **316 / 344 (91.9%)**
- **Inside Top 5,000 (🔬 Advanced Tier):** **340 / 344 (98.8%)**
- **Master Tier Only (> 5,000):** **4 / 344 (1.2%)**
- **Median Rank:** **#385**

## 2. Option 3 Recognizable Taxa & Genuses Impact

The 40 iconic baseline organisms where the English Wikipedia article covers the Genus, Suborder, Family, or Order:

| Common Name | Taxonomic Level | Species Binomial | Species Rank | Option 3 Taxon | Taxon Rank | Rank Gain | Taxon Views |
| :--- | :--- | :--- | :---: | :--- | :---: | :---: | :---: |
| **Caecilian** | Order | *Gymnopis multiplicata* | #17,353 | *Gymnophiona* | **#587** | +16,766 | 348,203 |
| **Slow Loris** | Genus | *Nycticebus coucang* | #3,614 | *Nycticebus* | **#443** | +3,171 | 454,277 |
| **Chinchilla** | Genus | *Chinchilla lanigera* | #3,239 | *Chinchilla* | **#198** | +3,041 | 861,228 |
| **Kiwi** | Genus | *Apteryx mantelli* | #2,775 | *Apteryx* | **#115** | +2,660 | 1,178,121 |
| **Tree Kangaroo** | Genus | *Dendrolagus matschiei* | #3,335 | *Dendrolagus* | **#690** | +2,645 | 300,140 |
| **Howler Monkey** | Genus | *Alouatta palliata* | #3,101 | *Alouatta* | **#861** | +2,240 | 241,829 |
| **Sloth** | Suborder | *Bradypus tridactylus* | #2,118 | *Folivora* | **#123** | +1,995 | 1,142,165 |
| **Spider Monkey** | Genus | *Ateles geoffroyi* | #2,407 | *Ateles* | **#487** | +1,920 | 415,780 |
| **Giraffe** | Genus | *Giraffa camelopardalis* | #1,915 | *Giraffa* | **#52** | +1,863 | 1,725,569 |
| **Coelacanth** | Genus | *Latimeria chalumnae* | #1,731 | *Latimeria* | **#100** | +1,631 | 1,271,248 |
| **Mole** | Family | *Talpa europaea* | #1,730 | *Talpidae* | **#229** | +1,501 | 796,859 |
| **Gibbon** | Genus | *Hylobates lar* | #1,635 | *Hylobates* | **#296** | +1,339 | 620,243 |
| **Baboon** | Genus | *Papio anubis* | #1,407 | *Papio* | **#260** | +1,147 | 708,763 |
| **Hedgehog** | Subfamily | *Erinaceus europaeus* | #1,081 | *Erinaceinae* | **#113** | +968 | 1,198,254 |
| **Vampire Bat** | Genus | *Desmodus rotundus* | #1,281 | *Desmodus* | **#436** | +845 | 463,852 |
| **Arapaima** | Genus | *Arapaima gigas* | #1,039 | *Arapaima* | **#306** | +733 | 603,950 |
| **Porcupine** | Genus | *Erethizon dorsatum* | #892 | *Erethizon* | **#172** | +720 | 932,169 |
| **Manatee** | Genus | *Trichechus manatus* | #841 | *Trichechus* | **#134** | +707 | 1,092,463 |
| **Hare** | Genus | *Lepus europaeus* | #899 | *Lepus* | **#212** | +687 | 836,738 |
| **Bottlenose Dolphin** | Genus | *Tursiops truncatus* | #1,173 | *Tursiops* | **#521** | +652 | 385,941 |
| **Gorilla** | Genus | *Gorilla gorilla* | #597 | *Gorilla* | **#28** | +569 | 2,145,135 |
| **Seal** | Clade | *Phoca vitulina* | #633 | *Pinnipedia* | **#97** | +536 | 1,280,030 |
| **Orangutan** | Genus | *Pongo pygmaeus* | #576 | *Pongo* | **#65** | +511 | 1,532,594 |
| **Beaver** | Genus | *Castor canadensis* | #526 | *Castor* | **#84** | +442 | 1,368,835 |
| **Turkey** | Genus | *Meleagris gallopavo* | #396 | *Meleagris* | **#2** | +394 | 9,145,211 |
| **Opossum** | Family | *Didelphis virginiana* | #413 | *Didelphidae* | **#34** | +379 | 1,990,819 |
| **Rabbit** | Genus | *Oryctolagus cuniculus* | #383 | *Oryctolagus* | **#38** | +345 | 1,948,854 |
| **Elephant** | Family | *Loxodonta africana* | #252 | *Elephantidae* | **#15** | +237 | 2,715,467 |
| **Ostrich** | Genus | *Struthio camelus* | #367 | *Struthio* | **#206** | +161 | 853,421 |
| **Black Rhinoceros** | Genus | *Diceros bicornis* | #403 | *Diceros* | **#401** | +2 | 497,789 |
| **African Buffalo** | Genus | *Syncerus caffer* | #301 | *Syncerus* | **#299** | +2 | 612,682 |
| **King Cobra** | Genus | *Ophiophagus hannah* | #78 | *Ophiophagus* | **#77** | +1 | 1,425,097 |
| **Python** | Genus | *Python regius* | #343 | *Python* | **#1,047** | -704 | 194,740 |
| **Python** | Genus | *Python bivittatus* | #328 | *Python* | **#1,047** | -719 | 194,740 |
| **Rat** | Genus | *Rattus norvegicus* | #340 | *Rattus* | **#1,199** | -859 | 168,949 |
| **Tree Squirrel** | Genus | *Sciurus carolinensis* | #400 | *Sciurus* | **#2,218** | -1,818 | 84,432 |
| **Tree Squirrel** | Genus | *Sciurus vulgaris* | #218 | *Sciurus* | **#2,218** | -2,000 | 84,432 |
| **Mouse** | Genus | *Mus musculus* | #368 | *Mus* | **#2,448** | -2,080 | 74,881 |
| **River Otter** | Genus | *Lontra canadensis* | #501 | *Lontra* | **#2,696** | -2,195 | 64,770 |
| **Long-nosed Armadillo** | Genus | *Dasypus novemcinctus* | #743 | *Dasypus* | **#2,951** | -2,208 | 57,271 |

## 3. Organisms Just Outside Top 1,000 (Ranks 1,001 – 2,000)

These organisms missed the 🐾 Easy (top 1k) cutoff, but comfortably qualify for the 🌿 Normal (top 2k) tier:

| Vwiki Rank | Off by (vs. 1k) | Common Name | Scientific Name | Cumulative Views | Sitelinks |
| :---: | :---: | :--- | :--- | :---: | :---: |
| #1,015 | +15 | Greylag Goose | *Anser anser* | 204,049 | 106 |
| #1,019 | +19 | Eastern Grey Kangaroo | *Macropus giganteus* | 203,631 | 50 |
| #1,025 | +25 | Deep-sea Anglerfish | *Melanocetus johnsonii* | 201,797 | 29 |
| #1,032 | +32 | Red Imported Fire Ant | *Solenopsis invicta* | 199,559 | 33 |
| #1,033 | +33 | Common Warthog | *Phacochoerus africanus* | 198,349 | 68 |
| #1,037 | +37 | Black Widow Spider | *Latrodectus mactans* | 196,342 | 41 |
| #1,040 | +40 | Thorny Devil | *Moloch horridus* | 196,169 | 49 |
| #1,048 | +48 | Wandering Albatross | *Diomedea exulans* | 194,315 | 52 |
| #1,073 | +73 | Fire Salamander | *Salamandra salamandra* | 188,642 | 72 |
| #1,086 | +86 | Common Octopus | *Octopus vulgaris* | 187,607 | 51 |
| #1,093 | +93 | Ringed Seal | *Pusa hispida* | 186,696 | 57 |
| #1,094 | +94 | California Quail | *Callipepla californica* | 186,693 | 33 |
| #1,110 | +110 | Brown Pelican | *Pelecanus occidentalis* | 183,520 | 60 |
| #1,122 | +122 | Sea Wasp Box Jellyfish | *Chironex fleckeri* | 180,983 | 44 |
| #1,151 | +151 | Golden Lion Tamarin | *Leontopithecus rosalia* | 175,767 | 47 |
| #1,161 | +161 | Ruby-throated Hummingbird | *Archilochus colubris* | 174,397 | 39 |
| #1,191 | +191 | Regal Blue Tang | *Paracanthurus hepatus* | 169,792 | 43 |
| #1,192 | +192 | Gelada | *Theropithecus gelada* | 169,779 | 58 |
| #1,194 | +194 | Goliath Frog | *Conraua goliath* | 169,552 | 49 |
| #1,207 | +207 | Siamang | *Symphalangus syndactylus* | 168,284 | 60 |
| #1,208 | +208 | Fiddler Crab | *Uca pugilator* | 168,137 | 34 |
| #1,213 | +213 | Red-eyed Tree Frog | *Agalychnis callidryas* | 167,689 | 48 |
| #1,230 | +230 | Philippine Tarsier | *Carlito syrichta* | 164,902 | 44 |
| #1,232 | +232 | Ocellaris Clownfish | *Amphiprion ocellaris* | 164,800 | 37 |
| #1,236 | +236 | Channel Catfish | *Ictalurus punctatus* | 163,970 | 29 |
| #1,238 | +238 | Harbor Porpoise | *Phocoena phocoena* | 163,789 | 61 |
| #1,253 | +253 | Common Toad | *Bufo bufo* | 162,821 | 71 |
| #1,261 | +261 | Seven-spot Ladybird | *Coccinella septempunctata* | 161,899 | 65 |
| #1,275 | +275 | Red-bellied Piranha | *Pygocentrus nattereri* | 159,724 | 38 |
| #1,282 | +282 | Atlantic Horseshoe Crab | *Limulus polyphemus* | 158,598 | 35 |
| #1,296 | +296 | Japanese Giant Salamander | *Andrias japonicus* | 155,937 | 43 |
| #1,312 | +312 | Emperor Scorpion | *Pandinus imperator* | 154,270 | 35 |
| #1,336 | +336 | Giant Tiger Prawn | *Penaeus monodon* | 151,890 | 35 |
| #1,366 | +366 | Little Brown Bat | *Myotis lucifugus* | 148,034 | 31 |
| #1,369 | +369 | Whooper Swan | *Cygnus cygnus* | 147,740 | 90 |
| #1,389 | +389 | Common Earthworm | *Lumbricus terrestris* | 145,441 | 53 |
| #1,492 | +492 | Hard Clam | *Mercenaria mercenaria* | 134,211 | 19 |
| #1,528 | +528 | Central Bearded Dragon | *Pogona vitticeps* | 130,875 | 41 |
| #1,555 | +555 | Chambered Nautilus | *Nautilus pompilius* | 128,352 | 27 |
| #1,557 | +557 | Common Frog | *Rana temporaria* | 128,107 | 61 |
| #1,579 | +579 | African Clawed Frog | *Xenopus laevis* | 126,647 | 39 |
| #1,609 | +609 | Roman Snail | *Helix pomatia* | 124,485 | 55 |
| #1,630 | +630 | Swallowtail Butterfly | *Papilio machaon* | 122,536 | 71 |
| #1,689 | +689 | Black-tailed Prairie Dog | *Cynomys ludovicianus* | 118,320 | 39 |
| #1,758 | +758 | Great Barracuda | *Sphyraena barracuda* | 113,177 | 40 |
| #1,788 | +788 | Buff-tailed Bumblebee | *Bombus terrestris* | 111,183 | 44 |
| #1,792 | +792 | European Stag Beetle | *Lucanus cervus* | 110,958 | 57 |
| #1,813 | +813 | Electric Eel | *Electrophorus electricus* | 108,571 | 74 |
| #1,833 | +833 | Common Wasp | *Vespula vulgaris* | 107,600 | 44 |
| #1,916 | +916 | Common Wombat | *Vombatus ursinus* | 101,608 | 48 |

## 4. Species in Advanced Tier (Ranks 2,001 – 5,000)

| Vwiki Rank | Off by (vs. 1k) | Common Name | Scientific Name | Cumulative Views | Sitelinks |
| :---: | :---: | :--- | :--- | :---: | :---: |
| #2,107 | +1,107 | Red Lionfish | *Pterois volitans* | 89,795 | 47 |
| #2,111 | +1,111 | Giant African Millipede | *Archispirostreptus gigas* | 89,656 | 22 |
| #2,116 | +1,116 | Common Cuttlefish | *Sepia officinalis* | 89,453 | 37 |
| #2,401 | +1,401 | Smooth Newt | *Lissotriton vulgaris* | 76,788 | 51 |
| #2,434 | +1,434 | Giant Moray | *Gymnothorax javanicus* | 75,357 | 24 |
| #2,464 | +1,464 | Pacific Oyster | *Crassostrea gigas* | 74,154 | 32 |
| #2,613 | +1,613 | Mexican Redknee Tarantula | *Brachypelma hamorii* | 67,850 | 14 |
| #2,755 | +1,755 | Yellow Tube Sponge | *Aplysina fistularis* | 62,795 | 14 |
| #2,857 | +1,857 | Sea Walnut Comb Jelly | *Mnemiopsis leidyi* | 59,877 | 26 |
| #3,019 | +2,019 | Purple Sea Urchin | *Strongylocentrotus purpuratus* | 55,313 | 16 |
| #3,140 | +2,140 | Periodical Cicada | *Magicicada septendecim* | 52,279 | 19 |
| #3,358 | +2,358 | Common Chameleon | *Chamaeleo chamaeleon* | 47,034 | 40 |
| #3,393 | +2,393 | Common Starfish | *Asterias rubens* | 46,275 | 31 |
| #3,402 | +2,402 | Emperor Dragonfly | *Anax imperator* | 46,106 | 47 |
| #3,449 | +2,449 | African Malaria Mosquito | *Anopheles gambiae* | 45,189 | 21 |
| #3,461 | +2,461 | Common Stingray | *Dasyatis pastinaca* | 45,032 | 38 |
| #3,619 | +2,619 | Blue-ringed Octopus | *Hapalochlaena maculosa* | 42,263 | 24 |
| #3,840 | +2,840 | Dyeing Dart Frog | *Dendrobates tinctorius* | 38,183 | 32 |
| #3,918 | +2,918 | European Squid | *Loligo vulgaris* | 37,127 | 36 |
| #4,428 | +3,428 | Goliath Beetle | *Goliathus goliatus* | 30,041 | 17 |
| #4,437 | +3,437 | Estuary Seahorse | *Hippocampus kuda* | 29,995 | 25 |
| #4,627 | +3,627 | Green Spotted Puffer | *Tetraodon nigroviridis* | 27,802 | 22 |
| #4,801 | +3,801 | Leafcutter Ant | *Atta cephalotes* | 26,128 | 14 |
| #4,836 | +3,836 | Beadlet Anemone | *Actinia equina* | 25,787 | 31 |

## 5. Species in Master Tier Only (Ranks > 5,000)

These organisms represent specialized microscopic, deep-sea, or obscure biological lineages present in the original 344:

| Vwiki Rank | Off by (vs. 1k) | Common Name | Scientific Name | Cumulative Views | Sitelinks |
| :---: | :---: | :--- | :--- | :---: | :---: |
| #5,250 | +4,250 | Black Sea Cucumber | *Holothuria atra* | 22,616 | 15 |
| #5,511 | +4,511 | Grey Field Slug | *Deroceras reticulatum* | 20,908 | 22 |
| #7,243 | +6,243 | Freshwater Planarian | *Schmidtea mediterranea* | 12,816 | 11 |
| #7,399 | +6,399 | Water Bear Tardigrade | *Hypsibius exemplaris* | 12,277 | 13 |
