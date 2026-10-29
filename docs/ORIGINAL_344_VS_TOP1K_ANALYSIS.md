# 🧬 Analysis: Original 344 Species vs. Top 1,000 Vwiki Rankings

> **Analysis Date:** 2026-10-29  
> **Dataset:** `species_ranking_by_vwiki.csv` (empirical Wikimedia pageviews)  
> **Baseline:** 344 Original Untouched Organisms  

## 1. Executive Summary

### Comparison by Evaluation Mode:
- **Option 3 Gameplay Perspective (Live in Game):** **257 / 344 (74.7%)** in Top 1,000
- **Strict Species-Only Perspective:** **252 / 344 (73.3%)** in Top 1,000

### Option 3 Tier Distribution:
- **Inside Top 1,000 (🐾 Easy Tier):** **257 / 344 (74.7%)**
- **Inside Top 2,000 (🌿 Normal Tier):** **309 / 344 (89.8%)**
- **Inside Top 5,000 (🔬 Advanced Tier):** **339 / 344 (98.5%)**
- **Master Tier Only (> 5,000):** **5 / 344 (1.5%)**
- **Median Rank:** **#395**

## 2. Option 3 Recognizable Genuses Impact

The 7 iconic baseline organisms where the English Wikipedia article covers the Genus:

| Common Name | Species Binomial | Species Rank | Genus Taxon | Genus Rank | Rank Difference | Genus Views |
| :--- | :--- | :---: | :--- | :---: | :---: | :---: |
| **Gorilla** | *Gorilla gorilla* | #574 | *Gorilla* | **#26** | +548 | 2,145,135 |
| **Giraffe** | *Giraffa camelopardalis* | #1,888 | *Giraffa* | **#48** | +1,840 | 1,725,569 |
| **Orangutan** | *Pongo pygmaeus* | #554 | *Pongo* | **#61** | +493 | 1,532,594 |
| **Coelacanth** | *Latimeria chalumnae* | #1,704 | *Latimeria* | **#93** | +1,611 | 1,271,248 |
| **Chinchilla** | *Chinchilla lanigera* | #3,208 | *Chinchilla* | **#186** | +3,022 | 861,228 |
| **Baboon** | *Papio anubis* | #1,380 | *Papio* | **#245** | +1,135 | 708,763 |
| **Arapaima** | *Arapaima gigas* | #1,014 | *Arapaima* | **#289** | +725 | 603,950 |

## 3. Organisms Just Outside Top 1,000 (Ranks 1,001 – 2,000)

These organisms missed the 🐾 Easy (top 1k) cutoff, but comfortably qualify for the 🌿 Normal (top 2k) tier:

| Vwiki Rank | Off by (vs. 1k) | Common Name | Scientific Name | Cumulative Views | Sitelinks |
| :---: | :---: | :--- | :--- | :---: | :---: |
| #1,007 | +7 | Red Imported Fire Ant | *Solenopsis invicta* | 199,559 | 33 |
| #1,008 | +8 | Common Warthog | *Phacochoerus africanus* | 198,349 | 68 |
| #1,012 | +12 | Black Widow Spider | *Latrodectus mactans* | 196,342 | 41 |
| #1,015 | +15 | Thorny Devil | *Moloch horridus* | 196,169 | 49 |
| #1,022 | +22 | Wandering Albatross | *Diomedea exulans* | 194,315 | 52 |
| #1,047 | +47 | Fire Salamander | *Salamandra salamandra* | 188,642 | 72 |
| #1,055 | +55 | Hedgehog | *Erinaceus europaeus* | 187,961 | 83 |
| #1,060 | +60 | Common Octopus | *Octopus vulgaris* | 187,607 | 51 |
| #1,067 | +67 | Ringed Seal | *Pusa hispida* | 186,696 | 57 |
| #1,068 | +68 | California Quail | *Callipepla californica* | 186,693 | 33 |
| #1,084 | +84 | Brown Pelican | *Pelecanus occidentalis* | 183,520 | 60 |
| #1,096 | +96 | Sea Wasp Box Jellyfish | *Chironex fleckeri* | 180,983 | 44 |
| #1,125 | +125 | Golden Lion Tamarin | *Leontopithecus rosalia* | 175,767 | 47 |
| #1,135 | +135 | Ruby-throated Hummingbird | *Archilochus colubris* | 174,397 | 39 |
| #1,147 | +147 | Bottlenose Dolphin | *Tursiops truncatus* | 172,066 | 73 |
| #1,165 | +165 | Regal Blue Tang | *Paracanthurus hepatus* | 169,792 | 43 |
| #1,166 | +166 | Gelada | *Theropithecus gelada* | 169,779 | 58 |
| #1,168 | +168 | Goliath Frog | *Conraua goliath* | 169,552 | 49 |
| #1,180 | +180 | Siamang | *Symphalangus syndactylus* | 168,284 | 60 |
| #1,181 | +181 | Fiddler Crab | *Uca pugilator* | 168,137 | 34 |
| #1,186 | +186 | Red-eyed Tree Frog | *Agalychnis callidryas* | 167,689 | 48 |
| #1,203 | +203 | Philippine Tarsier | *Carlito syrichta* | 164,902 | 44 |
| #1,205 | +205 | Ocellaris Clownfish | *Amphiprion ocellaris* | 164,800 | 37 |
| #1,209 | +209 | Channel Catfish | *Ictalurus punctatus* | 163,970 | 29 |
| #1,211 | +211 | Harbor Porpoise | *Phocoena phocoena* | 163,789 | 61 |
| #1,226 | +226 | Common Toad | *Bufo bufo* | 162,821 | 71 |
| #1,234 | +234 | Seven-spot Ladybird | *Coccinella septempunctata* | 161,899 | 65 |
| #1,248 | +248 | Red-bellied Piranha | *Pygocentrus nattereri* | 159,724 | 38 |
| #1,254 | +254 | Bat | *Desmodus rotundus* | 158,845 | 43 |
| #1,255 | +255 | Atlantic Horseshoe Crab | *Limulus polyphemus* | 158,598 | 35 |
| #1,269 | +269 | Japanese Giant Salamander | *Andrias japonicus* | 155,937 | 43 |
| #1,285 | +285 | Emperor Scorpion | *Pandinus imperator* | 154,270 | 35 |
| #1,309 | +309 | Giant Tiger Prawn | *Penaeus monodon* | 151,890 | 35 |
| #1,339 | +339 | Little Brown Bat | *Myotis lucifugus* | 148,034 | 31 |
| #1,342 | +342 | Whooper Swan | *Cygnus cygnus* | 147,740 | 90 |
| #1,362 | +362 | Common Earthworm | *Lumbricus terrestris* | 145,441 | 53 |
| #1,465 | +465 | Hard Clam | *Mercenaria mercenaria* | 134,211 | 19 |
| #1,501 | +501 | Central Bearded Dragon | *Pogona vitticeps* | 130,875 | 41 |
| #1,528 | +528 | Chambered Nautilus | *Nautilus pompilius* | 128,352 | 27 |
| #1,530 | +530 | Common Frog | *Rana temporaria* | 128,107 | 61 |
| #1,552 | +552 | African Clawed Frog | *Xenopus laevis* | 126,647 | 39 |
| #1,582 | +582 | Roman Snail | *Helix pomatia* | 124,485 | 55 |
| #1,603 | +603 | Swallowtail Butterfly | *Papilio machaon* | 122,536 | 71 |
| #1,608 | +608 | White-handed Gibbon | *Hylobates lar* | 122,351 | 51 |
| #1,662 | +662 | Black-tailed Prairie Dog | *Cynomys ludovicianus* | 118,320 | 39 |
| #1,703 | +703 | Mole | *Talpa europaea* | 114,556 | 78 |
| #1,731 | +731 | Great Barracuda | *Sphyraena barracuda* | 113,177 | 40 |
| #1,761 | +761 | Buff-tailed Bumblebee | *Bombus terrestris* | 111,183 | 44 |
| #1,765 | +765 | European Stag Beetle | *Lucanus cervus* | 110,958 | 57 |
| #1,786 | +786 | Electric Eel | *Electrophorus electricus* | 108,571 | 74 |
| #1,806 | +806 | Common Wasp | *Vespula vulgaris* | 107,600 | 44 |
| #1,889 | +889 | Common Wombat | *Vombatus ursinus* | 101,608 | 48 |

## 4. Species in Advanced Tier (Ranks 2,001 – 5,000)

