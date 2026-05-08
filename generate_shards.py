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
    # Primates
    "Human": "Homo sapiens", "Chimpanzee": "Pan troglodytes", "Gorilla": "Gorilla gorilla", 
    "Orangutan": "Pongo pygmaeus", "Macaque": "Macaca mulatta", "Baboon": "Papio anubis",
    "Lemur": "Lemur catta", "Tarsier": "Carlito syrichta",
    # Felines
    "Lion": "Panthera leo", "Tiger": "Panthera tigris", "Leopard": "Panthera pardus", 
    "Cheetah": "Acinonyx jubatus", "Domestic Cat": "Felis catus", "Cougar": "Puma concolor",
    "Jaguar": "Panthera onca", "Snow Leopard": "Panthera uncia", "Lynx": "Lynx lynx",
    # Canines & Ursids
    "Wolf": "Canis lupus", "Dog": "Canis lupus familiaris", "Fox": "Vulpes vulpes", 
    "Coyote": "Canis latrans", "Bear": "Ursus arctos", "Polar Bear": "Ursus maritimus",
    "Panda": "Ailuropoda melanoleuca", "Raccoon": "Procyon lotor", "Hyena": "Crocuta crocuta",
    # Ungulates
    "Horse": "Equus caballus", "Zebra": "Equus quagga", "Donkey": "Equus asinus",
    "Cow": "Bos taurus", "Pig": "Sus scrofa domesticus", "Sheep": "Ovis aries",
    "Goat": "Capra hircus", "Deer": "Odocoileus virginianus", "Moose": "Alces alces",
    "Camel": "Camelus dromedarius", "Llama": "Lama glama", "Giraffe": "Giraffa camelopardalis",
    "Hippopotamus": "Hippopotamus amphibius", "Rhinoceros": "Diceros bicornis",
    # Other Mammals
    "Elephant": "Loxodonta africana", "Kangaroo": "Macropus rufus", "Koala": "Phascolarctos cinereus",
    "Platypus": "Ornithorhynchus anatinus", "Opossum": "Didelphis virginiana", "Armadillo": "Dasypus novemcinctus",
    "Sloth": "Bradypus tridactylus", "Rabbit": "Oryctolagus cuniculus", "Hare": "Lepus europaeus",
    "Mouse": "Mus musculus", "Rat": "Rattus norvegicus", "Guinea Pig": "Cavia porcellus",
    "Squirrel": "Sciurus carolinensis", "Beaver": "Castor canadensis", "Porcupine": "Erethizon dorsatum",
    "Bat": "Desmodus rotundus", "Hedgehog": "Erinaceus europaeus", "Mole": "Talpa europaea",
    "Walrus": "Odobenus rosmarus", "Seal": "Phoca vitulina",
    # Marine Mammals
    "Dolphin": "Tursiops truncatus", "Orca": "Orcinus orca", "Blue Whale": "Balaenoptera musculus",
    "Humpback Whale": "Megaptera novaeangliae", "Sperm Whale": "Physeter macrocephalus", "Manatee": "Trichechus manatus",
    # Birds
    "Eagle": "Haliaeetus leucocephalus", "Hawk": "Buteo jamaicensis", "Falcon": "Falco peregrinus", 
    "Owl": "Bubo virginianus", "Penguin": "Aptenodytes forsteri", "Ostrich": "Struthio camelus",
    "Emu": "Dromaius novaehollandiae", "Kiwi": "Apteryx mantelli", "Chicken": "Gallus gallus domesticus",
    "Turkey": "Meleagris gallopavo", "Duck": "Anas platyrhynchos", "Goose": "Anser anser",
    "Swan": "Cygnus olor", "Pigeon": "Columba livia", "Crow": "Corvus brachyrhynchos",
    "Raven": "Corvus corax", "Parrot": "Ara macao", "Hummingbird": "Archilochus colubris",
    "Flamingo": "Phoenicopterus roseus", "Peacock": "Pavo cristatus",
    # Reptiles
    "Snake": "Crotalus atrox", "Lizard": "Iguana iguana", "Chameleon": "Chamaeleo chamaeleon",
    "Gecko": "Gekko gecko", "Crocodile": "Crocodylus niloticus", "Alligator": "Alligator mississippiensis",
    "Turtle": "Chrysemys picta", "Tortoise": "Chelonoidis nigra", "Sea Turtle": "Chelonia mydas",
    "Komodo Dragon": "Varanus komodoensis", "Cobra": "Ophiophagus hannah", "Python": "Python bivittatus",
    # Amphibians
    "Frog": "Rana temporaria", "Toad": "Bufo bufo", "Salamander": "Salamandra salamandra", 
    "Newt": "Lissotriton vulgaris", "Axolotl": "Ambystoma mexicanum", "Caecilian": "Gymnopis multiplicata",
    # Fish
    "Shark": "Carcharodon carcharias", "Tuna": "Thunnus thynnus", "Salmon": "Salmo salar",
    "Goldfish": "Carassius auratus", "Carp": "Cyprinus carpio", "Trout": "Oncorhynchus mykiss",
    "Bass": "Micropterus salmoides", "Catfish": "Ictalurus punctatus", "Pufferfish": "Tetraodon nigroviridis",
    "Eel": "Anguilla anguilla", "Stingray": "Dasyatis pastinaca", "Seahorse": "Hippocampus kuda",
    # Invertebrates
    "Octopus": "Octopus vulgaris", "Squid": "Loligo vulgaris", "Cuttlefish": "Sepia officinalis",
    "Snail": "Helix pomatia", "Slug": "Deroceras reticulatum", "Oyster": "Crassostrea gigas",
    "Clam": "Mercenaria mercenaria", "Crab": "Callinectes sapidus", "Lobster": "Homarus americanus",
    "Shrimp": "Penaeus monodon", "Spider": "Latrodectus mactans", "Scorpion": "Pandinus imperator",
    "Centipede": "Scolopendra gigantea", "Millipede": "Archispirostreptus gigas", "Ant": "Solenopsis invicta",
    "Bee": "Apis mellifera", "Wasp": "Vespula vulgaris", "Butterfly": "Danaus plexippus",
    "Moth": "Bombyx mori", "Beetle": "Coccinella septempunctata", "Fly": "Musca domestica",
    "Mosquito": "Anopheles gambiae", "Cockroach": "Periplaneta americana", "Earthworm": "Lumbricus terrestris",
    "Jellyfish": "Aurelia aurita", "Starfish": "Asterias rubens", "Sea Urchin": "Strongylocentrotus purpuratus"
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
