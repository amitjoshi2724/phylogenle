# 🧬 Analysis: Original 344 Species vs. Top 1,000 Vwiki Rankings

> **Analysis Date:** 2026-10-30  
> **Dataset:** `species_ranking_by_vwiki.csv` (empirical Wikimedia pageviews)  
> **Baseline:** 344 Original Untouched Organisms  

## 1. Executive Summary

### Comparison by Evaluation Mode:
- **Option 3 Gameplay Perspective (Live in Game):** **327 / 344 (95.1%)** in Top 1,000
- **Strict Species-Only Perspective:** **241 / 344 (70.1%)** in Top 1,000

### Option 3 Tier Distribution:
- **Inside Top 1,000 (🐾 Easy Tier):** **327 / 344 (95.1%)**
- **Inside Top 2,000 (🌿 Normal Tier):** **344 / 344 (100.0%)**
- **Inside Top 5,000 (🔬 Advanced Tier):** **344 / 344 (100.0%)**
- **Master Tier Only (> 5,000):** **0 / 344 (0.0%)**
- **Median Rank:** **#298**

## 2. Option 3 Recognizable Taxa & Genuses Impact

The 121 iconic baseline organisms where the English Wikipedia article covers the Genus, Suborder, Family, or Order:

| Common Name | Taxonomic Level | Species Binomial | Species Rank | Option 3 Taxon | Taxon Rank | Rank Gain | Taxon Views |
| :--- | :--- | :--- | :---: | :--- | :---: | :---: | :---: |
| **Caecilian** | Order | *Gymnopis multiplicata* | #17,433 | *Gymnophiona* | **#659** | +16,774 | 348,203 |
| **Tardigrade** | Phylum | *Hypsibius exemplaris* | #7,479 | *Tardigrada* | **#28** | +7,451 | 2,247,127 |
| **Planarian** | Order | *Schmidtea mediterranea* | #7,323 | *Tricladida* | **#820** | +6,503 | 274,316 |
| **Slug** | Family | *Deroceras reticulatum* | #5,591 | *Agriolimacidae* | **#469** | +5,122 | 492,072 |
| **Sea Cucumber** | Class | *Holothuria atra* | #5,330 | *Holothuroidea* | **#340** | +4,990 | 635,717 |
| **Sea Anemone** | Order | *Actinia equina* | #4,916 | *Actiniaria* | **#385** | +4,531 | 570,737 |
| **Seahorse** | Genus | *Hippocampus kuda* | #4,517 | *Hippocampus* | **#222** | +4,295 | 880,481 |
| **Pufferfish** | Family | *Tetraodon nigroviridis* | #4,707 | *Tetraodontidae* | **#417** | +4,290 | 542,342 |
| **Leafcutter Ant** | Genus | *Atta cephalotes* | #4,881 | *Atta* | **#1,107** | +3,774 | 200,569 |
| **Squid** | Class | *Loligo vulgaris* | #3,998 | *Decapodiformes* | **#277** | +3,721 | 768,194 |
| **Poison Dart Frog** | Family | *Dendrobates tinctorius* | #3,920 | *Dendrobatidae* | **#329** | +3,591 | 649,580 |
| **Blue-ringed octopus** | Genus | *Hapalochlaena maculosa* | #3,699 | *Hapalochlaena* | **#108** | +3,591 | 1,274,892 |
| **Mosquito** | Family | *Anopheles gambiae* | #3,529 | *Culicidae* | **#115** | +3,414 | 1,259,066 |
| **Dragonfly** | Order | *Anax imperator* | #3,482 | *Anisoptera* | **#164** | +3,318 | 1,048,873 |
| **Stingray** | Order | *Dasyatis pastinaca* | #3,541 | *Myliobatiformes* | **#273** | +3,268 | 779,248 |
| **Starfish** | Class | *Asterias rubens* | #3,473 | *Asteroidea* | **#263** | +3,210 | 801,295 |
| **Chameleon** | Family | *Chamaeleo chamaeleon* | #3,438 | *Chamaeleonidae* | **#252** | +3,186 | 819,924 |
| **Slow Loris** | Genus | *Nycticebus coucang* | #3,694 | *Nycticebus* | **#509** | +3,185 | 454,277 |
| **Cicada** | Family | *Magicicada septendecim* | #3,220 | *Cicadidae* | **#73** | +3,147 | 1,523,445 |
| **Chinchilla** | Genus | *Chinchilla lanigera* | #3,319 | *Chinchilla* | **#231** | +3,088 | 861,228 |
| **Sea Urchin** | Class | *Strongylocentrotus purpuratus* | #3,099 | *Echinoidea* | **#237** | +2,862 | 858,627 |
| **Kiwi** | Genus | *Apteryx mantelli* | #2,855 | *Apteryx* | **#130** | +2,725 | 1,178,121 |
| **Tree Kangaroo** | Genus | *Dendrolagus matschiei* | #3,415 | *Dendrolagus* | **#763** | +2,652 | 300,140 |
| **Goliath Beetle** | Genus | *Goliathus goliatus* | #4,508 | *Goliathus* | **#1,863** | +2,645 | 111,366 |
| **Sponge** | Phylum | *Aplysina fistularis* | #2,835 | *Porifera* | **#260** | +2,575 | 806,240 |
| **Tarantula** | Family | *Brachypelma hamorii* | #2,693 | *Theraphosidae* | **#198** | +2,495 | 934,100 |
| **Comb Jelly** | Phylum | *Mnemiopsis leidyi* | #2,937 | *Ctenophora* | **#479** | +2,458 | 482,694 |
| **Howler Monkey** | Genus | *Alouatta palliata* | #3,181 | *Alouatta* | **#936** | +2,245 | 241,829 |
| **Oyster** | Family | *Crassostrea gigas* | #2,543 | *Ostreidae* | **#299** | +2,244 | 722,272 |
| **Sloth** | Suborder | *Bradypus tridactylus* | #2,197 | *Folivora* | **#138** | +2,059 | 1,142,165 |
| **Moray Eel** | Family | *Gymnothorax javanicus* | #2,513 | *Muraenidae* | **#471** | +2,042 | 491,708 |
| **Cuttlefish** | Order | *Sepia officinalis* | #2,195 | *Sepiida* | **#180** | +2,015 | 982,814 |
| **Newt** | Subfamily | *Lissotriton vulgaris* | #2,480 | *Pleurodelinae* | **#498** | +1,982 | 465,343 |
| **Giraffe** | Genus | *Giraffa camelopardalis* | #1,994 | *Giraffa* | **#59** | +1,935 | 1,725,569 |
| **Spider Monkey** | Genus | *Ateles geoffroyi* | #2,486 | *Ateles* | **#555** | +1,931 | 415,780 |
| **Lionfish** | Genus | *Pterois volitans* | #2,186 | *Pterois* | **#284** | +1,902 | 741,145 |
| **Wombat** | Family | *Vombatus ursinus* | #1,995 | *Vombatidae* | **#125** | +1,870 | 1,220,950 |
| **Millipede** | Class | *Archispirostreptus gigas* | #2,190 | *Diplopoda* | **#357** | +1,833 | 609,716 |
| **Bumblebee** | Genus | *Bombus terrestris* | #1,867 | *Bombus* | **#160** | +1,707 | 1,057,674 |
| **Coelacanth** | Genus | *Latimeria chalumnae* | #1,809 | *Latimeria* | **#111** | +1,698 | 1,271,248 |
| **Wasp** | Family | *Vespula vulgaris* | #1,912 | *Vespidae* | **#219** | +1,693 | 886,747 |
| **Frog** | Order | *Rana temporaria* | #1,635 | *Anura* | **#37** | +1,598 | 2,048,190 |
| **Electric Eel** | Genus | *Electrophorus electricus* | #1,892 | *Electrophorus* | **#345** | +1,547 | 629,695 |
| **Barracuda** | Genus | *Sphyraena barracuda* | #1,836 | *Sphyraena* | **#291** | +1,545 | 733,646 |
| **Mole** | Family | *Talpa europaea* | #1,808 | *Talpidae* | **#267** | +1,541 | 796,859 |
| **Prairie Dog** | Genus | *Cynomys ludovicianus* | #1,767 | *Cynomys* | **#323** | +1,444 | 663,084 |
| **Nautilus** | Family | *Nautilus pompilius* | #1,633 | *Nautilidae* | **#238** | +1,395 | 858,051 |
| **Snail** | Class | *Helix pomatia* | #1,687 | *Gastropoda* | **#317** | +1,370 | 680,730 |
| **Gibbon** | Genus | *Hylobates lar* | #1,713 | *Hylobates* | **#350** | +1,363 | 620,243 |
| **Swan** | Genus | *Cygnus cygnus* | #1,447 | *Cygnus* | **#188** | +1,259 | 969,709 |
| **Swallowtail Butterfly** | Family | *Papilio machaon* | #1,708 | *Papilionidae* | **#454** | +1,254 | 504,382 |
| **Scorpion** | Order | *Pandinus imperator* | #1,390 | *Scorpiones* | **#142** | +1,248 | 1,128,831 |
| **Horseshoe Crab** | Family | *Limulus polyphemus* | #1,360 | *Limulidae* | **#112** | +1,248 | 1,263,466 |
| **Baboon** | Genus | *Papio anubis* | #1,485 | *Papio* | **#306** | +1,179 | 708,763 |
| **Ladybird** | Family | *Coccinella septempunctata* | #1,339 | *Coccinellidae* | **#184** | +1,155 | 976,980 |
| **Catfish** | Order | *Ictalurus punctatus* | #1,314 | *Siluriformes* | **#169** | +1,145 | 1,013,202 |
| **Hummingbird** | Family | *Archilochus colubris* | #1,238 | *Trochilidae* | **#118** | +1,120 | 1,250,040 |
| **Earthworm** | Order | *Lumbricus terrestris* | #1,467 | *Lumbricina* | **#347** | +1,120 | 625,973 |
| **Octopus** | Order | *Octopus vulgaris* | #1,163 | *Octopoda* | **#49** | +1,114 | 1,825,040 |
| **Stag Beetle** | Family | *Lucanus cervus* | #1,871 | *Lucanidae* | **#769** | +1,102 | 297,542 |
| **Kangaroo** | Genus | *Macropus giganteus* | #1,095 | *Macropus* | **#32** | +1,063 | 2,124,308 |
| **Piranha** | Family | *Pygocentrus nattereri* | #1,353 | *Serrasalmidae* | **#298** | +1,055 | 724,648 |
| **Bearded Dragon** | Genus | *Pogona vitticeps* | #1,606 | *Pogona* | **#575** | +1,031 | 400,123 |
| **Hedgehog** | Subfamily | *Erinaceus europaeus* | #1,158 | *Erinaceinae* | **#128** | +1,030 | 1,198,254 |
| **Anglerfish** | Order | *Melanocetus johnsonii* | #1,101 | *Lophiiformes* | **#76** | +1,025 | 1,486,903 |
| **Clam** | Class | *Mercenaria mercenaria* | #1,570 | *Bivalvia* | **#546** | +1,024 | 423,910 |
| **Clownfish** | Genus | *Amphiprion ocellaris* | #1,310 | *Amphiprion* | **#342** | +968 | 632,287 |
| **Box Jellyfish** | Class | *Chironex fleckeri* | #1,199 | *Cubozoa* | **#270** | +929 | 785,893 |
| **Albatross** | Family | *Diomedea exulans* | #1,125 | *Diomedeidae* | **#204** | +921 | 924,227 |
| **Salamander** | Order | *Salamandra salamandra* | #1,150 | *Caudata* | **#230** | +920 | 862,097 |
| **Mantis** | Order | *Mantis religiosa* | #1,074 | *Mantodea* | **#155** | +919 | 1,068,871 |
| **Black Widow Spider** | Genus | *Latrodectus mactans* | #1,114 | *Latrodectus* | **#197** | +917 | 935,454 |
| **Mantis Shrimp** | Order | *Odontodactylus scyllarus* | #1,062 | *Stomatopoda* | **#152** | +910 | 1,082,717 |
| **Porpoise** | Family | *Phocoena phocoena* | #1,316 | *Phocoenidae* | **#423** | +893 | 533,615 |
| **Tarsier** | Family | *Carlito syrichta* | #1,308 | *Tarsiidae* | **#438** | +870 | 516,739 |
| **Prawn** | Order | *Penaeus monodon* | #1,414 | *Dendrobranchiata* | **#547** | +867 | 423,794 |
| **Lobster** | Family | *Homarus americanus* | #1,076 | *Nephropidae* | **#217** | +859 | 894,673 |
| **Vampire Bat** | Genus | *Desmodus rotundus* | #1,359 | *Desmodus* | **#502** | +857 | 463,852 |
| **Pelican** | Genus | *Pelecanus occidentalis* | #1,187 | *Pelecanus* | **#365** | +822 | 599,242 |
| **Sea Lion** | Subfamily | *Zalophus californianus* | #1,026 | *Otariinae* | **#211** | +815 | 912,072 |
| **Goose** | Genus | *Anser anser* | #1,091 | *Anser* | **#302** | +789 | 713,460 |
| **Porcupine** | Genus | *Erethizon dorsatum* | #967 | *Erethizon* | **#199** | +768 | 932,169 |
| **Manatee** | Genus | *Trichechus manatus* | #916 | *Trichechus* | **#151** | +765 | 1,092,463 |
| **Arapaima** | Genus | *Arapaima gigas* | #1,116 | *Arapaima* | **#361** | +755 | 603,950 |
| **Cormorant** | Family | *Phalacrocorax carbo* | #1,050 | *Phalacrocoracidae* | **#312** | +738 | 691,354 |
| **Hare** | Genus | *Lepus europaeus* | #974 | *Lepus* | **#247** | +727 | 836,738 |
| **Bottlenose Dolphin** | Genus | *Tursiops truncatus* | #1,250 | *Tursiops* | **#593** | +657 | 385,941 |
| **Toad** | Family | *Bufo bufo* | #1,331 | *Bufonidae* | **#687** | +644 | 334,481 |
| **Gorilla** | Genus | *Gorilla gorilla* | #669 | *Gorilla* | **#31** | +638 | 2,145,135 |
| **Seal** | Clade | *Phoca vitulina* | #706 | *Pinnipedia* | **#107** | +599 | 1,280,030 |
| **Orangutan** | Genus | *Pongo pygmaeus* | #648 | *Pongo* | **#72** | +576 | 1,532,594 |
| **Fire Ant** | Genus | *Solenopsis invicta* | #1,109 | *Solenopsis* | **#579** | +530 | 396,096 |
| **Warthog** | Genus | *Phacochoerus africanus* | #1,110 | *Phacochoerus* | **#592** | +518 | 386,768 |
| **Beaver** | Genus | *Castor canadensis* | #598 | *Castor* | **#94** | +504 | 1,368,835 |
| **Turkey** | Genus | *Meleagris gallopavo* | #458 | *Meleagris* | **#2** | +456 | 9,145,211 |
| **Barn Owl** | Genus | *Tyto alba* | #1,039 | *Tyto* | **#590** | +449 | 387,592 |
| **Opossum** | Family | *Didelphis virginiana* | #477 | *Didelphidae* | **#39** | +438 | 1,990,819 |
| **Rabbit** | Genus | *Oryctolagus cuniculus* | #444 | *Oryctolagus* | **#43** | +401 | 1,948,854 |
| **Elephant** | Family | *Loxodonta africana* | #295 | *Elephantidae* | **#15** | +280 | 2,715,467 |
| **Hyena** | Family | *Crocuta crocuta* | #332 | *Hyaenidae* | **#77** | +255 | 1,480,798 |
| **Lynx** | Genus | *Lynx lynx* | #384 | *Lynx* | **#141** | +243 | 1,131,565 |
| **Ostrich** | Genus | *Struthio camelus* | #427 | *Struthio* | **#241** | +186 | 853,421 |
| **Macaque** | Genus | *Macaca mulatta* | #511 | *Macaca* | **#366** | +145 | 598,859 |
| **Fiddler Crab** | Family | *Uca pugilator* | #1,286 | *Ocypodidae* | **#1,282** | +4 | 168,626 |
| **Giant Clam** | Genus | *Tridacna gigas* | #1,038 | *Tridacna* | **#1,035** | +3 | 216,856 |
| **Raccoon** | Genus | *Procyon lotor* | #27 | *Procyon* | **#25** | +2 | 2,270,162 |
| **Black Rhinoceros** | Genus | *Diceros bicornis* | #465 | *Diceros* | **#463** | +2 | 497,789 |
| **African Buffalo** | Genus | *Syncerus caffer* | #355 | *Syncerus* | **#353** | +2 | 612,682 |
| **Giant Panda** | Genus | *Ailuropoda melanoleuca* | #20 | *Ailuropoda* | **#19** | +1 | 2,542,645 |
| **Hippopotamus** | Family | *Hippopotamus amphibius* | #53 | *Hippopotamidae* | **#52** | +1 | 1,780,359 |
| **Kangaroo** | Genus | *Macropus rufus* | #33 | *Macropus* | **#32** | +1 | 2,124,308 |
| **King Cobra** | Genus | *Ophiophagus hannah* | #88 | *Ophiophagus* | **#87** | +1 | 1,425,097 |
| **Python** | Genus | *Python regius* | #401 | *Python* | **#1,124** | -723 | 194,740 |
| **Python** | Genus | *Python bivittatus* | #386 | *Python* | **#1,124** | -738 | 194,740 |
| **Rat** | Genus | *Rattus norvegicus* | #398 | *Rattus* | **#1,276** | -878 | 168,949 |
| **Clawed Frog** | Genus | *Xenopus laevis* | #1,657 | *Xenopus* | **#2,586** | -929 | 72,234 |
| **Tree Squirrel** | Genus | *Sciurus carolinensis* | #462 | *Sciurus* | **#2,297** | -1,835 | 84,432 |
| **Tree Squirrel** | Genus | *Sciurus vulgaris* | #254 | *Sciurus* | **#2,297** | -2,043 | 84,432 |
| **Mouse** | Genus | *Mus musculus* | #428 | *Mus* | **#2,527** | -2,099 | 74,881 |
| **River Otter** | Genus | *Lontra canadensis* | #569 | *Lontra* | **#2,776** | -2,207 | 64,770 |
| **Long-nosed Armadillo** | Genus | *Dasypus novemcinctus* | #817 | *Dasypus* | **#3,031** | -2,214 | 57,271 |

