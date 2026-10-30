# 🧬 Analysis: Original 344 Species vs. Top 1,000 Vwiki Rankings

> **Analysis Date:** 2026-10-29  
> **Dataset:** `species_ranking_by_vwiki.csv` (empirical Wikimedia pageviews)  
> **Baseline:** 344 Original Untouched Organisms  

## 1. Executive Summary

### Comparison by Evaluation Mode:
- **Option 3 Gameplay Perspective (Live in Game):** **318 / 344 (92.4%)** in Top 1,000
- **Strict Species-Only Perspective:** **241 / 344 (70.1%)** in Top 1,000

### Option 3 Tier Distribution:
- **Inside Top 1,000 (🐾 Easy Tier):** **318 / 344 (92.4%)**
- **Inside Top 2,000 (🌿 Normal Tier):** **340 / 344 (98.8%)**
- **Inside Top 5,000 (🔬 Advanced Tier):** **344 / 344 (100.0%)**
- **Master Tier Only (> 5,000):** **0 / 344 (0.0%)**
- **Median Rank:** **#303**

## 2. Option 3 Recognizable Taxa & Genuses Impact

The 100 iconic baseline organisms where the English Wikipedia article covers the Genus, Suborder, Family, or Order:

| Common Name | Taxonomic Level | Species Binomial | Species Rank | Option 3 Taxon | Taxon Rank | Rank Gain | Taxon Views |
| :--- | :--- | :--- | :---: | :--- | :---: | :---: | :---: |
| **Caecilian** | Order | *Gymnopis multiplicata* | #17,413 | *Gymnophiona* | **#644** | +16,769 | 348,203 |
| **Tardigrade** | Phylum | *Hypsibius exemplaris* | #7,459 | *Tardigrada* | **#26** | +7,433 | 2,247,127 |
| **Planarian** | Order | *Schmidtea mediterranea* | #7,303 | *Tricladida* | **#805** | +6,498 | 274,316 |
| **Slug** | Family | *Deroceras reticulatum* | #5,571 | *Agriolimacidae* | **#457** | +5,114 | 492,072 |
| **Sea Cucumber** | Class | *Holothuria atra* | #5,310 | *Holothuroidea* | **#331** | +4,979 | 635,717 |
| **Sea Anemone** | Order | *Actinia equina* | #4,896 | *Actiniaria* | **#374** | +4,522 | 570,737 |
| **Seahorse** | Genus | *Hippocampus kuda* | #4,497 | *Hippocampus* | **#213** | +4,284 | 880,481 |
| **Squid** | Class | *Loligo vulgaris* | #3,978 | *Decapodiformes* | **#268** | +3,710 | 768,194 |
| **Poison Dart Frog** | Family | *Dendrobates tinctorius* | #3,900 | *Dendrobatidae* | **#320** | +3,580 | 649,580 |
| **Blue-ringed octopus** | Genus | *Hapalochlaena maculosa* | #3,679 | *Hapalochlaena* | **#104** | +3,575 | 1,274,892 |
| **Mosquito** | Family | *Anopheles gambiae* | #3,509 | *Culicidae* | **#111** | +3,398 | 1,259,066 |
| **Dragonfly** | Order | *Anax imperator* | #3,462 | *Anisoptera* | **#159** | +3,303 | 1,048,873 |
| **Stingray** | Order | *Dasyatis pastinaca* | #3,521 | *Myliobatiformes* | **#264** | +3,257 | 779,248 |
| **Starfish** | Class | *Asterias rubens* | #3,453 | *Asteroidea* | **#254** | +3,199 | 801,295 |
| **Slow Loris** | Genus | *Nycticebus coucang* | #3,674 | *Nycticebus* | **#496** | +3,178 | 454,277 |
| **Chameleon** | Family | *Chamaeleo chamaeleon* | #3,418 | *Chamaeleonidae* | **#243** | +3,175 | 819,924 |
| **Cicada** | Family | *Magicicada septendecim* | #3,200 | *Cicadidae* | **#70** | +3,130 | 1,523,445 |
| **Chinchilla** | Genus | *Chinchilla lanigera* | #3,299 | *Chinchilla* | **#222** | +3,077 | 861,228 |
| **Sea Urchin** | Class | *Strongylocentrotus purpuratus* | #3,079 | *Echinoidea* | **#228** | +2,851 | 858,627 |
| **Kiwi** | Genus | *Apteryx mantelli* | #2,835 | *Apteryx* | **#126** | +2,709 | 1,178,121 |
| **Tree Kangaroo** | Genus | *Dendrolagus matschiei* | #3,395 | *Dendrolagus* | **#748** | +2,647 | 300,140 |
| **Sponge** | Phylum | *Aplysina fistularis* | #2,815 | *Porifera* | **#251** | +2,564 | 806,240 |
| **Tarantula** | Family | *Brachypelma hamorii* | #2,673 | *Theraphosidae* | **#191** | +2,482 | 934,100 |
| **Howler Monkey** | Genus | *Alouatta palliata* | #3,161 | *Alouatta* | **#921** | +2,240 | 241,829 |
| **Oyster** | Family | *Crassostrea gigas* | #2,524 | *Ostreidae* | **#290** | +2,234 | 722,272 |
| **Sloth** | Suborder | *Bradypus tridactylus* | #2,178 | *Folivora* | **#134** | +2,044 | 1,142,165 |
| **Moray Eel** | Family | *Gymnothorax javanicus* | #2,494 | *Muraenidae* | **#459** | +2,035 | 491,708 |
| **Cuttlefish** | Order | *Sepia officinalis* | #2,176 | *Sepiida* | **#175** | +2,001 | 982,814 |
| **Newt** | Subfamily | *Lissotriton vulgaris* | #2,461 | *Pleurodelinae* | **#485** | +1,976 | 465,343 |
| **Spider Monkey** | Genus | *Ateles geoffroyi* | #2,467 | *Ateles* | **#542** | +1,925 | 415,780 |
| **Giraffe** | Genus | *Giraffa camelopardalis* | #1,975 | *Giraffa* | **#56** | +1,919 | 1,725,569 |
| **Lionfish** | Genus | *Pterois volitans* | #2,167 | *Pterois* | **#275** | +1,892 | 741,145 |
| **Wombat** | Family | *Vombatus ursinus* | #1,976 | *Vombatidae* | **#121** | +1,855 | 1,220,950 |
| **Millipede** | Class | *Archispirostreptus gigas* | #2,171 | *Diplopoda* | **#347** | +1,824 | 609,716 |
| **Bumblebee** | Genus | *Bombus terrestris* | #1,848 | *Bombus* | **#155** | +1,693 | 1,057,674 |
| **Coelacanth** | Genus | *Latimeria chalumnae* | #1,791 | *Latimeria* | **#107** | +1,684 | 1,271,248 |
| **Wasp** | Family | *Vespula vulgaris* | #1,893 | *Vespidae* | **#210** | +1,683 | 886,747 |
| **Frog** | Order | *Rana temporaria* | #1,617 | *Anura* | **#35** | +1,582 | 2,048,190 |
| **Barracuda** | Genus | *Sphyraena barracuda* | #1,818 | *Sphyraena* | **#282** | +1,536 | 733,646 |
| **Mole** | Family | *Talpa europaea* | #1,790 | *Talpidae* | **#258** | +1,532 | 796,859 |
| **Prairie Dog** | Genus | *Cynomys ludovicianus* | #1,749 | *Cynomys* | **#314** | +1,435 | 663,084 |
| **Nautilus** | Family | *Nautilus pompilius* | #1,615 | *Nautilidae* | **#229** | +1,386 | 858,051 |
| **Snail** | Class | *Helix pomatia* | #1,669 | *Gastropoda* | **#308** | +1,361 | 680,730 |
| **Gibbon** | Genus | *Hylobates lar* | #1,695 | *Hylobates* | **#340** | +1,355 | 620,243 |
| **Swallowtail Butterfly** | Family | *Papilio machaon* | #1,690 | *Papilionidae* | **#442** | +1,248 | 504,382 |
| **Swan** | Genus | *Cygnus cygnus* | #1,429 | *Cygnus* | **#182** | +1,247 | 969,709 |
| **Scorpion** | Order | *Pandinus imperator* | #1,372 | *Scorpiones* | **#137** | +1,235 | 1,128,831 |
| **Horseshoe Crab** | Family | *Limulus polyphemus* | #1,342 | *Limulidae* | **#108** | +1,234 | 1,263,466 |
| **Baboon** | Genus | *Papio anubis* | #1,467 | *Papio* | **#297** | +1,170 | 708,763 |
| **Catfish** | Order | *Ictalurus punctatus* | #1,296 | *Siluriformes* | **#164** | +1,132 | 1,013,202 |
| **Earthworm** | Order | *Lumbricus terrestris* | #1,449 | *Lumbricina* | **#337** | +1,112 | 625,973 |
| **Hummingbird** | Family | *Archilochus colubris* | #1,221 | *Trochilidae* | **#114** | +1,107 | 1,250,040 |
| **Octopus** | Order | *Octopus vulgaris* | #1,146 | *Octopoda* | **#47** | +1,099 | 1,825,040 |
| **Stag Beetle** | Family | *Lucanus cervus* | #1,852 | *Lucanidae* | **#754** | +1,098 | 297,542 |
| **Kangaroo** | Genus | *Macropus giganteus* | #1,079 | *Macropus* | **#30** | +1,049 | 2,122,501 |
| **Piranha** | Family | *Pygocentrus nattereri* | #1,335 | *Serrasalmidae* | **#289** | +1,046 | 724,648 |
| **Clam** | Class | *Mercenaria mercenaria* | #1,552 | *Bivalvia* | **#533** | +1,019 | 423,910 |
| **Hedgehog** | Subfamily | *Erinaceus europaeus* | #1,141 | *Erinaceinae* | **#124** | +1,017 | 1,198,254 |
| **Anglerfish** | Order | *Melanocetus johnsonii* | #1,085 | *Lophiiformes* | **#73** | +1,012 | 1,486,903 |
| **Clownfish** | Genus | *Amphiprion ocellaris* | #1,292 | *Amphiprion* | **#333** | +959 | 632,287 |
| **Box Jellyfish** | Class | *Chironex fleckeri* | #1,182 | *Cubozoa* | **#261** | +921 | 785,893 |
| **Salamander** | Order | *Salamandra salamandra* | #1,133 | *Caudata* | **#221** | +912 | 862,097 |
| **Mantis** | Order | *Mantis religiosa* | #1,058 | *Mantodea* | **#150** | +908 | 1,068,871 |
| **Mantis Shrimp** | Order | *Odontodactylus scyllarus* | #1,046 | *Stomatopoda* | **#147** | +899 | 1,082,717 |
| **Porpoise** | Family | *Phocoena phocoena* | #1,298 | *Phocoenidae* | **#411** | +887 | 533,615 |
| **Tarsier** | Family | *Carlito syrichta* | #1,290 | *Tarsiidae* | **#426** | +864 | 516,739 |
| **Prawn** | Order | *Penaeus monodon* | #1,396 | *Dendrobranchiata* | **#534** | +862 | 423,794 |
| **Vampire Bat** | Genus | *Desmodus rotundus* | #1,341 | *Desmodus* | **#489** | +852 | 463,852 |
| **Lobster** | Family | *Homarus americanus* | #1,060 | *Nephropidae* | **#208** | +852 | 894,673 |
| **Pelican** | Genus | *Pelecanus occidentalis* | #1,170 | *Pelecanus* | **#355** | +815 | 599,242 |
| **Goose** | Genus | *Anser anser* | #1,075 | *Anser* | **#293** | +782 | 713,460 |
| **Porcupine** | Genus | *Erethizon dorsatum* | #952 | *Erethizon* | **#192** | +760 | 932,169 |
| **Manatee** | Genus | *Trichechus manatus* | #901 | *Trichechus* | **#146** | +755 | 1,092,463 |
| **Arapaima** | Genus | *Arapaima gigas* | #1,099 | *Arapaima* | **#351** | +748 | 603,950 |
| **Cormorant** | Family | *Phalacrocorax carbo* | #1,034 | *Phalacrocoracidae* | **#303** | +731 | 691,354 |
| **Hare** | Genus | *Lepus europaeus* | #959 | *Lepus* | **#238** | +721 | 836,738 |
| **Bottlenose Dolphin** | Genus | *Tursiops truncatus* | #1,233 | *Tursiops* | **#578** | +655 | 385,941 |
| **Toad** | Family | *Bufo bufo* | #1,313 | *Bufonidae* | **#672** | +641 | 334,481 |
| **Gorilla** | Genus | *Gorilla gorilla* | #654 | *Gorilla* | **#29** | +625 | 2,145,135 |
| **Seal** | Clade | *Phoca vitulina* | #691 | *Pinnipedia* | **#103** | +588 | 1,280,030 |
| **Orangutan** | Genus | *Pongo pygmaeus* | #633 | *Pongo* | **#69** | +564 | 1,532,594 |
| **Fire Ant** | Genus | *Solenopsis invicta* | #1,092 | *Solenopsis* | **#565** | +527 | 396,096 |
| **Warthog** | Genus | *Phacochoerus africanus* | #1,093 | *Phacochoerus* | **#577** | +516 | 386,768 |
| **Beaver** | Genus | *Castor canadensis* | #583 | *Castor* | **#90** | +493 | 1,368,835 |
| **Turkey** | Genus | *Meleagris gallopavo* | #446 | *Meleagris* | **#2** | +444 | 9,145,211 |
| **Opossum** | Family | *Didelphis virginiana* | #465 | *Didelphidae* | **#37** | +428 | 1,990,819 |
| **Rabbit** | Genus | *Oryctolagus cuniculus* | #432 | *Oryctolagus* | **#41** | +391 | 1,948,854 |
| **Elephant** | Family | *Loxodonta africana* | #286 | *Elephantidae* | **#15** | +271 | 2,715,467 |
| **Ostrich** | Genus | *Struthio camelus* | #415 | *Struthio* | **#232** | +183 | 853,421 |
| **Black Rhinoceros** | Genus | *Diceros bicornis* | #453 | *Diceros* | **#451** | +2 | 497,789 |
| **African Buffalo** | Genus | *Syncerus caffer* | #345 | *Syncerus* | **#343** | +2 | 612,682 |
| **King Cobra** | Genus | *Ophiophagus hannah* | #84 | *Ophiophagus* | **#83** | +1 | 1,425,097 |
| **Python** | Genus | *Python regius* | #390 | *Python* | **#1,107** | -717 | 194,740 |
| **Python** | Genus | *Python bivittatus* | #375 | *Python* | **#1,107** | -732 | 194,740 |
| **Rat** | Genus | *Rattus norvegicus* | #387 | *Rattus* | **#1,259** | -872 | 168,949 |
| **Tree Squirrel** | Genus | *Sciurus carolinensis* | #450 | *Sciurus* | **#2,278** | -1,828 | 84,432 |
| **Tree Squirrel** | Genus | *Sciurus vulgaris* | #245 | *Sciurus* | **#2,278** | -2,033 | 84,432 |
| **Mouse** | Genus | *Mus musculus* | #416 | *Mus* | **#2,508** | -2,092 | 74,881 |
| **River Otter** | Genus | *Lontra canadensis* | #556 | *Lontra* | **#2,756** | -2,200 | 64,770 |
| **Long-nosed Armadillo** | Genus | *Dasypus novemcinctus* | #802 | *Dasypus* | **#3,011** | -2,209 | 57,271 |

