import html, sys, os, json, re, time, requests

class MockCGI:
    escape = html.escape
sys.modules['cgi'] = MockCGI
from ete3 import NCBITaxa
ncbi = NCBITaxa()

data_dir = '/Users/amitjoshi2724/Desktop/phylogenle/data'
with open(os.path.join(data_dir, 'species_list.json')) as f:
    species_list = json.load(f)

with open(os.path.join(data_dir, 'time_cache.json')) as f:
    time_cache = json.load(f)

NEW_DISPLAY = "Swallowtail Butterfly (Papilio machaon)"
NEW_SCI = "Papilio machaon"

if NEW_DISPLAY in species_list:
    print(f"{NEW_DISPLAY} is already in species_list.json!")
    sys.exit(0)

# 1. Parse all species scientific names
def get_sci(s):
    return s.split('(')[1].split(')')[0].strip() if '(' in s else s.strip()

all_species = species_list + [NEW_DISPLAY]
sci_map = {sp: get_sci(sp) for sp in all_species}

# Resolve taxids
taxids = {}
for sp, sci in sci_map.items():
    t = ncbi.get_name_translator([sci])
    if not t and len(sci.split()) >= 2:
        t = ncbi.get_name_translator([' '.join(sci.split()[:2])])
    if t:
        taxids[sci] = list(t.values())[0][0]
    else:
        raise Exception(f"Cannot resolve taxid for {sci}")

lineages = {sci: ncbi.get_lineage(taxids[sci]) for sci in sci_map.values()}

# Find LCA and metadata for new species with all other species
major_ranks = ["superkingdom", "kingdom", "phylum", "class", "order", "family", "genus", "species"]

def get_lca_info(sci1, sci2):
    if sci1 == sci2:
        return {"rank": "Species", "name": sci1, "time": 0.0}
    
    pair_key = f"{min(sci1, sci2)}||{max(sci1, sci2)}"
    cached_time = time_cache.get(pair_key)
    
    lin1 = lineages[sci1]
    lin2 = lineages[sci2]
    lca = None
    for a, b in zip(lin1, lin2):
        if a == b: lca = a
        else: break
        
    found_rank = "Unknown"
    found_name = "Unknown"
    if lca:
        lca_lin = ncbi.get_lineage(lca)
        for t in reversed(lca_lin):
            r = ncbi.get_rank([t]).get(t, "")
            if r in major_ranks:
                found_rank = r.capitalize()
                found_name = ncbi.get_taxid_translator([t]).get(t, "Unknown")
                break
                
    if cached_time is not None:
        div_time = cached_time
    else:
        # Check TimeTree
        t1, t2 = taxids[sci1], taxids[sci2]
        url = f"http://www.timetree.org/ajax/pairwise/{t1}/{t2}"
        div_time = None
        try:
            r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=5)
            match = re.search(r"Median Time:.*?([\d\.]+)\s*MYA", r.text, re.IGNORECASE | re.DOTALL)
            if match:
                div_time = float(match.group(1))
        except Exception:
            pass
        if div_time is None or div_time <= 0:
            # Fallback based on rank
            rank_defaults = {
                "Species": 0.0,
                "Genus": 5.0,
                "Family": 30.0,
                "Order": 80.0,
                "Class": 160.0,
                "Phylum": 550.0,
                "Kingdom": 650.0
            }
            div_time = rank_defaults.get(found_rank, 100.0)
        time_cache[pair_key] = div_time
        
    return {"rank": found_rank, "name": found_name, "time": div_time}

print(f"Generating shard data for {NEW_DISPLAY} against {len(all_species)} species...")
new_shard_data = {}
for other_sp in all_species:
    other_sci = sci_map[other_sp]
    info = get_lca_info(NEW_SCI, other_sci)
    new_shard_data[other_sp.lower()] = {
        "time": info["time"],
        "rank": info["rank"],
        "lca_name": info["name"]
    }

# Save new shard
new_shard_name = re.sub(r"[^a-z0-9_()]+", "_", NEW_DISPLAY.lower().replace(" ", "_")) + ".json"
with open(os.path.join(data_dir, new_shard_name), 'w') as f:
    json.dump(new_shard_data, f, indent=2)

# Also create hyphen variant if needed
hyphen_variant = "swallowtail-butterfly.json"
with open(os.path.join(data_dir, hyphen_variant), 'w') as f:
    json.dump(new_shard_data, f, indent=2)

print(f"Created shards: {new_shard_name} and {hyphen_variant}")

# Update all existing shards to include the new species
print("Updating all existing shard files with new species...")
for sp in species_list:
    shard_name = re.sub(r"[^a-z0-9_()]+", "_", sp.lower().replace(" ", "_")) + ".json"
    shard_path = os.path.join(data_dir, shard_name)
    if os.path.exists(shard_path):
        with open(shard_path, 'r') as sf:
            sdata = json.load(sf)
        info = get_lca_info(sci_map[sp], NEW_SCI)
        sdata[NEW_DISPLAY.lower()] = {
            "time": info["time"],
            "rank": info["rank"],
            "lca_name": info["name"]
        }
        with open(shard_path, 'w') as sf:
            json.dump(sdata, sf, indent=2)

# Update species_list.json
with open(os.path.join(data_dir, 'species_list.json'), 'w') as f:
    json.dump(all_species, f, indent=2)

# Update time_cache.json
with open(os.path.join(data_dir, 'time_cache.json'), 'w') as f:
    json.dump(time_cache, f)

# Update species_taxonomy_catalog.json
catalog_path = os.path.join(data_dir, 'species_taxonomy_catalog.json')
if os.path.exists(catalog_path):
    with open(catalog_path, 'r') as f:
        catalog = json.load(f)
    catalog.append({
        "display": NEW_DISPLAY,
        "common": "Swallowtail Butterfly",
        "scientific": NEW_SCI,
        "clade": "Invertebrates",
        "subclade": "Arthropoda - Insecta (Lepidoptera)"
    })
    with open(catalog_path, 'w') as f:
        json.dump(catalog, f, indent=2)

print(f"Successfully added {NEW_DISPLAY}! Total species now: {len(all_species)}.")