| Vwiki Rank | Off by (vs. 1k) | Common Name | Scientific Name | Cumulative Views | Sitelinks |
| :---: | :---: | :--- | :--- | :---: | :---: |
| #2,080 | +1,080 | Red Lionfish | *Pterois volitans* | 89,795 | 47 |
| #2,084 | +1,084 | Giant African Millipede | *Archispirostreptus gigas* | 89,656 | 22 |
| #2,089 | +1,089 | Common Cuttlefish | *Sepia officinalis* | 89,453 | 37 |
| #2,091 | +1,091 | Sloth | *Bradypus tridactylus* | 89,300 | 40 |
| #2,373 | +1,373 | Smooth Newt | *Lissotriton vulgaris* | 76,788 | 51 |
| #2,379 | +1,379 | Spider Monkey | *Ateles geoffroyi* | 76,636 | 44 |
| #2,406 | +1,406 | Giant Moray | *Gymnothorax javanicus* | 75,357 | 24 |
| #2,435 | +1,435 | Pacific Oyster | *Crassostrea gigas* | 74,154 | 32 |
| #2,584 | +1,584 | Mexican Redknee Tarantula | *Brachypelma hamorii* | 67,850 | 14 |
| #2,725 | +1,725 | Yellow Tube Sponge | *Aplysina fistularis* | 62,795 | 14 |
| #2,745 | +1,745 | Kiwi | *Apteryx mantelli* | 62,256 | 38 |
| #2,827 | +1,827 | Sea Walnut Comb Jelly | *Mnemiopsis leidyi* | 59,877 | 26 |
| #2,988 | +1,988 | Purple Sea Urchin | *Strongylocentrotus purpuratus* | 55,313 | 16 |
| #3,070 | +2,070 | Howler Monkey | *Alouatta palliata* | 53,292 | 33 |
| #3,109 | +2,109 | Periodical Cicada | *Magicicada septendecim* | 52,279 | 19 |
| #3,304 | +2,304 | Tree Kangaroo | *Dendrolagus matschiei* | 47,520 | 35 |
| #3,327 | +2,327 | Common Chameleon | *Chamaeleo chamaeleon* | 47,034 | 40 |
| #3,362 | +2,362 | Common Starfish | *Asterias rubens* | 46,275 | 31 |
| #3,371 | +2,371 | Emperor Dragonfly | *Anax imperator* | 46,106 | 47 |
| #3,418 | +2,418 | African Malaria Mosquito | *Anopheles gambiae* | 45,189 | 21 |
| #3,430 | +2,430 | Common Stingray | *Dasyatis pastinaca* | 45,032 | 38 |
| #3,583 | +2,583 | Slow Loris | *Nycticebus coucang* | 42,464 | 43 |
| #3,588 | +2,588 | Blue-ringed Octopus | *Hapalochlaena maculosa* | 42,263 | 24 |
| #3,809 | +2,809 | Dyeing Dart Frog | *Dendrobates tinctorius* | 38,183 | 32 |
| #3,887 | +2,887 | European Squid | *Loligo vulgaris* | 37,127 | 36 |
| #4,397 | +3,397 | Goliath Beetle | *Goliathus goliatus* | 30,041 | 17 |
| #4,406 | +3,406 | Estuary Seahorse | *Hippocampus kuda* | 29,995 | 25 |
| #4,596 | +3,596 | Green Spotted Puffer | *Tetraodon nigroviridis* | 27,802 | 22 |
| #4,770 | +3,770 | Leafcutter Ant | *Atta cephalotes* | 26,128 | 14 |
| #4,805 | +3,805 | Beadlet Anemone | *Actinia equina* | 25,787 | 31 |

## 5. Species in Master Tier Only (Ranks > 5,000)

These organisms represent specialized microscopic, deep-sea, or obscure biological lineages present in the original 344:

| Vwiki Rank | Off by (vs. 1k) | Common Name | Scientific Name | Cumulative Views | Sitelinks |
| :---: | :---: | :--- | :--- | :---: | :---: |
| #5,219 | +4,219 | Black Sea Cucumber | *Holothuria atra* | 22,616 | 15 |
| #5,479 | +4,479 | Grey Field Slug | *Deroceras reticulatum* | 20,908 | 22 |
| #7,211 | +6,211 | Freshwater Planarian | *Schmidtea mediterranea* | 12,816 | 11 |
| #7,367 | +6,367 | Water Bear Tardigrade | *Hypsibius exemplaris* | 12,277 | 13 |
| #17,321 | +16,321 | Caecilian | *Gymnopis multiplicata* | 2,826 | 17 |