## 3. Organisms Just Outside Top 1,000 (Ranks 1,001 – 2,000)

These organisms missed the 🐾 Easy (top 1k) cutoff, but comfortably qualify for the 🌿 Normal (top 2k) tier:

| Vwiki Rank | Off by (vs. 1k) | Common Name | Scientific Name | Cumulative Views | Sitelinks |
| :---: | :---: | :--- | :--- | :---: | :---: |
| #1,011 | +11 | California Sea Lion | *Zalophus californianus* | 218,492 | 48 |
| #1,015 | +15 | Wood Duck | *Aix sponsa* | 217,644 | 54 |
| #1,022 | +22 | Giant Clam | *Tridacna gigas* | 216,232 | 40 |
| #1,023 | +23 | Barn Owl | *Tyto alba* | 216,229 | 104 |
| #1,097 | +97 | Black Widow Spider | *Latrodectus mactans* | 196,342 | 41 |
| #1,100 | +100 | Thorny Devil | *Moloch horridus* | 196,169 | 49 |
| #1,108 | +108 | Wandering Albatross | *Diomedea exulans* | 194,315 | 52 |
| #1,153 | +153 | Ringed Seal | *Pusa hispida* | 186,696 | 57 |
| #1,154 | +154 | California Quail | *Callipepla californica* | 186,693 | 33 |
| #1,211 | +211 | Golden Lion Tamarin | *Leontopithecus rosalia* | 175,767 | 47 |
| #1,251 | +251 | Regal Blue Tang | *Paracanthurus hepatus* | 169,792 | 43 |
| #1,252 | +252 | Gelada | *Theropithecus gelada* | 169,779 | 58 |
| #1,254 | +254 | Goliath Frog | *Conraua goliath* | 169,552 | 49 |
| #1,267 | +267 | Siamang | *Symphalangus syndactylus* | 168,284 | 60 |
| #1,268 | +268 | Fiddler Crab | *Uca pugilator* | 168,137 | 34 |
| #1,273 | +273 | Red-eyed Tree Frog | *Agalychnis callidryas* | 167,689 | 48 |
| #1,321 | +321 | Seven-spot Ladybird | *Coccinella septempunctata* | 161,899 | 65 |
| #1,356 | +356 | Japanese Giant Salamander | *Andrias japonicus* | 155,937 | 43 |
| #1,426 | +426 | Little Brown Bat | *Myotis lucifugus* | 148,034 | 31 |
| #1,588 | +588 | Central Bearded Dragon | *Pogona vitticeps* | 130,875 | 41 |
| #1,639 | +639 | African Clawed Frog | *Xenopus laevis* | 126,647 | 39 |
| #1,873 | +873 | Electric Eel | *Electrophorus electricus* | 108,571 | 74 |

## 4. Species in Advanced Tier (Ranks 2,001 – 5,000)

| Vwiki Rank | Off by (vs. 1k) | Common Name | Scientific Name | Cumulative Views | Sitelinks |
| :---: | :---: | :--- | :--- | :---: | :---: |
| #2,917 | +1,917 | Sea Walnut Comb Jelly | *Mnemiopsis leidyi* | 59,877 | 26 |
| #4,488 | +3,488 | Goliath Beetle | *Goliathus goliatus* | 30,041 | 17 |
| #4,687 | +3,687 | Green Spotted Puffer | *Tetraodon nigroviridis* | 27,802 | 22 |
| #4,861 | +3,861 | Leafcutter Ant | *Atta cephalotes* | 26,128 | 14 |

## 5. Species in Master Tier Only (Ranks > 5,000)

These organisms represent specialized microscopic, deep-sea, or obscure biological lineages present in the original 344:

| Vwiki Rank | Off by (vs. 1k) | Common Name | Scientific Name | Cumulative Views | Sitelinks |
| :---: | :---: | :--- | :--- | :---: | :---: |
