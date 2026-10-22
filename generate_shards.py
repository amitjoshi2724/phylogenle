import json
import os
import argparse
import time
import requests
import re
import urllib3
import ssl
import sys
import html

# Disable insecure request warnings for TimeTree
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# --- Python 3.13 shim for ete3 (which relies on the removed 'cgi' module) ---
class MockCGI:
    escape = html.escape
sys.modules["cgi"] = MockCGI
from ete3 import NCBITaxa

# Mapping of common names to scientific names for precise lookups
SPECIES_MAP = {
    "Human (Homo sapiens)": "Homo sapiens",
    "Chimpanzee (Pan troglodytes)": "Pan troglodytes",
    "Gorilla (Gorilla gorilla)": "Gorilla gorilla",
    "Orangutan (Pongo pygmaeus)": "Pongo pygmaeus",
    "Macaque (Macaca mulatta)": "Macaca mulatta",
    "Baboon (Papio anubis)": "Papio anubis",
    "Ring-tailed Lemur (Lemur catta)": "Lemur catta",
    "Philippine Tarsier (Carlito syrichta)": "Carlito syrichta",
    "Lion (Panthera leo)": "Panthera leo",
    "Tiger (Panthera tigris)": "Panthera tigris",
    "Leopard (Panthera pardus)": "Panthera pardus",
    "Cheetah (Acinonyx jubatus)": "Acinonyx jubatus",
    "Domestic Cat (Felis catus)": "Felis catus",
    "Cougar (Puma concolor)": "Puma concolor",
    "Jaguar (Panthera onca)": "Panthera onca",
    "Snow Leopard (Panthera uncia)": "Panthera uncia",
    "Lynx (Lynx lynx)": "Lynx lynx",
    "Gray Wolf (Canis lupus)": "Canis lupus",
    "Dog (Canis lupus familiaris)": "Canis lupus familiaris",
    "Red Fox (Vulpes vulpes)": "Vulpes vulpes",
    "Coyote (Canis latrans)": "Canis latrans",
    "Brown Bear (Ursus arctos)": "Ursus arctos",
    "Polar Bear (Ursus maritimus)": "Ursus maritimus",
    "Panda (Ailuropoda melanoleuca)": "Ailuropoda melanoleuca",
    "Raccoon (Procyon lotor)": "Procyon lotor",
    "Hyena (Crocuta crocuta)": "Crocuta crocuta",
    "Domestic Horse (Equus caballus)": "Equus caballus",
    "Plains Zebra (Equus quagga)": "Equus quagga",
    "Donkey (Equus asinus)": "Equus asinus",
    "Domestic Cow (Bos taurus)": "Bos taurus",
    "Domestic Pig (Sus scrofa domesticus)": "Sus scrofa domesticus",
    "Domestic Sheep (Ovis aries)": "Ovis aries",
    "Domestic Goat (Capra hircus)": "Capra hircus",
    "White-tailed Deer (Odocoileus virginianus)": "Odocoileus virginianus",
    "Moose (Alces alces)": "Alces alces",
    "Dromedary Camel (Camelus dromedarius)": "Camelus dromedarius",
    "Llama (Lama glama)": "Lama glama",
    "Giraffe (Giraffa camelopardalis)": "Giraffa camelopardalis",
    "Hippopotamus (Hippopotamus amphibius)": "Hippopotamus amphibius",
    "Rhinoceros (Diceros bicornis)": "Diceros bicornis",
    "Elephant (Loxodonta africana)": "Loxodonta africana",
    "Kangaroo (Macropus rufus)": "Macropus rufus",
    "Koala (Phascolarctos cinereus)": "Phascolarctos cinereus",
    "Platypus (Ornithorhynchus anatinus)": "Ornithorhynchus anatinus",
    "Opossum (Didelphis virginiana)": "Didelphis virginiana",
    "Armadillo (Dasypus novemcinctus)": "Dasypus novemcinctus",
    "Sloth (Bradypus tridactylus)": "Bradypus tridactylus",
    "Rabbit (Oryctolagus cuniculus)": "Oryctolagus cuniculus",
    "Hare (Lepus europaeus)": "Lepus europaeus",
    "Mouse (Mus musculus)": "Mus musculus",
    "Rat (Rattus norvegicus)": "Rattus norvegicus",
    "Guinea Pig (Cavia porcellus)": "Cavia porcellus",
    "Squirrel (Sciurus carolinensis)": "Sciurus carolinensis",
    "Beaver (Castor canadensis)": "Castor canadensis",
    "Porcupine (Erethizon dorsatum)": "Erethizon dorsatum",
    "Bat (Desmodus rotundus)": "Desmodus rotundus",
    "Hedgehog (Erinaceus europaeus)": "Erinaceus europaeus",
    "Mole (Talpa europaea)": "Talpa europaea",
    "Walrus (Odobenus rosmarus)": "Odobenus rosmarus",
    "Seal (Phoca vitulina)": "Phoca vitulina",
    "Bottlenose Dolphin (Tursiops truncatus)": "Tursiops truncatus",
    "Orca (Orcinus orca)": "Orcinus orca",
    "Blue Whale (Balaenoptera musculus)": "Balaenoptera musculus",
    "Humpback Whale (Megaptera novaeangliae)": "Megaptera novaeangliae",
    "Sperm Whale (Physeter macrocephalus)": "Physeter macrocephalus",
    "Manatee (Trichechus manatus)": "Trichechus manatus",
    "Bald Eagle (Haliaeetus leucocephalus)": "Haliaeetus leucocephalus",
    "Red-tailed Hawk (Buteo jamaicensis)": "Buteo jamaicensis",
    "Peregrine Falcon (Falco peregrinus)": "Falco peregrinus",
    "Great Horned Owl (Bubo virginianus)": "Bubo virginianus",
    "Emperor Penguin (Aptenodytes forsteri)": "Aptenodytes forsteri",
    "Ostrich (Struthio camelus)": "Struthio camelus",
    "Emu (Dromaius novaehollandiae)": "Dromaius novaehollandiae",
    "Kiwi (Apteryx mantelli)": "Apteryx mantelli",
    "Domestic Chicken (Gallus gallus domesticus)": "Gallus gallus domesticus",
    "Turkey (Meleagris gallopavo)": "Meleagris gallopavo",
    "Mallard Duck (Anas platyrhynchos)": "Anas platyrhynchos",
    "Greylag Goose (Anser anser)": "Anser anser",
    "Mute Swan (Cygnus olor)": "Cygnus olor",
    "Rock Dove (Columba livia)": "Columba livia",
    "American Crow (Corvus brachyrhynchos)": "Corvus brachyrhynchos",
    "Common Raven (Corvus corax)": "Corvus corax",
    "Scarlet Macaw (Ara macao)": "Ara macao",
    "Ruby-throated Hummingbird (Archilochus colubris)": "Archilochus colubris",
    "Greater Flamingo (Phoenicopterus roseus)": "Phoenicopterus roseus",
    "Indian Peafowl (Pavo cristatus)": "Pavo cristatus",
    "Western Diamondback Rattlesnake (Crotalus atrox)": "Crotalus atrox",
    "Green Iguana (Iguana iguana)": "Iguana iguana",
    "Common Chameleon (Chamaeleo chamaeleon)": "Chamaeleo chamaeleon",
    "Tokay Gecko (Gekko gecko)": "Gekko gecko",
    "Nile Crocodile (Crocodylus niloticus)": "Crocodylus niloticus",
    "American Alligator (Alligator mississippiensis)": "Alligator mississippiensis",
    "Painted Turtle (Chrysemys picta)": "Chrysemys picta",
    "Galapagos Tortoise (Chelonoidis nigra)": "Chelonoidis nigra",
    "Green Sea Turtle (Chelonia mydas)": "Chelonia mydas",
    "Komodo Dragon (Varanus komodoensis)": "Varanus komodoensis",
    "Cobra (Ophiophagus hannah)": "Ophiophagus hannah",
    "Python (Python bivittatus)": "Python bivittatus",
    "Common Frog (Rana temporaria)": "Rana temporaria",
    "Common Toad (Bufo bufo)": "Bufo bufo",
    "Fire Salamander (Salamandra salamandra)": "Salamandra salamandra",
    "Smooth Newt (Lissotriton vulgaris)": "Lissotriton vulgaris",
    "Axolotl (Ambystoma mexicanum)": "Ambystoma mexicanum",
    "Caecilian (Gymnopis multiplicata)": "Gymnopis multiplicata",
    "Great White Shark (Carcharodon carcharias)": "Carcharodon carcharias",
    "Atlantic Bluefin Tuna (Thunnus thynnus)": "Thunnus thynnus",
    "Atlantic Salmon (Salmo salar)": "Salmo salar",
    "Goldfish (Carassius auratus)": "Carassius auratus",
    "Common Carp (Cyprinus carpio)": "Cyprinus carpio",
    "Rainbow Trout (Oncorhynchus mykiss)": "Oncorhynchus mykiss",
    "Largemouth Bass (Micropterus salmoides)": "Micropterus salmoides",
    "Channel Catfish (Ictalurus punctatus)": "Ictalurus punctatus",
    "Green Spotted Puffer (Tetraodon nigroviridis)": "Tetraodon nigroviridis",
    "European Eel (Anguilla anguilla)": "Anguilla anguilla",
    "Common Stingray (Dasyatis pastinaca)": "Dasyatis pastinaca",
    "Estuary Seahorse (Hippocampus kuda)": "Hippocampus kuda",
    "Common Octopus (Octopus vulgaris)": "Octopus vulgaris",
    "European Squid (Loligo vulgaris)": "Loligo vulgaris",
    "Common Cuttlefish (Sepia officinalis)": "Sepia officinalis",
    "Roman Snail (Helix pomatia)": "Helix pomatia",
    "Grey Field Slug (Deroceras reticulatum)": "Deroceras reticulatum",
    "Pacific Oyster (Crassostrea gigas)": "Crassostrea gigas",
    "Hard Clam (Mercenaria mercenaria)": "Mercenaria mercenaria",
    "Blue Crab (Callinectes sapidus)": "Callinectes sapidus",
    "American Lobster (Homarus americanus)": "Homarus americanus",
    "Giant Tiger Prawn (Penaeus monodon)": "Penaeus monodon",
    "Black Widow Spider (Latrodectus mactans)": "Latrodectus mactans",
    "Emperor Scorpion (Pandinus imperator)": "Pandinus imperator",
    "Amazonian Giant Centipede (Scolopendra gigantea)": "Scolopendra gigantea",
    "Giant African Millipede (Archispirostreptus gigas)": "Archispirostreptus gigas",
    "Red Imported Fire Ant (Solenopsis invicta)": "Solenopsis invicta",
    "Western Honey Bee (Apis mellifera)": "Apis mellifera",
    "Common Wasp (Vespula vulgaris)": "Vespula vulgaris",
    "Monarch Butterfly (Danaus plexippus)": "Danaus plexippus",
    "Domestic Silk Moth (Bombyx mori)": "Bombyx mori",
    "Seven-spot Ladybird (Coccinella septempunctata)": "Coccinella septempunctata",
    "Housefly (Musca domestica)": "Musca domestica",
    "African Malaria Mosquito (Anopheles gambiae)": "Anopheles gambiae",
    "American Cockroach (Periplaneta americana)": "Periplaneta americana",
    "Common Earthworm (Lumbricus terrestris)": "Lumbricus terrestris",
    "Moon Jelly (Aurelia aurita)": "Aurelia aurita",
    "Common Starfish (Asterias rubens)": "Asterias rubens",
    "Purple Sea Urchin (Strongylocentrotus purpuratus)": "Strongylocentrotus purpuratus",
    "Sea Otter (Enhydra lutris)": "Enhydra lutris",
    "River Otter (Lontra canadensis)": "Lontra canadensis",
    "Giant Otter (Pteronura brasiliensis)": "Pteronura brasiliensis",
    "Red Panda (Ailurus fulgens)": "Ailurus fulgens",
    "Meerkat (Suricata suricatta)": "Suricata suricatta",
    "Wolverine (Gulo gulo)": "Gulo gulo",
    "Honey Badger (Mellivora capensis)": "Mellivora capensis",
    "European Badger (Meles meles)": "Meles meles",
    "Striped Skunk (Mephitis mephitis)": "Mephitis mephitis",
    "Fennec Fox (Vulpes zerda)": "Vulpes zerda",
    "Arctic Fox (Vulpes lagopus)": "Vulpes lagopus",
    "African Wild Dog (Lycaon pictus)": "Lycaon pictus",
    "Dingo (Canis lupus dingo)": "Canis lupus dingo",
    "American Black Bear (Ursus americanus)": "Ursus americanus",
    "Sun Bear (Helarctos malayanus)": "Helarctos malayanus",
    "Sloth Bear (Melursus ursinus)": "Melursus ursinus",
    "Spectacled Bear (Tremarctos ornatus)": "Tremarctos ornatus",
    "Leopard Seal (Hydrurga leptonyx)": "Hydrurga leptonyx",
    "California Sea Lion (Zalophus californianus)": "Zalophus californianus",
    "Ringed Seal (Pusa hispida)": "Pusa hispida",
    "Striped Hyena (Hyaena hyaena)": "Hyaena hyaena",
    "Binturong (Arctictis binturong)": "Arctictis binturong",
    "Caracal (Caracal caracal)": "Caracal caracal",
    "Serval (Leptailurus serval)": "Leptailurus serval",
    "Ocelot (Leopardus pardalis)": "Leopardus pardalis",
    "Clouded Leopard (Neofelis nebulosa)": "Neofelis nebulosa",
    "Jaguarundi (Herpailurus yagouaroundi)": "Herpailurus yagouaroundi",
    "Bonobo (Pan paniscus)": "Pan paniscus",
    "Mandrill (Mandrillus sphinx)": "Mandrillus sphinx",
    "Proboscis Monkey (Nasalis larvatus)": "Nasalis larvatus",
    "Golden Lion Tamarin (Leontopithecus rosalia)": "Leontopithecus rosalia",
    "Pygmy Marmoset (Cebuella pygmaea)": "Cebuella pygmaea",
    "Aye-aye (Daubentonia madagascariensis)": "Daubentonia madagascariensis",
    "Slow Loris (Nycticebus coucang)": "Nycticebus coucang",
    "Gelada (Theropithecus gelada)": "Theropithecus gelada",
    "Siamang (Symphalangus syndactylus)": "Symphalangus syndactylus",
    "White-handed Gibbon (Hylobates lar)": "Hylobates lar",
    "Spider Monkey (Ateles geoffroyi)": "Ateles geoffroyi",
    "Howler Monkey (Alouatta palliata)": "Alouatta palliata",
    "Narwhal (Monodon monoceros)": "Monodon monoceros",
    "Beluga Whale (Delphinapterus leucas)": "Delphinapterus leucas",
    "Bowhead Whale (Balaena mysticetus)": "Balaena mysticetus",
    "Harbor Porpoise (Phocoena phocoena)": "Phocoena phocoena",
    "Gray Whale (Eschrichtius robustus)": "Eschrichtius robustus",
    "Fin Whale (Balaenoptera physalus)": "Balaenoptera physalus",
    "Dugong (Dugong dugon)": "Dugong dugon",
    "American Bison (Bison bison)": "Bison bison",
    "Cape Buffalo (Syncerus caffer)": "Syncerus caffer",
    "Okapi (Okapia johnstoni)": "Okapia johnstoni",
    "Bighorn Sheep (Ovis canadensis)": "Ovis canadensis",
    "Mountain Goat (Oreamnos americanus)": "Oreamnos americanus",
    "Muskox (Ovibos moschatus)": "Ovibos moschatus",
    "Reindeer (Rangifer tarandus)": "Rangifer tarandus",
    "Red Deer (Cervus elaphus)": "Cervus elaphus",
    "Common Warthog (Phacochoerus africanus)": "Phacochoerus africanus",
    "Wild Boar (Sus scrofa)": "Sus scrofa",
    "White Rhinoceros (Ceratotherium simum)": "Ceratotherium simum",
    "Indian Rhinoceros (Rhinoceros unicornis)": "Rhinoceros unicornis",
    "Asian Elephant (Elephas maximus)": "Elephas maximus",
    "Aardvark (Orycteropus afer)": "Orycteropus afer",
    "Giant Anteater (Myrmecophaga tridactyla)": "Myrmecophaga tridactyla",
    "Malayan Tapir (Tapirus indicus)": "Tapirus indicus",
    "Pronghorn (Antilocapra americana)": "Antilocapra americana",
    "Alpaca (Vicugna pacos)": "Vicugna pacos",
    "Vicuña (Vicugna vicugna)": "Vicugna vicugna",
    "Short-beaked Echidna (Tachyglossus aculeatus)": "Tachyglossus aculeatus",
    "Tasmanian Devil (Sarcophilus harrisii)": "Sarcophilus harrisii",
    "Common Wombat (Vombatus ursinus)": "Vombatus ursinus",
    "Sugar Glider (Petaurus breviceps)": "Petaurus breviceps",
    "Quokka (Setonix brachyurus)": "Setonix brachyurus",
    "Common Brushtail Possum (Trichosurus vulpecula)": "Trichosurus vulpecula",
    "Eastern Grey Kangaroo (Macropus giganteus)": "Macropus giganteus",
    "Numbat (Myrmecobius fasciatus)": "Myrmecobius fasciatus",
    "Tree Kangaroo (Dendrolagus matschiei)": "Dendrolagus matschiei",
    "Capybara (Hydrochoerus hydrochaeris)": "Hydrochoerus hydrochaeris",
    "Groundhog (Marmota monax)": "Marmota monax",
    "Black-tailed Prairie Dog (Cynomys ludovicianus)": "Cynomys ludovicianus",
    "Chinchilla (Chinchilla lanigera)": "Chinchilla lanigera",
    "Naked Mole-rat (Heterocephalus glaber)": "Heterocephalus glaber",
    "Eurasian Red Squirrel (Sciurus vulgaris)": "Sciurus vulgaris",
    "Giant Golden-crowned Flying Fox (Acerodon jubatus)": "Acerodon jubatus",
    "Little Brown Bat (Myotis lucifugus)": "Myotis lucifugus",
    "Harpy Eagle (Harpia harpyja)": "Harpia harpyja",
    "Golden Eagle (Aquila chrysaetos)": "Aquila chrysaetos",
    "Osprey (Pandion haliaetus)": "Pandion haliaetus",
    "Barn Owl (Tyto alba)": "Tyto alba",
    "Snowy Owl (Bubo scandiacus)": "Bubo scandiacus",
    "Burrowing Owl (Athene cunicularia)": "Athene cunicularia",
    "Andean Condor (Vultur gryphus)": "Vultur gryphus",
    "Secretarybird (Sagittarius serpentarius)": "Sagittarius serpentarius",
    "Atlantic Puffin (Fratercula arctica)": "Fratercula arctica",
    "Wandering Albatross (Diomedea exulans)": "Diomedea exulans",
    "Shoebill (Balaeniceps rex)": "Balaeniceps rex",
    "King Penguin (Aptenodytes patagonicus)": "Aptenodytes patagonicus",
    "Gentoo Penguin (Pygoscelis papua)": "Pygoscelis papua",
    "Great Blue Heron (Ardea herodias)": "Ardea herodias",
    "Roseate Spoonbill (Platalea ajaja)": "Platalea ajaja",
    "Brown Pelican (Pelecanus occidentalis)": "Pelecanus occidentalis",
    "Common Loon (Gavia immer)": "Gavia immer",
    "Great Cormorant (Phalacrocorax carbo)": "Phalacrocorax carbo",
    "Canada Goose (Branta canadensis)": "Branta canadensis",
    "Whooper Swan (Cygnus cygnus)": "Cygnus cygnus",
    "Wood Duck (Aix sponsa)": "Aix sponsa",
    "Southern Cassowary (Casuarius casuarius)": "Casuarius casuarius",
    "Ring-necked Pheasant (Phasianus colchicus)": "Phasianus colchicus",
    "California Quail (Callipepla californica)": "Callipepla californica",
    "Common Kingfisher (Alcedo atthis)": "Alcedo atthis",
    "Toco Toucan (Ramphastos toco)": "Ramphastos toco",
    "Pileated Woodpecker (Dryocopus pileatus)": "Dryocopus pileatus",
    "Kakapo (Strigops habroptila)": "Strigops habroptila",
    "Kea (Nestor notabilis)": "Nestor notabilis",
    "Budgerigar (Melopsittacus undulatus)": "Melopsittacus undulatus",
    "Cockatiel (Nymphicus hollandicus)": "Nymphicus hollandicus",
    "Blue Jay (Cyanocitta cristata)": "Cyanocitta cristata",
    "Northern Cardinal (Cardinalis cardinalis)": "Cardinalis cardinalis",
    "Eurasian Magpie (Pica pica)": "Pica pica",
    "European Robin (Erithacus rubecula)": "Erithacus rubecula",
    "House Sparrow (Passer domesticus)": "Passer domesticus",
    "Common Starling (Sturnus vulgaris)": "Sturnus vulgaris",
    "Gila Monster (Heloderma suspectum)": "Heloderma suspectum",
    "Leatherback Sea Turtle (Dermochelys coriacea)": "Dermochelys coriacea",
    "Hawksbill Sea Turtle (Eretmochelys imbricata)": "Eretmochelys imbricata",
    "Loggerhead Sea Turtle (Caretta caretta)": "Caretta caretta",
    "Alligator Snapping Turtle (Macrochelys temminckii)": "Macrochelys temminckii",
    "Eastern Box Turtle (Terrapene carolina)": "Terrapene carolina",
    "Green Anaconda (Eunectes murinus)": "Eunectes murinus",
    "Black Mamba (Dendroaspis polylepis)": "Dendroaspis polylepis",
    "Corn Snake (Pantherophis guttatus)": "Pantherophis guttatus",
    "Ball Python (Python regius)": "Python regius",
    "Copperhead (Agkistrodon contortrix)": "Agkistrodon contortrix",
    "Inland Taipan (Oxyuranus microlepidotus)": "Oxyuranus microlepidotus",
    "Central Bearded Dragon (Pogona vitticeps)": "Pogona vitticeps",
    "Marine Iguana (Amblyrhynchus cristatus)": "Amblyrhynchus cristatus",
    "Thorny Devil (Moloch horridus)": "Moloch horridus",
    "Frilled Lizard (Chlamydosaurus kingii)": "Chlamydosaurus kingii",
    "Leopard Gecko (Eublepharis macularius)": "Eublepharis macularius",
    "Tuatara (Sphenodon punctatus)": "Sphenodon punctatus",
    "Saltwater Crocodile (Crocodylus porosus)": "Crocodylus porosus",
    "Gharial (Gavialis gangeticus)": "Gavialis gangeticus",
    "Dyeing Dart Frog (Dendrobates tinctorius)": "Dendrobates tinctorius",
    "Golden Poison Frog (Phyllobates terribilis)": "Phyllobates terribilis",
    "Goliath Frog (Conraua goliath)": "Conraua goliath",
    "American Bullfrog (Lithobates catesbeianus)": "Lithobates catesbeianus",
    "Red-eyed Tree Frog (Agalychnis callidryas)": "Agalychnis callidryas",
    "Hellbender (Cryptobranchus alleganiensis)": "Cryptobranchus alleganiensis",
    "Japanese Giant Salamander (Andrias japonicus)": "Andrias japonicus",
    "Cane Toad (Rhinella marina)": "Rhinella marina",
    "African Clawed Frog (Xenopus laevis)": "Xenopus laevis",
    "Olm Salamander (Proteus anguinus)": "Proteus anguinus",
    "Whale Shark (Rhincodon typus)": "Rhincodon typus",
    "Great Hammerhead Shark (Sphyrna mokarran)": "Sphyrna mokarran",
    "Tiger Shark (Galeocerdo cuvier)": "Galeocerdo cuvier",
    "Basking Shark (Cetorhinus maximus)": "Cetorhinus maximus",
    "Giant Oceanic Manta Ray (Mobula birostris)": "Mobula birostris",
    "Coelacanth (Latimeria chalumnae)": "Latimeria chalumnae",
    "Alligator Gar (Atractosteus spatula)": "Atractosteus spatula",
    "Ocellaris Clownfish (Amphiprion ocellaris)": "Amphiprion ocellaris",
    "Deep-sea Anglerfish (Melanocetus johnsonii)": "Melanocetus johnsonii",
    "Great Barracuda (Sphyraena barracuda)": "Sphyraena barracuda",
    "Giant Moray (Gymnothorax javanicus)": "Gymnothorax javanicus",
    "Ocean Sunfish (Mola mola)": "Mola mola",
    "Swordfish (Xiphias gladius)": "Xiphias gladius",
    "Atlantic Cod (Gadus morhua)": "Gadus morhua",
    "Red Lionfish (Pterois volitans)": "Pterois volitans",
    "Regal Blue Tang (Paracanthurus hepatus)": "Paracanthurus hepatus",
    "Red-bellied Piranha (Pygocentrus nattereri)": "Pygocentrus nattereri",
    "Arapaima (Arapaima gigas)": "Arapaima gigas",
    "Northern Pike (Esox lucius)": "Esox lucius",
    "Electric Eel (Electrophorus electricus)": "Electrophorus electricus",
    "Siamese Fighting Fish (Betta splendens)": "Betta splendens",
    "Peacock Mantis Shrimp (Odontodactylus scyllarus)": "Odontodactylus scyllarus",
    "European Praying Mantis (Mantis religiosa)": "Mantis religiosa",
    "Leafcutter Ant (Atta cephalotes)": "Atta cephalotes",
    "Buff-tailed Bumblebee (Bombus terrestris)": "Bombus terrestris",
    "Emperor Dragonfly (Anax imperator)": "Anax imperator",
    "Atlas Moth (Attacus atlas)": "Attacus atlas",
    "Periodical Cicada (Magicicada septendecim)": "Magicicada septendecim",
    "European Stag Beetle (Lucanus cervus)": "Lucanus cervus",
    "Goliath Beetle (Goliathus goliatus)": "Goliathus goliatus",
    "Mexican Redknee Tarantula (Brachypelma hamorii)": "Brachypelma hamorii",
    "Sydney Funnel-web Spider (Atrax robustus)": "Atrax robustus",
    "Atlantic Horseshoe Crab (Limulus polyphemus)": "Limulus polyphemus",
    "Fiddler Crab (Uca pugilator)": "Uca pugilator",
    "Coconut Crab (Birgus latro)": "Birgus latro",
    "Giant Pacific Octopus (Enteroctopus dofleini)": "Enteroctopus dofleini",
    "Blue-ringed Octopus (Hapalochlaena maculosa)": "Hapalochlaena maculosa",
    "Giant Squid (Architeuthis dux)": "Architeuthis dux",
    "Colossal Squid (Mesonychoteuthis hamiltoni)": "Mesonychoteuthis hamiltoni",
    "Chambered Nautilus (Nautilus pompilius)": "Nautilus pompilius",
    "Giant Clam (Tridacna gigas)": "Tridacna gigas",
    "Beadlet Anemone (Actinia equina)": "Actinia equina",
    "Sea Wasp Box Jellyfish (Chironex fleckeri)": "Chironex fleckeri",
    "Portuguese Man o War (Physalia physalis)": "Physalia physalis",
    "Lions Mane Jellyfish (Cyanea capillata)": "Cyanea capillata",
    "Crown-of-thorns Starfish (Acanthaster planci)": "Acanthaster planci",
    "Black Sea Cucumber (Holothuria atra)": "Holothuria atra",
    "Sea Walnut Comb Jelly (Mnemiopsis leidyi)": "Mnemiopsis leidyi",
    "Yellow Tube Sponge (Aplysina fistularis)": "Aplysina fistularis",
    "Freshwater Planarian (Schmidtea mediterranea)": "Schmidtea mediterranea",
    "Water Bear Tardigrade (Hypsibius exemplaris)": "Hypsibius exemplaris",
}