## 3. Organisms Just Outside Top 1,000 (Ranks 1,001 – 2,000)

These organisms missed the 🐾 Easy (top 1k) cutoff, but comfortably qualify for the 🌿 Normal (top 2k) tier:

| Vwiki Rank | Off by (vs. 1k) | Common Name | Scientific Name | Cumulative Views | Sitelinks |
| :---: | :---: | :--- | :--- | :---: | :---: |
| #1,030 | +30 | Wood Duck | *Aix sponsa* | 217,644 | 54 |
| #1,035 | +35 | Giant Clam | *Tridacna gigas* | 216,856 | 40 |
| #1,107 | +107 | Leafcutter Ant | *Atta cephalotes* | 200,569 | 14 |
| #1,117 | +117 | Thorny Devil | *Moloch horridus* | 196,169 | 49 |
| #1,170 | +170 | Ringed Seal | *Pusa hispida* | 186,696 | 57 |
| #1,171 | +171 | California Quail | *Callipepla californica* | 186,693 | 33 |
| #1,228 | +228 | Golden Lion Tamarin | *Leontopithecus rosalia* | 175,767 | 47 |
| #1,268 | +268 | Regal Blue Tang | *Paracanthurus hepatus* | 169,792 | 43 |
| #1,269 | +269 | Gelada | *Theropithecus gelada* | 169,779 | 58 |
| #1,271 | +271 | Goliath Frog | *Conraua goliath* | 169,552 | 49 |
| #1,282 | +282 | Fiddler Crab | *Uca pugilator* | 168,626 | 34 |
| #1,285 | +285 | Siamang | *Symphalangus syndactylus* | 168,284 | 60 |
| #1,291 | +291 | Red-eyed Tree Frog | *Agalychnis callidryas* | 167,689 | 48 |
| #1,374 | +374 | Japanese Giant Salamander | *Andrias japonicus* | 155,937 | 43 |
| #1,444 | +444 | Little Brown Bat | *Myotis lucifugus* | 148,034 | 31 |
| #1,657 | +657 | African Clawed Frog | *Xenopus laevis* | 126,647 | 39 |
| #1,863 | +863 | Goliath Beetle | *Goliathus goliatus* | 111,366 | 17 |

## 4. Species in Advanced Tier (Ranks 2,001 – 5,000)

| Vwiki Rank | Off by (vs. 1k) | Common Name | Scientific Name | Cumulative Views | Sitelinks |
| :---: | :---: | :--- | :--- | :---: | :---: |

## 5. Species in Master Tier Only (Ranks > 5,000)

These organisms represent specialized microscopic, deep-sea, or obscure biological lineages present in the original 344:

| Vwiki Rank | Off by (vs. 1k) | Common Name | Scientific Name | Cumulative Views | Sitelinks |
| :---: | :---: | :--- | :--- | :---: | :---: |
