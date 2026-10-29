# 🧬 Analysis: Original 344 Species vs. Top 1,000 Vwiki Rankings

> **Analysis Date:** 2026-10-29  
> **Dataset:** `species_ranking_by_vwiki.csv` (empirical Wikimedia pageviews)  
> **Baseline:** 344 Original Untouched Organisms  

## 1. Executive Summary

### Comparison by Evaluation Mode:
- **Option 3 Gameplay Perspective (Live in Game):** **291 / 344 (84.6%)** in Top 1,000
- **Strict Species-Only Perspective:** **245 / 344 (71.2%)** in Top 1,000

### Option 3 Tier Distribution:
- **Inside Top 1,000 (🐾 Easy Tier):** **291 / 344 (84.6%)**
- **Inside Top 2,000 (🌿 Normal Tier):** **332 / 344 (96.5%)**
- **Inside Top 5,000 (🔬 Advanced Tier):** **344 / 344 (100.0%)**
- **Master Tier Only (> 5,000):** **0 / 344 (0.0%)**
- **Median Rank:** **#331**

## 2. Option 3 Recognizable Taxa & Genuses Impact

The 69 iconic baseline organisms where the English Wikipedia article covers the Genus, Suborder, Family, or Order:

| Common Name | Taxonomic Level | Species Binomial | Species Rank | Option 3 Taxon | Taxon Rank | Rank Gain | Taxon Views |
| :--- | :--- | :--- | :---: | :--- | :---: | :---: | :---: |
| **Caecilian** | Order | *Gymnopis multiplicata* | #17,382 | *Gymnophiona* | **#613** | +16,769 | 348,203 |
| **Tardigrade** | Phylum | *Hypsibius exemplaris* | #7,428 | *Tardigrada* | **#26** | +7,402 | 2,247,127 |
| **Planarian** | Order | *Schmidtea mediterranea* | #7,272 | *Tricladida* | **#774** | +6,498 | 274,316 |
| **Slug** | Family | *Deroceras reticulatum* | #5,540 | *Agriolimacidae* | **#430** | +5,110 | 492,072 |
| **Sea Cucumber** | Class | *Holothuria atra* | #5,279 | *Holothuroidea* | **#309** | +4,970 | 635,717 |
| **Sea Anemone** | Order | *Actinia equina* | #4,865 | *Actiniaria* | **#350** | +4,515 | 570,737 |
| **Seahorse** | Genus | *Hippocampus kuda* | #4,466 | *Hippocampus* | **#201** | +4,265 | 880,481 |
| **Squid** | Class | *Loligo vulgaris* | #3,947 | *Decapodiformes* | **#253** | +3,694 | 768,194 |
| **Dragonfly** | Order | *Anax imperator* | #3,431 | *Anisoptera* | **#150** | +3,281 | 1,048,873 |
| **Stingray** | Order | *Dasyatis pastinaca* | #3,490 | *Myliobatiformes* | **#249** | +3,241 | 779,248 |
| **Starfish** | Class | *Asterias rubens* | #3,422 | *Asteroidea* | **#240** | +3,182 | 801,295 |
| **Slow Loris** | Genus | *Nycticebus coucang* | #3,643 | *Nycticebus* | **#467** | +3,176 | 454,277 |
| **Chameleon** | Family | *Chamaeleo chamaeleon* | #3,387 | *Chamaeleonidae* | **#229** | +3,158 | 819,924 |
| **Chinchilla** | Genus | *Chinchilla lanigera* | #3,268 | *Chinchilla* | **#209** | +3,059 | 861,228 |
| **Sea Urchin** | Class | *Strongylocentrotus purpuratus* | #3,048 | *Echinoidea* | **#215** | +2,833 | 858,627 |
| **Kiwi** | Genus | *Apteryx mantelli* | #2,804 | *Apteryx* | **#118** | +2,686 | 1,178,121 |
| **Tree Kangaroo** | Genus | *Dendrolagus matschiei* | #3,364 | *Dendrolagus* | **#717** | +2,647 | 300,140 |
| **Sponge** | Phylum | *Aplysina fistularis* | #2,784 | *Porifera* | **#237** | +2,547 | 806,240 |
| **Howler Monkey** | Genus | *Alouatta palliata* | #3,130 | *Alouatta* | **#890** | +2,240 | 241,829 |
| **Oyster** | Family | *Crassostrea gigas* | #2,493 | *Ostreidae* | **#272** | +2,221 | 722,272 |
| **Sloth** | Suborder | *Bradypus tridactylus* | #2,147 | *Folivora* | **#126** | +2,021 | 1,142,165 |
| **Cuttlefish** | Order | *Sepia officinalis* | #2,145 | *Sepiida* | **#165** | +1,980 | 982,814 |
| **Spider Monkey** | Genus | *Ateles geoffroyi* | #2,436 | *Ateles* | **#513** | +1,923 | 415,780 |
| **Giraffe** | Genus | *Giraffa camelopardalis* | #1,944 | *Giraffa* | **#55** | +1,889 | 1,725,569 |
| **Millipede** | Class | *Archispirostreptus gigas* | #2,140 | *Diplopoda* | **#324** | +1,816 | 609,716 |
| **Bumblebee** | Genus | *Bombus terrestris* | #1,817 | *Bombus* | **#146** | +1,671 | 1,057,674 |
| **Wasp** | Family | *Vespula vulgaris* | #1,862 | *Vespidae* | **#198** | +1,664 | 886,747 |
| **Coelacanth** | Genus | *Latimeria chalumnae* | #1,760 | *Latimeria* | **#103** | +1,657 | 1,271,248 |
| **Frog** | Order | *Rana temporaria* | #1,586 | *Anura* | **#34** | +1,552 | 2,048,190 |
| **Mole** | Family | *Talpa europaea* | #1,759 | *Talpidae* | **#244** | +1,515 | 796,859 |
| **Snail** | Class | *Helix pomatia* | #1,638 | *Gastropoda* | **#288** | +1,350 | 680,730 |
| **Gibbon** | Genus | *Hylobates lar* | #1,664 | *Hylobates* | **#317** | +1,347 | 620,243 |
| **Scorpion** | Order | *Pandinus imperator* | #1,341 | *Scorpiones* | **#129** | +1,212 | 1,128,831 |
| **Baboon** | Genus | *Papio anubis* | #1,436 | *Papio* | **#278** | +1,158 | 708,763 |
| **Earthworm** | Order | *Lumbricus terrestris* | #1,418 | *Lumbricina* | **#314** | +1,104 | 625,973 |
| **Stag Beetle** | Family | *Lucanus cervus* | #1,821 | *Lucanidae* | **#723** | +1,098 | 297,542 |
| **Octopus** | Order | *Octopus vulgaris* | #1,115 | *Octopoda* | **#46** | +1,069 | 1,825,040 |
| **Clam** | Class | *Mercenaria mercenaria* | #1,521 | *Bivalvia* | **#504** | +1,017 | 423,910 |
| **Hedgehog** | Subfamily | *Erinaceus europaeus* | #1,110 | *Erinaceinae* | **#116** | +994 | 1,198,254 |
| **Mantis** | Order | *Mantis religiosa* | #1,027 | *Mantodea* | **#141** | +886 | 1,068,871 |
| **Prawn** | Order | *Penaeus monodon* | #1,365 | *Dendrobranchiata* | **#505** | +860 | 423,794 |
| **Vampire Bat** | Genus | *Desmodus rotundus* | #1,310 | *Desmodus* | **#460** | +850 | 463,852 |
| **Lobster** | Family | *Homarus americanus* | #1,029 | *Nephropidae* | **#196** | +833 | 894,673 |
| **Porcupine** | Genus | *Erethizon dorsatum* | #921 | *Erethizon* | **#180** | +741 | 932,169 |
| **Arapaima** | Genus | *Arapaima gigas* | #1,068 | *Arapaima* | **#328** | +740 | 603,950 |
| **Manatee** | Genus | *Trichechus manatus* | #870 | *Trichechus* | **#138** | +732 | 1,092,463 |
| **Hare** | Genus | *Lepus europaeus* | #928 | *Lepus* | **#224** | +704 | 836,738 |
| **Bottlenose Dolphin** | Genus | *Tursiops truncatus* | #1,202 | *Tursiops* | **#547** | +655 | 385,941 |
| **Toad** | Family | *Bufo bufo* | #1,282 | *Bufonidae* | **#641** | +641 | 334,481 |
| **Gorilla** | Genus | *Gorilla gorilla* | #623 | *Gorilla* | **#29** | +594 | 2,145,135 |
| **Seal** | Clade | *Phoca vitulina* | #660 | *Pinnipedia* | **#100** | +560 | 1,280,030 |
| **Orangutan** | Genus | *Pongo pygmaeus* | #602 | *Pongo* | **#68** | +534 | 1,532,594 |
| **Beaver** | Genus | *Castor canadensis* | #552 | *Castor* | **#87** | +465 | 1,368,835 |
| **Turkey** | Genus | *Meleagris gallopavo* | #419 | *Meleagris* | **#2** | +417 | 9,145,211 |
| **Opossum** | Family | *Didelphis virginiana* | #437 | *Didelphidae* | **#36** | +401 | 1,990,819 |
| **Rabbit** | Genus | *Oryctolagus cuniculus* | #406 | *Oryctolagus* | **#40** | +366 | 1,948,854 |
| **Elephant** | Family | *Loxodonta africana* | #269 | *Elephantidae* | **#15** | +254 | 2,715,467 |
| **Ostrich** | Genus | *Struthio camelus* | #390 | *Struthio* | **#218** | +172 | 853,421 |
| **Black Rhinoceros** | Genus | *Diceros bicornis* | #426 | *Diceros* | **#424** | +2 | 497,789 |
| **African Buffalo** | Genus | *Syncerus caffer* | #322 | *Syncerus* | **#320** | +2 | 612,682 |
| **King Cobra** | Genus | *Ophiophagus hannah* | #81 | *Ophiophagus* | **#80** | +1 | 1,425,097 |
| **Python** | Genus | *Python regius* | #366 | *Python* | **#1,076** | -710 | 194,740 |
| **Python** | Genus | *Python bivittatus* | #351 | *Python* | **#1,076** | -725 | 194,740 |
| **Rat** | Genus | *Rattus norvegicus* | #363 | *Rattus* | **#1,228** | -865 | 168,949 |
| **Tree Squirrel** | Genus | *Sciurus carolinensis* | #423 | *Sciurus* | **#2,247** | -1,824 | 84,432 |
| **Tree Squirrel** | Genus | *Sciurus vulgaris* | #231 | *Sciurus* | **#2,247** | -2,016 | 84,432 |
| **Mouse** | Genus | *Mus musculus* | #391 | *Mus* | **#2,477** | -2,086 | 74,881 |
| **River Otter** | Genus | *Lontra canadensis* | #527 | *Lontra* | **#2,725** | -2,198 | 64,770 |
| **Long-nosed Armadillo** | Genus | *Dasypus novemcinctus* | #771 | *Dasypus* | **#2,980** | -2,209 | 57,271 |