def get_divergence_time(taxid1: int, taxid2: int, species1_sci: str, species2_sci: str, retries=3) -> float:
    """Uses TimeTree to get the median divergence time between two species using TaxIDs."""
    if taxid1 == taxid2:
        return 0.0
    
    url = f"http://www.timetree.org/ajax/pairwise/{taxid1}/{taxid2}"
    headers = {"User-Agent": "Mozilla/5.0"}
    
    for attempt in range(retries):
        try:
            resp = requests.get(url, headers=headers, verify=False, timeout=30)
            # TimeTree returns HTML containing the time
            match = re.search(r"Median Time:.*?>([\d\.]+)\s*MYA<", resp.text, re.IGNORECASE | re.DOTALL)
            if not match:
                match = re.search(r"Median Time:.*?<br>\s*([\d\.]+)\s*MYA", resp.text, re.IGNORECASE | re.DOTALL)
            if not match:
                # Also try the other pattern seen in TimeTree's HTML
                match = re.search(r"Median Time:.*?([\d\.]+)\s*MYA", resp.text, re.IGNORECASE | re.DOTALL)
                
            if match:
                return float(match.group(1))
            return -1.0 # Parsed successfully but no time found
        except requests.exceptions.Timeout:
            print(f"Timeout on attempt {attempt + 1} for {species1_sci} vs {species2_sci}")
            time.sleep(2)
        except Exception as e:
            print(f"Error fetching TimeTree for {species1_sci} vs {species2_sci}: {e}")
            time.sleep(2)
            
    return -1.0 # Unknown or failed after retries

