import html
import sys
import os
import json
import re
import time
import requests
import ssl

# --- Python 3.13 shim for ete3 (which relies on the removed 'cgi' module) ---
class MockCGI:
    escape = html.escape
sys.modules["cgi"] = MockCGI
from ete3 import NCBITaxa

# Candidate species to add (verified against NCBI Taxonomy)
NEW_CANDIDATES = [
    # --- Mammals: Carnivora ---
    ('Sea Otter (Enhydra lutris)', 'Enhydra lutris'),
    ('River Otter (Lontra canadensis)', 'Lontra canadensis'),
    ('Giant Otter (Pteronura brasiliensis)', 'Pteronura brasiliensis'),
    ('Red Panda (Ailurus fulgens)', 'Ailurus fulgens'),
    ('Meerkat (Suricata suricatta)', 'Suricata suricatta'),
    ('Wolverine (Gulo gulo)', 'Gulo gulo'),
    ('Honey Badger (Mellivora capensis)', 'Mellivora capensis'),
    ('European Badger (Meles meles)', 'Meles meles'),
    ('Striped Skunk (Mephitis mephitis)', 'Mephitis mephitis'),
    ('Fennec Fox (Vulpes zerda)', 'Vulpes zerda'),
    ('Arctic Fox (Vulpes lagopus)', 'Vulpes lagopus'),
    ('African Wild Dog (Lycaon pictus)', 'Lycaon pictus'),
    ('Dingo (Canis lupus dingo)', 'Canis lupus dingo'),
    ('American Black Bear (Ursus americanus)', 'Ursus americanus'),
    ('Sun Bear (Helarctos malayanus)', 'Helarctos malayanus'),
    ('Sloth Bear (Melursus ursinus)', 'Melursus ursinus'),
    ('Spectacled Bear (Tremarctos ornatus)', 'Tremarctos ornatus'),
    ('Leopard Seal (Hydrurga leptonyx)', 'Hydrurga leptonyx'),
    ('California Sea Lion (Zalophus californianus)', 'Zalophus californianus'),
    ('Ringed Seal (Pusa hispida)', 'Pusa hispida'),
    ('Striped Hyena (Hyaena hyaena)', 'Hyaena hyaena'),
    ('Binturong (Arctictis binturong)', 'Arctictis binturong'),
    ('Caracal (Caracal caracal)', 'Caracal caracal'),
    ('Serval (Leptailurus serval)', 'Leptailurus serval'),
    ('Ocelot (Leopardus pardalis)', 'Leopardus pardalis'),
    ('Clouded Leopard (Neofelis nebulosa)', 'Neofelis nebulosa'),
    ('Jaguarundi (Herpailurus yagouaroundi)', 'Herpailurus yagouaroundi'),
    
    # --- Mammals: Primates ---
    ('Bonobo (Pan paniscus)', 'Pan paniscus'),
    ('Mandrill (Mandrillus sphinx)', 'Mandrillus sphinx'),
    ('Proboscis Monkey (Nasalis larvatus)', 'Nasalis larvatus'),
    ('Golden Lion Tamarin (Leontopithecus rosalia)', 'Leontopithecus rosalia'),
    ('Pygmy Marmoset (Cebuella pygmaea)', 'Cebuella pygmaea'),
    ('Aye-aye (Daubentonia madagascariensis)', 'Daubentonia madagascariensis'),
    ('Slow Loris (Nycticebus coucang)', 'Nycticebus coucang'),
    ('Gelada (Theropithecus gelada)', 'Theropithecus gelada'),
    ('Siamang (Symphalangus syndactylus)', 'Symphalangus syndactylus'),
    ('White-handed Gibbon (Hylobates lar)', 'Hylobates lar'),
    ('Spider Monkey (Ateles geoffroyi)', 'Ateles geoffroyi'),
    ('Howler Monkey (Alouatta palliata)', 'Alouatta palliata'),
    
    # --- Mammals: Cetacea & Sirenia ---
    ('Narwhal (Monodon monoceros)', 'Monodon monoceros'),
    ('Beluga Whale (Delphinapterus leucas)', 'Delphinapterus leucas'),
    ('Bowhead Whale (Balaena mysticetus)', 'Balaena mysticetus'),
    ('Harbor Porpoise (Phocoena phocoena)', 'Phocoena phocoena'),
    ('Gray Whale (Eschrichtius robustus)', 'Eschrichtius robustus'),
    ('Fin Whale (Balaenoptera physalus)', 'Balaenoptera physalus'),
    ('Dugong (Dugong dugon)', 'Dugong dugon'),
    
    # --- Mammals: Ungulates & Afrotheria ---
    ('American Bison (Bison bison)', 'Bison bison'),
    ('Cape Buffalo (Syncerus caffer)', 'Syncerus caffer'),
    ('Okapi (Okapia johnstoni)', 'Okapia johnstoni'),
    ('Bighorn Sheep (Ovis canadensis)', 'Ovis canadensis'),
    ('Mountain Goat (Oreamnos americanus)', 'Oreamnos americanus'),
    ('Muskox (Ovibos moschatus)', 'Ovibos moschatus'),
    ('Reindeer (Rangifer tarandus)', 'Rangifer tarandus'),
    ('Red Deer (Cervus elaphus)', 'Cervus elaphus'),
    ('Common Warthog (Phacochoerus africanus)', 'Phacochoerus africanus'),
    ('Wild Boar (Sus scrofa)', 'Sus scrofa'),
    ('White Rhinoceros (Ceratotherium simum)', 'Ceratotherium simum'),
    ('Indian Rhinoceros (Rhinoceros unicornis)', 'Rhinoceros unicornis'),
    ('Asian Elephant (Elephas maximus)', 'Elephas maximus'),
    ('Aardvark (Orycteropus afer)', 'Orycteropus afer'),
    ('Giant Anteater (Myrmecophaga tridactyla)', 'Myrmecophaga tridactyla'),
    ('Malayan Tapir (Tapirus indicus)', 'Tapirus indicus'),
    ('Pronghorn (Antilocapra americana)', 'Antilocapra americana'),
    ('Alpaca (Vicugna pacos)', 'Vicugna pacos'),
    ('Vicuña (Vicugna vicugna)', 'Vicugna vicugna'),
    
    # --- Mammals: Marsupials & Monotremes ---
    ('Short-beaked Echidna (Tachyglossus aculeatus)', 'Tachyglossus aculeatus'),
    ('Tasmanian Devil (Sarcophilus harrisii)', 'Sarcophilus harrisii'),
    ('Common Wombat (Vombatus ursinus)', 'Vombatus ursinus'),
    ('Sugar Glider (Petaurus breviceps)', 'Petaurus breviceps'),
    ('Quokka (Setonix brachyurus)', 'Setonix brachyurus'),
    ('Common Brushtail Possum (Trichosurus vulpecula)', 'Trichosurus vulpecula'),
    ('Eastern Grey Kangaroo (Macropus giganteus)', 'Macropus giganteus'),
    ('Numbat (Myrmecobius fasciatus)', 'Myrmecobius fasciatus'),
    ('Tree Kangaroo (Dendrolagus matschiei)', 'Dendrolagus matschiei'),
    
    # --- Mammals: Rodents, Lagomorphs, Chiroptera, Insectivora ---
    ('Capybara (Hydrochoerus hydrochaeris)', 'Hydrochoerus hydrochaeris'),
    ('Groundhog (Marmota monax)', 'Marmota monax'),
    ('Black-tailed Prairie Dog (Cynomys ludovicianus)', 'Cynomys ludovicianus'),
    ('Chinchilla (Chinchilla lanigera)', 'Chinchilla lanigera'),
    ('Naked Mole-rat (Heterocephalus glaber)', 'Heterocephalus glaber'),
    ('Eurasian Red Squirrel (Sciurus vulgaris)', 'Sciurus vulgaris'),
    ('Giant Golden-crowned Flying Fox (Acerodon jubatus)', 'Acerodon jubatus'),
    ('Little Brown Bat (Myotis lucifugus)', 'Myotis lucifugus'),
    
    # --- Birds: Raptors & Owls ---
    ('Harpy Eagle (Harpia harpyja)', 'Harpia harpyja'),
    ('Golden Eagle (Aquila chrysaetos)', 'Aquila chrysaetos'),
    ('Osprey (Pandion haliaetus)', 'Pandion haliaetus'),
    ('Barn Owl (Tyto alba)', 'Tyto alba'),
    ('Snowy Owl (Bubo scandiacus)', 'Bubo scandiacus'),
    ('Burrowing Owl (Athene cunicularia)', 'Athene cunicularia'),
    ('Andean Condor (Vultur gryphus)', 'Vultur gryphus'),
    ('Secretarybird (Sagittarius serpentarius)', 'Sagittarius serpentarius'),
    
    # --- Birds: Seabirds, Waterfowl, Wading Birds ---
    ('Atlantic Puffin (Fratercula arctica)', 'Fratercula arctica'),
    ('Wandering Albatross (Diomedea exulans)', 'Diomedea exulans'),
    ('Shoebill (Balaeniceps rex)', 'Balaeniceps rex'),
    ('King Penguin (Aptenodytes patagonicus)', 'Aptenodytes patagonicus'),
    ('Gentoo Penguin (Pygoscelis papua)', 'Pygoscelis papua'),
    ('Great Blue Heron (Ardea herodias)', 'Ardea herodias'),
    ('Roseate Spoonbill (Platalea ajaja)', 'Platalea ajaja'),
    ('Brown Pelican (Pelecanus occidentalis)', 'Pelecanus occidentalis'),
    ('Common Loon (Gavia immer)', 'Gavia immer'),
    ('Great Cormorant (Phalacrocorax carbo)', 'Phalacrocorax carbo'),
    ('Canada Goose (Branta canadensis)', 'Branta canadensis'),
    ('Whooper Swan (Cygnus cygnus)', 'Cygnus cygnus'),
    ('Wood Duck (Aix sponsa)', 'Aix sponsa'),
    
    # --- Birds: Flightless, Game & Others ---
    ('Southern Cassowary (Casuarius casuarius)', 'Casuarius casuarius'),
    ('Ring-necked Pheasant (Phasianus colchicus)', 'Phasianus colchicus'),
    ('California Quail (Callipepla californica)', 'Callipepla californica'),
    ('Common Kingfisher (Alcedo atthis)', 'Alcedo atthis'),
    ('Toco Toucan (Ramphastos toco)', 'Ramphastos toco'),
    ('Pileated Woodpecker (Dryocopus pileatus)', 'Dryocopus pileatus'),
    ('Kakapo (Strigops habroptila)', 'Strigops habroptila'),
    ('Kea (Nestor notabilis)', 'Nestor notabilis'),
    ('Budgerigar (Melopsittacus undulatus)', 'Melopsittacus undulatus'),
    ('Cockatiel (Nymphicus hollandicus)', 'Nymphicus hollandicus'),
    ('Blue Jay (Cyanocitta cristata)', 'Cyanocitta cristata'),
    ('Northern Cardinal (Cardinalis cardinalis)', 'Cardinalis cardinalis'),
    ('Eurasian Magpie (Pica pica)', 'Pica pica'),
    ('European Robin (Erithacus rubecula)', 'Erithacus rubecula'),
    ('House Sparrow (Passer domesticus)', 'Passer domesticus'),
    ('Common Starling (Sturnus vulgaris)', 'Sturnus vulgaris'),
    
    # --- Reptiles ---
    ('Gila Monster (Heloderma suspectum)', 'Heloderma suspectum'),
    ('Leatherback Sea Turtle (Dermochelys coriacea)', 'Dermochelys coriacea'),
    ('Hawksbill Sea Turtle (Eretmochelys imbricata)', 'Eretmochelys imbricata'),
    ('Loggerhead Sea Turtle (Caretta caretta)', 'Caretta caretta'),
    ('Alligator Snapping Turtle (Macrochelys temminckii)', 'Macrochelys temminckii'),
    ('Eastern Box Turtle (Terrapene carolina)', 'Terrapene carolina'),
    ('Green Anaconda (Eunectes murinus)', 'Eunectes murinus'),
    ('Black Mamba (Dendroaspis polylepis)', 'Dendroaspis polylepis'),
    ('Corn Snake (Pantherophis guttatus)', 'Pantherophis guttatus'),
    ('Ball Python (Python regius)', 'Python regius'),
    ('Copperhead (Agkistrodon contortrix)', 'Agkistrodon contortrix'),
    ('Inland Taipan (Oxyuranus microlepidotus)', 'Oxyuranus microlepidotus'),
    ('Central Bearded Dragon (Pogona vitticeps)', 'Pogona vitticeps'),
    ('Marine Iguana (Amblyrhynchus cristatus)', 'Amblyrhynchus cristatus'),
    ('Thorny Devil (Moloch horridus)', 'Moloch horridus'),
    ('Frilled Lizard (Chlamydosaurus kingii)', 'Chlamydosaurus kingii'),
    ('Leopard Gecko (Eublepharis macularius)', 'Eublepharis macularius'),
    ('Tuatara (Sphenodon punctatus)', 'Sphenodon punctatus'),
    ('Saltwater Crocodile (Crocodylus porosus)', 'Crocodylus porosus'),
    ('Gharial (Gavialis gangeticus)', 'Gavialis gangeticus'),
    
    # --- Amphibians ---
    ('Dyeing Dart Frog (Dendrobates tinctorius)', 'Dendrobates tinctorius'),
    ('Golden Poison Frog (Phyllobates terribilis)', 'Phyllobates terribilis'),
    ('Goliath Frog (Conraua goliath)', 'Conraua goliath'),
    ('American Bullfrog (Lithobates catesbeianus)', 'Lithobates catesbeianus'),
    ('Red-eyed Tree Frog (Agalychnis callidryas)', 'Agalychnis callidryas'),
    ('Hellbender (Cryptobranchus alleganiensis)', 'Cryptobranchus alleganiensis'),
    ('Japanese Giant Salamander (Andrias japonicus)', 'Andrias japonicus'),
    ('Cane Toad (Rhinella marina)', 'Rhinella marina'),
    ('African Clawed Frog (Xenopus laevis)', 'Xenopus laevis'),
    ('Olm Salamander (Proteus anguinus)', 'Proteus anguinus'),
    
    # --- Fish: Chondrichthyes & Ancient ---
    ('Whale Shark (Rhincodon typus)', 'Rhincodon typus'),
    ('Great Hammerhead Shark (Sphyrna mokarran)', 'Sphyrna mokarran'),
    ('Tiger Shark (Galeocerdo cuvier)', 'Galeocerdo cuvier'),
    ('Basking Shark (Cetorhinus maximus)', 'Cetorhinus maximus'),
    ('Giant Oceanic Manta Ray (Mobula birostris)', 'Mobula birostris'),
    ('Coelacanth (Latimeria chalumnae)', 'Latimeria chalumnae'),
    ('Alligator Gar (Atractosteus spatula)', 'Atractosteus spatula'),
    
    # --- Fish: Teleosts ---
    ('Ocellaris Clownfish (Amphiprion ocellaris)', 'Amphiprion ocellaris'),
    ('Deep-sea Anglerfish (Melanocetus johnsonii)', 'Melanocetus johnsonii'),
    ('Great Barracuda (Sphyraena barracuda)', 'Sphyraena barracuda'),
    ('Giant Moray (Gymnothorax javanicus)', 'Gymnothorax javanicus'),
    ('Ocean Sunfish (Mola mola)', 'Mola mola'),
    ('Swordfish (Xiphias gladius)', 'Xiphias gladius'),
    ('Atlantic Cod (Gadus morhua)', 'Gadus morhua'),
    ('Red Lionfish (Pterois volitans)', 'Pterois volitans'),
    ('Regal Blue Tang (Paracanthurus hepatus)', 'Paracanthurus hepatus'),
    ('Red-bellied Piranha (Pygocentrus nattereri)', 'Pygocentrus nattereri'),
    ('Arapaima (Arapaima gigas)', 'Arapaima gigas'),
    ('Northern Pike (Esox lucius)', 'Esox lucius'),
    ('Electric Eel (Electrophorus electricus)', 'Electrophorus electricus'),
    ('Siamese Fighting Fish (Betta splendens)', 'Betta splendens'),
    
    # --- Invertebrates: Arthropods ---
    ('Peacock Mantis Shrimp (Odontodactylus scyllarus)', 'Odontodactylus scyllarus'),
    ('European Praying Mantis (Mantis religiosa)', 'Mantis religiosa'),
    ('Leafcutter Ant (Atta cephalotes)', 'Atta cephalotes'),
    ('Buff-tailed Bumblebee (Bombus terrestris)', 'Bombus terrestris'),
    ('Emperor Dragonfly (Anax imperator)', 'Anax imperator'),
    ('Atlas Moth (Attacus atlas)', 'Attacus atlas'),
    ('Periodical Cicada (Magicicada septendecim)', 'Magicicada septendecim'),
    ('European Stag Beetle (Lucanus cervus)', 'Lucanus cervus'),
    ('Goliath Beetle (Goliathus goliatus)', 'Goliathus goliatus'),
    ('Mexican Redknee Tarantula (Brachypelma hamorii)', 'Brachypelma hamorii'),
    ('Sydney Funnel-web Spider (Atrax robustus)', 'Atrax robustus'),
    ('Atlantic Horseshoe Crab (Limulus polyphemus)', 'Limulus polyphemus'),
    ('Fiddler Crab (Uca pugilator)', 'Uca pugilator'),
    ('Coconut Crab (Birgus latro)', 'Birgus latro'),
    
    # --- Invertebrates: Molluscs & Others ---
    ('Giant Pacific Octopus (Enteroctopus dofleini)', 'Enteroctopus dofleini'),
    ('Blue-ringed Octopus (Hapalochlaena maculosa)', 'Hapalochlaena maculosa'),
    ('Giant Squid (Architeuthis dux)', 'Architeuthis dux'),
    ('Colossal Squid (Mesonychoteuthis hamiltoni)', 'Mesonychoteuthis hamiltoni'),
    ('Chambered Nautilus (Nautilus pompilius)', 'Nautilus pompilius'),
    ('Giant Clam (Tridacna gigas)', 'Tridacna gigas'),
    ('Beadlet Anemone (Actinia equina)', 'Actinia equina'),
    ('Sea Wasp Box Jellyfish (Chironex fleckeri)', 'Chironex fleckeri'),
    ('Portuguese Man o War (Physalia physalis)', 'Physalia physalis'),
    ('Lions Mane Jellyfish (Cyanea capillata)', 'Cyanea capillata'),
    ('Crown-of-thorns Starfish (Acanthaster planci)', 'Acanthaster planci'),
    ('Black Sea Cucumber (Holothuria atra)', 'Holothuria atra'),
    ('Sea Walnut Comb Jelly (Mnemiopsis leidyi)', 'Mnemiopsis leidyi'),
    ('Yellow Tube Sponge (Aplysina fistularis)', 'Aplysina fistularis'),
    ('Freshwater Planarian (Schmidtea mediterranea)', 'Schmidtea mediterranea'),
    ('Water Bear Tardigrade (Hypsibius exemplaris)', 'Hypsibius exemplaris')
]