## 3. Organisms Just Outside Top 1,000 (Ranks 1,001 – 2,000)

These organisms missed the 🐾 Easy (top 1k) cutoff, but comfortably qualify for the 🌿 Normal (top 2k) tier:

| Vwiki Rank | Off by (vs. 1k) | Common Name | Scientific Name | Cumulative Views | Sitelinks |
| :---: | :---: | :--- | :--- | :---: | :---: |
| #1,003 | +3 | Great Cormorant | *Phalacrocorax carbo* | 213,252 | 108 |
| #1,015 | +15 | Peacock Mantis Shrimp | *Odontodactylus scyllarus* | 210,926 | 32 |
| #1,044 | +44 | Greylag Goose | *Anser anser* | 204,049 | 106 |
| #1,048 | +48 | Eastern Grey Kangaroo | *Macropus giganteus* | 203,631 | 50 |
| #1,054 | +54 | Deep-sea Anglerfish | *Melanocetus johnsonii* | 201,797 | 29 |
| #1,061 | +61 | Red Imported Fire Ant | *Solenopsis invicta* | 199,559 | 33 |
| #1,062 | +62 | Common Warthog | *Phacochoerus africanus* | 198,349 | 68 |
| #1,066 | +66 | Black Widow Spider | *Latrodectus mactans* | 196,342 | 41 |
| #1,069 | +69 | Thorny Devil | *Moloch horridus* | 196,169 | 49 |
| #1,077 | +77 | Wandering Albatross | *Diomedea exulans* | 194,315 | 52 |
| #1,102 | +102 | Fire Salamander | *Salamandra salamandra* | 188,642 | 72 |
| #1,122 | +122 | Ringed Seal | *Pusa hispida* | 186,696 | 57 |
| #1,123 | +123 | California Quail | *Callipepla californica* | 186,693 | 33 |
| #1,139 | +139 | Brown Pelican | *Pelecanus occidentalis* | 183,520 | 60 |
| #1,151 | +151 | Sea Wasp Box Jellyfish | *Chironex fleckeri* | 180,983 | 44 |
| #1,180 | +180 | Golden Lion Tamarin | *Leontopithecus rosalia* | 175,767 | 47 |
| #1,190 | +190 | Ruby-throated Hummingbird | *Archilochus colubris* | 174,397 | 39 |
| #1,220 | +220 | Regal Blue Tang | *Paracanthurus hepatus* | 169,792 | 43 |
| #1,221 | +221 | Gelada | *Theropithecus gelada* | 169,779 | 58 |
| #1,223 | +223 | Goliath Frog | *Conraua goliath* | 169,552 | 49 |
| #1,236 | +236 | Siamang | *Symphalangus syndactylus* | 168,284 | 60 |
| #1,237 | +237 | Fiddler Crab | *Uca pugilator* | 168,137 | 34 |
| #1,242 | +242 | Red-eyed Tree Frog | *Agalychnis callidryas* | 167,689 | 48 |
| #1,259 | +259 | Philippine Tarsier | *Carlito syrichta* | 164,902 | 44 |
| #1,261 | +261 | Ocellaris Clownfish | *Amphiprion ocellaris* | 164,800 | 37 |
| #1,265 | +265 | Channel Catfish | *Ictalurus punctatus* | 163,970 | 29 |
| #1,267 | +267 | Harbor Porpoise | *Phocoena phocoena* | 163,789 | 61 |
| #1,290 | +290 | Seven-spot Ladybird | *Coccinella septempunctata* | 161,899 | 65 |
| #1,304 | +304 | Red-bellied Piranha | *Pygocentrus nattereri* | 159,724 | 38 |
| #1,311 | +311 | Atlantic Horseshoe Crab | *Limulus polyphemus* | 158,598 | 35 |
| #1,325 | +325 | Japanese Giant Salamander | *Andrias japonicus* | 155,937 | 43 |
| #1,395 | +395 | Little Brown Bat | *Myotis lucifugus* | 148,034 | 31 |
| #1,398 | +398 | Whooper Swan | *Cygnus cygnus* | 147,740 | 90 |
| #1,557 | +557 | Central Bearded Dragon | *Pogona vitticeps* | 130,875 | 41 |
| #1,584 | +584 | Chambered Nautilus | *Nautilus pompilius* | 128,352 | 27 |
| #1,608 | +608 | African Clawed Frog | *Xenopus laevis* | 126,647 | 39 |
| #1,659 | +659 | Swallowtail Butterfly | *Papilio machaon* | 122,536 | 71 |
| #1,718 | +718 | Black-tailed Prairie Dog | *Cynomys ludovicianus* | 118,320 | 39 |
| #1,787 | +787 | Great Barracuda | *Sphyraena barracuda* | 113,177 | 40 |
| #1,842 | +842 | Electric Eel | *Electrophorus electricus* | 108,571 | 74 |
| #1,945 | +945 | Common Wombat | *Vombatus ursinus* | 101,608 | 48 |