def get_lca_info(ncbi: NCBITaxa, species1_sci: str, species2_sci: str) -> dict:
    """Uses ete3 and NCBI Taxonomy to find the rank and name of the Lowest Common Ancestor."""
    if species1_sci == species2_sci:
        return {"rank": "Species", "name": species1_sci}
        
    try:
        # Get Tax IDs
        name_map1 = ncbi.get_name_translator([species1_sci])
        name_map2 = ncbi.get_name_translator([species2_sci])
        
        if not name_map1 or not name_map2:
            return {"rank": "Unknown", "name": "Unknown"}
            
        taxid1 = name_map1[species1_sci][0]
        taxid2 = name_map2[species2_sci][0]
        
        lin1 = ncbi.get_lineage(taxid1)
        lin2 = ncbi.get_lineage(taxid2)
        
        # Find LCA ID
        lca_id = None
        for t1, t2 in zip(lin1, lin2):
            if t1 == t2: lca_id = t1
            else: break
            
        if lca_id:
            major_ranks = ["superkingdom", "kingdom", "phylum", "class", "order", "family", "genus", "species"]
            # Find the closest major rank going up the tree from the LCA
            for t in reversed(lin1[:lin1.index(lca_id)+1]):
                rank = ncbi.get_rank([t]).get(t, "")
                if rank in major_ranks:
                    rank_name = ncbi.get_taxid_translator([t]).get(t, "Unknown")
                    return {"rank": rank.capitalize(), "name": rank_name}
                    
    except Exception as e:
        print(f"Error fetching Taxonomy for {species1_sci} vs {species2_sci}: {e}")
        
    return {"rank": "Unknown", "name": "Unknown"}