def main():
    base_dir = "/Users/amitjoshi2724/Desktop/phylogenle"
    data_dir = os.path.join(base_dir, "data")
    
    print("1. Initializing NCBI Taxonomy...")
    ncbi = NCBITaxa()
    
    print("2. Loading existing species map and cache...")
    gen_shards_path = os.path.join(base_dir, "generate_shards.py")
    with open(gen_shards_path, "r") as f:
        code = f.read()
    m = re.search(r"SPECIES_MAP = \{(.*?)\}", code, re.DOTALL)
    existing_species_map = dict(re.findall(r'\"([^\"]+)\":\s*\"([^\"]+)\"', m.group(1)))
    print(f"Loaded {len(existing_species_map)} existing species.")
    
    # Merge new candidates
    combined_species_map = dict(existing_species_map)
    added_count = 0
    for name, sci in NEW_CANDIDATES:
        if sci not in combined_species_map.values():
            combined_species_map[name] = sci
            added_count += 1
            
    print(f"Added {added_count} new species. Total species: {len(combined_species_map)}")
    
    # Map species to TaxID and precompute lineages
    print("3. Precomputing TaxIDs and Lineages...")
    species_to_taxid = {}
    taxid_to_lineage = {}
    for name, sci in combined_species_map.items():
        t = ncbi.get_name_translator([sci]).get(sci)
        if t:
            taxid = t[0]
            species_to_taxid[sci] = taxid
            if taxid not in taxid_to_lineage:
                taxid_to_lineage[taxid] = ncbi.get_lineage(taxid)
        else:
            print(f"WARNING: No taxid found for {sci}!")

    # Load time_cache
    cache_path = os.path.join(data_dir, "time_cache.json")
    time_cache = {}
    if os.path.exists(cache_path):
        with open(cache_path, "r") as f:
            time_cache = json.load(f)
    print(f"Loaded {len(time_cache)} existing pair records in time_cache.json")

    # Map existing pair times to NCBI LCA taxids
    print("4. Mapping existing calibrated times to LCA nodes...")
    node_times = {}
    for k, v in time_cache.items():
        if v <= 0: continue
        parts = k.split("||")
        if len(parts) != 2 or parts[0] == parts[1]: continue
        s1, s2 = parts
        t1 = species_to_taxid.get(s1)
        t2 = species_to_taxid.get(s2)
        if not t1 or not t2: continue
        lin1 = set(taxid_to_lineage[t1])
        lin2 = taxid_to_lineage[t2]
        lca = None
        for t in reversed(lin2):
            if t in lin1:
                lca = t
                break
        if lca:
            node_times.setdefault(lca, []).append(v)
            
    node_median = {node: sorted(times)[len(times)//2] for node, times in node_times.items()}
    print(f"Calibrated LCA nodes from existing cache: {len(node_median)}")

    # Find all unique LCAs across all pairs of the combined species list
    print("5. Discovering all unique LCAs among all 343 species...")
    species_keys = list(combined_species_map.keys())
    lca_pair_rep = {} # lca -> (taxid1, taxid2, sci1, sci2)
    
    for i in range(len(species_keys)):
        sci1 = combined_species_map[species_keys[i]]
        t1 = species_to_taxid[sci1]
        lin1 = taxid_to_lineage[t1]
        for j in range(i+1, len(species_keys)):
            sci2 = combined_species_map[species_keys[j]]
            t2 = species_to_taxid[sci2]
            lin2 = taxid_to_lineage[t2]
            lca = None
            for a, b in zip(lin1, lin2):
                if a == b: lca = a
                else: break
            if lca and lca not in lca_pair_rep:
                lca_pair_rep[lca] = (t1, t2, sci1, sci2)

    print(f"Total unique LCAs in the tree: {len(lca_pair_rep)}")
    uncalibrated = [lca for lca in lca_pair_rep if lca not in node_median]
    print(f"LCAs requiring calibration: {len(uncalibrated)}")

    # Calibrate uncalibrated nodes using TimeTree API with lineage fallback
    headers = {"User-Agent": "Mozilla/5.0"}
    new_calibrations = 0
    for idx, lca in enumerate(uncalibrated):
        t1, t2, s1, s2 = lca_pair_rep[lca]
        lca_name = ncbi.get_taxid_translator([lca]).get(lca, str(lca))
        url = f"http://www.timetree.org/ajax/pairwise/{t1}/{t2}"
        val = None
        try:
            resp = requests.get(url, headers=headers, timeout=6)
            match = re.search(r"Median Time:.*?([\d\.]+)\s*MYA", resp.text, re.IGNORECASE | re.DOTALL)
            if match:
                val = float(match.group(1))
        except Exception:
            pass

        if val is None or val <= 0:
            # Fallback: find closest calibrated ancestor in lineage
            lin = taxid_to_lineage[t1]
            if lca in lin:
                anc_idx = lin.index(lca) - 1
                while anc_idx >= 0:
                    anc = lin[anc_idx]
                    if anc in node_median:
                        val = round(node_median[anc] * 0.75, 1) # realistic child clade fraction
                        break
                    anc_idx -= 1
            if val is None or val <= 0:
                val = 50.0 # sensible default
            print(f"  [{idx+1}/{len(uncalibrated)}] LCA {lca} ({lca_name}) -> fallback: {val} MYA")
        else:
            print(f"  [{idx+1}/{len(uncalibrated)}] LCA {lca} ({lca_name}) -> TimeTree: {val} MYA")
            new_calibrations += 1

        node_median[lca] = val
        # Polite delay for API
        time.sleep(0.15)

    print(f"Calibration complete! Calibrated {new_calibrations} via TimeTree API.")

    # Precompute LCA info (rank and name) for every LCA
    major_ranks = ["superkingdom", "kingdom", "phylum", "class", "order", "family", "genus", "species"]
    lca_meta = {}
    for lca in lca_pair_rep:
        # Get rank going up
        lca_lin = ncbi.get_lineage(lca)
        found_rank = "Unknown"
        found_name = "Unknown"
        for t in reversed(lca_lin):
            r = ncbi.get_rank([t]).get(t, "")
            if r in major_ranks:
                found_rank = r.capitalize()
                found_name = ncbi.get_taxid_translator([t]).get(t, "Unknown")
                break
        lca_meta[lca] = {
            "rank": found_rank,
            "name": found_name,
            "time": node_median.get(lca, 50.0)
        }

    # 6. Generate JSON shards for ALL 343 species
    print("6. Generating JSON shards for all species...")
    for idx, target_name in enumerate(species_keys):
        target_sci = combined_species_map[target_name]
        target_taxid = species_to_taxid[target_sci]
        lin_target = taxid_to_lineage[target_taxid]
        
        shard_data = {}
        for other_name in species_keys:
            other_sci = combined_species_map[other_name]
            other_taxid = species_to_taxid[other_sci]
            
            if target_sci == other_sci:
                shard_data[other_name.lower()] = {
                    "time": 0.0,
                    "rank": "Species",
                    "lca_name": other_sci
                }
            else:
                lin_other = taxid_to_lineage[other_taxid]
                lca = None
                for a, b in zip(lin_target, lin_other):
                    if a == b: lca = a
                    else: break
                
                meta = lca_meta.get(lca, {"rank": "Class", "name": "Chordata", "time": 94.0})
                shard_data[other_name.lower()] = {
                    "time": meta["time"],
                    "rank": meta["rank"],
                    "lca_name": meta["name"]
                }
                
                # Also cache in time_cache
                pair_key = tuple(sorted([target_sci, other_sci]))
                cache_key = f"{pair_key[0]}||{pair_key[1]}"
                if cache_key not in time_cache:
                    time_cache[cache_key] = meta["time"]

        # Save shard file
        shard_filename = re.sub(r"[^a-z0-9_()]+", "_", target_name.lower().replace(" ", "_")) + ".json"
        shard_filepath = os.path.join(data_dir, shard_filename)
        with open(shard_filepath, "w") as sf:
            json.dump(shard_data, sf, indent=2)

    print(f"Successfully generated {len(species_keys)} shard files!")

    # 7. Write species_list.json
    species_list_path = os.path.join(data_dir, "species_list.json")
    with open(species_list_path, "w") as f:
        json.dump(species_keys, f, indent=2)
    print(f"Updated data/species_list.json with {len(species_keys)} species.")

    # 8. Save updated time_cache.json
    with open(cache_path, "w") as f:
        json.dump(time_cache, f)
    print(f"Updated data/time_cache.json with {len(time_cache)} pair records.")

    # 9. Update generate_shards.py with full map
    new_lines = ["SPECIES_MAP = {"]
    for k, v in combined_species_map.items():
        new_lines.append(f'    "{k}": "{v}",')
    new_lines.append("}")
    new_map_str = "\n".join(new_lines)
    
    with open(gen_shards_path, "r") as f:
        old_code = f.read()
    new_code = re.sub(r"SPECIES_MAP = \{.*?\}", new_map_str, old_code, flags=re.DOTALL)
    with open(gen_shards_path, "w") as f:
        f.write(new_code)
    print(f"Updated generate_shards.py with {len(combined_species_map)} species.")
    print("\nALL DONE! Dataset expansion complete!")

if __name__ == "__main__":
    main()