## 4. Species in Advanced Tier (Ranks 2,001 – 5,000)

| Vwiki Rank | Off by (vs. 1k) | Common Name | Scientific Name | Cumulative Views | Sitelinks |
| :---: | :---: | :--- | :--- | :---: | :---: |
| #2,136 | +1,136 | Red Lionfish | *Pterois volitans* | 89,795 | 47 |
| #2,430 | +1,430 | Smooth Newt | *Lissotriton vulgaris* | 76,788 | 51 |
| #2,463 | +1,463 | Giant Moray | *Gymnothorax javanicus* | 75,357 | 24 |
| #2,642 | +1,642 | Mexican Redknee Tarantula | *Brachypelma hamorii* | 67,850 | 14 |
| #2,886 | +1,886 | Sea Walnut Comb Jelly | *Mnemiopsis leidyi* | 59,877 | 26 |
| #3,169 | +2,169 | Periodical Cicada | *Magicicada septendecim* | 52,279 | 19 |
| #3,478 | +2,478 | African Malaria Mosquito | *Anopheles gambiae* | 45,189 | 21 |
| #3,648 | +2,648 | Blue-ringed Octopus | *Hapalochlaena maculosa* | 42,263 | 24 |
| #3,869 | +2,869 | Dyeing Dart Frog | *Dendrobates tinctorius* | 38,183 | 32 |
| #4,457 | +3,457 | Goliath Beetle | *Goliathus goliatus* | 30,041 | 17 |
| #4,656 | +3,656 | Green Spotted Puffer | *Tetraodon nigroviridis* | 27,802 | 22 |
| #4,830 | +3,830 | Leafcutter Ant | *Atta cephalotes* | 26,128 | 14 |

## 5. Species in Master Tier Only (Ranks > 5,000)

These organisms represent specialized microscopic, deep-sea, or obscure biological lineages present in the original 344:

| Vwiki Rank | Off by (vs. 1k) | Common Name | Scientific Name | Cumulative Views | Sitelinks |
| :---: | :---: | :--- | :--- | :---: | :---: |