def generate_shards(output_dir: str):
    """
    Generates JSON shards for every species using real Data (TimeTree and NCBI).
    Each shard contains the divergence time and LCA rank to every other species.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    print("Initializing NCBI Taxonomy Database (this may take a moment to download if first time)...")
    # Apply SSL workaround for NCBI download if needed
    ssl._create_default_https_context = ssl._create_unverified_context
    ncbi = NCBITaxa()
    
    species_list = list(SPECIES_MAP.keys())
    
    print(f"Generating data for {len(species_list)} species...")
    print(f"Total pairs to calculate: {len(species_list) * len(species_list)}")
    
    # Cache time queries to avoid duplicate external requests (A->B is same as B->A)
    cache_path = os.path.join(output_dir, "time_cache.json")
    time_cache = {}
    if os.path.exists(cache_path):
        try:
            with open(cache_path, 'r') as f:
                time_cache = json.load(f)
            print(f"Loaded {len(time_cache)} cached pair divergence times.")
        except:
            pass
    
    print("Mapping species to NCBI Taxon IDs...")
    species_to_taxid = {}
    for name in species_list:
        sci = SPECIES_MAP[name]
        try:
            name_map = ncbi.get_name_translator([sci])
            if name_map:
                species_to_taxid[sci] = name_map[sci][0]
        except:
            pass

    total_species = len(species_list)
    for i, target_species in enumerate(species_list):
        target_sci = SPECIES_MAP[target_species]
        target_taxid = species_to_taxid.get(target_sci)
        shard_data = {}
        print(f"\n--- Processing {i+1}/{total_species}: {target_species} ---")
        
        for other_species in species_list:
            other_sci = SPECIES_MAP[other_species]
            other_taxid = species_to_taxid.get(other_sci)
            
            # Determine Time
            if not target_taxid or not other_taxid:
                time_val = -1.0
            else:
                pair_key = tuple(sorted([target_sci, other_sci]))
                cache_key = f"{pair_key[0]}||{pair_key[1]}"
                if cache_key in time_cache:
                    time_val = time_cache[cache_key]
                else:
                    print(f"    Fetching API: {target_species} vs {other_species}...", end="", flush=True)
                    time_val = get_divergence_time(target_taxid, other_taxid, target_sci, other_sci)
                    print(f" Done ({time_val} MYA)")
                    time_cache[cache_key] = time_val
                    # Save cache incrementally
                    with open(cache_path, 'w') as f:
                        json.dump(time_cache, f)
                    # Sleep briefly to be nice to TimeTree API
                    time.sleep(0.5)
                
            # Determine Rank
            lca_info = get_lca_info(ncbi, target_sci, other_sci)
            
            shard_data[other_species.lower()] = {
                "time": time_val,
                "rank": lca_info["rank"],
                "lca_name": lca_info["name"]
            }
            
        # Write shard to file
        filename = target_species.lower().replace(" ", "_") + ".json"
        filepath = os.path.join(output_dir, filename)
        
        with open(filepath, 'w') as f:
            json.dump(shard_data, f, indent=2)
            
        print(f"Created shard: {filename}")
        
    # Create the master list of species
    master_list_path = os.path.join(output_dir, "species_list.json")
    with open(master_list_path, 'w') as f:
        json.dump(species_list, f, indent=2)
    print("Created species_list.json")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate data shards for Phylogenle.")
    parser.add_argument("--output", default="data", help="Output directory for shards")
    args = parser.parse_args()
    
    generate_shards(args.output)
    print("Done!")
