# 🧬 Analysis: Original 344 Species vs. Top 1,000 Vwiki Rankings

> **Analysis Date:** 2026-10-28  
> **Dataset:** `species_ranking_by_vwiki.csv` (26,200 verified species)  
> **Baseline:** 344 Original Untouched Organisms  

## 1. Executive Summary

- **Inside Top 1,000 (🐾 Easy Tier):** **253 / 344 (73.5%)**
- **Inside Top 2,000 (🌿 Normal Tier):** **307 / 344 (89.2%)**
- **Inside Top 5,000 (🔬 Advanced Tier):** **339 / 344 (98.5%)**
- **Master Tier Only (> 5,000):** **5 / 344 (1.5%)**
- **Median Rank:** **#422**

## 2. Species Just Outside Top 1,000 (Ranks 1,001 – 2,000)

These organisms missed the 🐾 Easy (top 1k) cutoff, but comfortably qualify for the 🌿 Normal (top 2k) tier:

| Vwiki Rank | Off by (vs. 1k) | Common Name | Scientific Name | Cumulative Views | Sitelinks |
| :---: | :---: | :--- | :--- | :---: | :---: |
| #1,004 | +4 | Black Widow Spider | *Latrodectus mactans* | 196,342 | 41 |
| #1,006 | +6 | Arapaima | *Arapaima gigas* | 196,262 | 57 |
| #1,007 | +7 | Thorny Devil | *Moloch horridus* | 196,169 | 49 |
| #1,014 | +14 | Wandering Albatross | *Diomedea exulans* | 194,315 | 52 |
| #1,039 | +39 | Fire Salamander | *Salamandra salamandra* | 188,642 | 72 |
| #1,047 | +47 | Hedgehog | *Erinaceus europaeus* | 187,961 | 83 |
| #1,052 | +52 | Common Octopus | *Octopus vulgaris* | 187,607 | 51 |
| #1,059 | +59 | Ringed Seal | *Pusa hispida* | 186,696 | 57 |
| #1,060 | +60 | California Quail | *Callipepla californica* | 186,693 | 33 |
| #1,076 | +76 | Brown Pelican | *Pelecanus occidentalis* | 183,520 | 60 |
| #1,088 | +88 | Sea Wasp Box Jellyfish | *Chironex fleckeri* | 180,983 | 44 |
| #1,117 | +117 | Golden Lion Tamarin | *Leontopithecus rosalia* | 175,767 | 47 |
| #1,127 | +127 | Ruby-throated Hummingbird | *Archilochus colubris* | 174,397 | 39 |
| #1,139 | +139 | Bottlenose Dolphin | *Tursiops truncatus* | 172,066 | 73 |
| #1,157 | +157 | Regal Blue Tang | *Paracanthurus hepatus* | 169,792 | 43 |
| #1,158 | +158 | Gelada | *Theropithecus gelada* | 169,779 | 58 |
| #1,160 | +160 | Goliath Frog | *Conraua goliath* | 169,552 | 49 |
| #1,172 | +172 | Siamang | *Symphalangus syndactylus* | 168,284 | 60 |
| #1,173 | +173 | Fiddler Crab | *Uca pugilator* | 168,137 | 34 |
| #1,178 | +178 | Red-eyed Tree Frog | *Agalychnis callidryas* | 167,689 | 48 |
| #1,195 | +195 | Philippine Tarsier | *Carlito syrichta* | 164,902 | 44 |
| #1,197 | +197 | Ocellaris Clownfish | *Amphiprion ocellaris* | 164,800 | 37 |
| #1,201 | +201 | Channel Catfish | *Ictalurus punctatus* | 163,970 | 29 |
| #1,203 | +203 | Harbor Porpoise | *Phocoena phocoena* | 163,789 | 61 |
| #1,218 | +218 | Common Toad | *Bufo bufo* | 162,821 | 71 |
| #1,226 | +226 | Seven-spot Ladybird | *Coccinella septempunctata* | 161,899 | 65 |
| #1,240 | +240 | Red-bellied Piranha | *Pygocentrus nattereri* | 159,724 | 38 |
| #1,246 | +246 | Bat | *Desmodus rotundus* | 158,845 | 43 |
| #1,247 | +247 | Atlantic Horseshoe Crab | *Limulus polyphemus* | 158,598 | 35 |
| #1,261 | +261 | Japanese Giant Salamander | *Andrias japonicus* | 155,937 | 43 |
| #1,277 | +277 | Emperor Scorpion | *Pandinus imperator* | 154,270 | 35 |
| #1,301 | +301 | Giant Tiger Prawn | *Penaeus monodon* | 151,890 | 35 |
| #1,331 | +331 | Little Brown Bat | *Myotis lucifugus* | 148,034 | 31 |
| #1,334 | +334 | Whooper Swan | *Cygnus cygnus* | 147,740 | 90 |
| #1,354 | +354 | Common Earthworm | *Lumbricus terrestris* | 145,441 | 53 |
| #1,372 | +372 | Baboon | *Papio anubis* | 143,616 | 61 |
| #1,457 | +457 | Hard Clam | *Mercenaria mercenaria* | 134,211 | 19 |
| #1,493 | +493 | Central Bearded Dragon | *Pogona vitticeps* | 130,875 | 41 |
| #1,520 | +520 | Chambered Nautilus | *Nautilus pompilius* | 128,352 | 27 |
| #1,522 | +522 | Common Frog | *Rana temporaria* | 128,107 | 61 |
| #1,544 | +544 | African Clawed Frog | *Xenopus laevis* | 126,647 | 39 |
| #1,574 | +574 | Roman Snail | *Helix pomatia* | 124,485 | 55 |
| #1,595 | +595 | Swallowtail Butterfly | *Papilio machaon* | 122,536 | 71 |
| #1,600 | +600 | White-handed Gibbon | *Hylobates lar* | 122,351 | 51 |
| #1,654 | +654 | Black-tailed Prairie Dog | *Cynomys ludovicianus* | 118,320 | 39 |
| #1,695 | +695 | Mole | *Talpa europaea* | 114,556 | 78 |
| #1,696 | +696 | Coelacanth | *Latimeria chalumnae* | 114,531 | 45 |
| #1,723 | +723 | Great Barracuda | *Sphyraena barracuda* | 113,177 | 40 |
| #1,753 | +753 | Buff-tailed Bumblebee | *Bombus terrestris* | 111,183 | 44 |
| #1,757 | +757 | European Stag Beetle | *Lucanus cervus* | 110,958 | 57 |
| #1,778 | +778 | Electric Eel | *Electrophorus electricus* | 108,571 | 74 |
| #1,798 | +798 | Common Wasp | *Vespula vulgaris* | 107,600 | 44 |
| #1,880 | +880 | Giraffe | *Giraffa camelopardalis* | 101,619 | 139 |
| #1,881 | +881 | Common Wombat | *Vombatus ursinus* | 101,608 | 48 |

## 3. Species in Advanced Tier (Ranks 2,001 – 5,000)

| Vwiki Rank | Off by (vs. 1k) | Common Name | Scientific Name | Cumulative Views | Sitelinks |
| :---: | :---: | :--- | :--- | :---: | :---: |
| #2,072 | +1,072 | Red Lionfish | *Pterois volitans* | 89,795 | 47 |
| #2,076 | +1,076 | Giant African Millipede | *Archispirostreptus gigas* | 89,656 | 22 |
| #2,081 | +1,081 | Common Cuttlefish | *Sepia officinalis* | 89,453 | 37 |
| #2,364 | +1,364 | Smooth Newt | *Lissotriton vulgaris* | 76,788 | 51 |
| #2,370 | +1,370 | Spider Monkey | *Ateles geoffroyi* | 76,636 | 44 |
| #2,397 | +1,397 | Giant Moray | *Gymnothorax javanicus* | 75,357 | 24 |
| #2,426 | +1,426 | Pacific Oyster | *Crassostrea gigas* | 74,154 | 32 |
| #2,480 | +1,480 | Dingo | *Canis lupus dingo* | 71,754 | 7 |
| #2,576 | +1,576 | Mexican Redknee Tarantula | *Brachypelma hamorii* | 67,850 | 14 |
| #2,717 | +1,717 | Yellow Tube Sponge | *Aplysina fistularis* | 62,795 | 14 |
| #2,737 | +1,737 | Kiwi | *Apteryx mantelli* | 62,256 | 38 |
| #2,819 | +1,819 | Sea Walnut Comb Jelly | *Mnemiopsis leidyi* | 59,877 | 26 |
| #2,980 | +1,980 | Purple Sea Urchin | *Strongylocentrotus purpuratus* | 55,313 | 16 |
| #3,062 | +2,062 | Howler Monkey | *Alouatta palliata* | 53,292 | 33 |
| #3,101 | +2,101 | Periodical Cicada | *Magicicada septendecim* | 52,279 | 19 |
| #3,200 | +2,200 | Chinchilla | *Chinchilla lanigera* | 49,924 | 40 |
| #3,296 | +2,296 | Tree Kangaroo | *Dendrolagus matschiei* | 47,520 | 35 |
| #3,319 | +2,319 | Common Chameleon | *Chamaeleo chamaeleon* | 47,034 | 40 |
| #3,354 | +2,354 | Common Starfish | *Asterias rubens* | 46,275 | 31 |
| #3,363 | +2,363 | Emperor Dragonfly | *Anax imperator* | 46,106 | 47 |
| #3,410 | +2,410 | African Malaria Mosquito | *Anopheles gambiae* | 45,189 | 21 |
| #3,422 | +2,422 | Common Stingray | *Dasyatis pastinaca* | 45,032 | 38 |
| #3,450 | +2,450 | Sloth | *Bradypus tridactylus* | 44,587 | 40 |
| #3,576 | +2,576 | Slow Loris | *Nycticebus coucang* | 42,464 | 43 |
| #3,581 | +2,581 | Blue-ringed Octopus | *Hapalochlaena maculosa* | 42,263 | 24 |
| #3,802 | +2,802 | Dyeing Dart Frog | *Dendrobates tinctorius* | 38,183 | 32 |
| #3,880 | +2,880 | European Squid | *Loligo vulgaris* | 37,127 | 36 |
| #4,390 | +3,390 | Goliath Beetle | *Goliathus goliatus* | 30,041 | 17 |
| #4,399 | +3,399 | Estuary Seahorse | *Hippocampus kuda* | 29,995 | 25 |
| #4,589 | +3,589 | Green Spotted Puffer | *Tetraodon nigroviridis* | 27,802 | 22 |
| #4,763 | +3,763 | Leafcutter Ant | *Atta cephalotes* | 26,128 | 14 |
| #4,798 | +3,798 | Beadlet Anemone | *Actinia equina* | 25,787 | 31 |

## 4. Species in Master Tier Only (Ranks > 5,000)

These organisms represent specialized microscopic, deep-sea, or obscure biological lineages present in the original 344:

| Vwiki Rank | Off by (vs. 1k) | Common Name | Scientific Name | Cumulative Views | Sitelinks |
| :---: | :---: | :--- | :--- | :---: | :---: |
| #5,212 | +4,212 | Black Sea Cucumber | *Holothuria atra* | 22,616 | 15 |
| #5,472 | +4,472 | Grey Field Slug | *Deroceras reticulatum* | 20,908 | 22 |
| #7,204 | +6,204 | Freshwater Planarian | *Schmidtea mediterranea* | 12,816 | 11 |
| #7,360 | +6,360 | Water Bear Tardigrade | *Hypsibius exemplaris* | 12,277 | 13 |
| #17,314 | +16,314 | Caecilian | *Gymnopis multiplicata* | 2,826 | 17 |
