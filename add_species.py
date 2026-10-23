#!/usr/bin/env python3
"""
Phylogenle - Single Species Ingestion CLI Tool
Adds a single new animal species into Phylogenle's dataset across:
1. data/phylogeny_tree.json (Lineage path & calibrated internal nodes)
2. data/species_list.json (Autocomplete list)
3. data/species_taxonomy_catalog.json (Metadata)
4. species_catalog.md (Markdown catalog)

Usage:
    python3 add_species.py "Common Name" "Scientific Name"
    python3 add_species.py "Common Name (Scientific Name)"
    python3 add_species.py   # (Interactive prompt mode)
"""

import sys
import os
import re
import json
from ete3 import NCBITaxa

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TREE_PATH = os.path.join(BASE_DIR, "data", "phylogeny_tree.json")
SPECIES_LIST_PATH = os.path.join(BASE_DIR, "data", "species_list.json")
CATALOG_JSON_PATH = os.path.join(BASE_DIR, "data", "species_taxonomy_catalog.json")
CATALOG_MD_PATH = os.path.join(BASE_DIR, "species_catalog.md")

MAJOR_RANKS = {"superkingdom", "kingdom", "phylum", "class", "order", "family", "genus", "species"}

def get_clade(lineage, ncbi):
    lineage_set = set(lineage)
    if 40674 in lineage_set:
        return "Mammals"
    if 8782 in lineage_set:
        return "Birds"
    if 8292 in lineage_set:
        return "Amphibians"
    if 7898 in lineage_set or 7777 in lineage_set:
        return "Fishes"
    # Sauropsids (Reptiles)
    if 8457 in lineage_set and 8782 not in lineage_set:
        return "Reptiles"
    # Check orders under Sauropsida
    reptile_orders = {8570, 8493, 8459, 8504} # Squamata, Crocodylia, Testudines, Rhynchocephalia
    if any(o in lineage_set for o in reptile_orders):
        return "Reptiles"
    # Other vertebrates (lungfish, coelacanth, cyclostomes)
    if 7742 in lineage_set:
        return "Fishes"
    return "Invertebrates"

def get_order_name(lineage, ncbi):
    for t in reversed(lineage):
        rank = ncbi.get_rank([t]).get(t, "")
        if rank == "order":
            return ncbi.get_taxid_translator([t]).get(t, "Other")
    return "Other"

def parse_input():
    if len(sys.argv) == 3:
        common = sys.argv[1].strip()
        scientific = sys.argv[2].strip()
    elif len(sys.argv) == 2:
        arg = sys.argv[1].strip()
        match = re.match(r"^(.*?)\s*\((.*?)\)$", arg)
        if match:
            common = match.group(1).strip()
            scientific = match.group(2).strip()
        else:
            print(f"Error: Unable to parse combined string '{arg}'. Expected format: 'Common Name (Scientific Name)'")
            sys.exit(1)
    else:
        print("=== 🧬 Phylogenle Single Species Ingestion ===")
        common = input("Enter English Common Name (e.g. Snow Leopard): ").strip()
        scientific = input("Enter Scientific Name (e.g. Panthera uncia): ").strip()
        if not common or not scientific:
            print("Error: Both common and scientific names are required.")
            sys.exit(1)

    # Clean capitalization
    common = " ".join([w.capitalize() if not w.startswith("(") else w for w in common.split(" ")])
    sci_parts = scientific.split()
    if len(sci_parts) >= 2:
        scientific = sci_parts[0].capitalize() + " " + " ".join([p.lower() for p in sci_parts[1:]])
    else:
        scientific = scientific.capitalize()

    return common, scientific

def save_tree_formatted(tree_path, tree):
    with open(tree_path, "w") as f:
        f.write('{\n  "species": {\n')
        species_items = list(tree["species"].items())
        for i, (k, v) in enumerate(species_items):
            comma = "," if i < len(species_items) - 1 else ""
            f.write(f'    {json.dumps(k)}: {json.dumps(v)}{comma}\n')
        f.write('  },\n  "nodes": {\n')
        node_items = list(tree["nodes"].items())
        for i, (k, v) in enumerate(node_items):
            comma = "," if i < len(node_items) - 1 else ""
            f.write(f'    {json.dumps(k)}: {json.dumps(v)}{comma}\n')
        f.write('  }\n}\n')

def add_species(common, scientific):
    display_name = f"{common} ({scientific})"
    species_key = display_name.lower()

    print(f"\n🔍 Processing candidate: {display_name}")

    # Check for duplicate
    with open(SPECIES_LIST_PATH) as f:
        species_list = json.load(f)

    if display_name in species_list or any(s.lower() == species_key for s in species_list):
        print(f"⚠️  Species '{display_name}' is ALREADY present in Phylogenle!")
        return False

    ncbi = NCBITaxa()

    # Resolve TaxID
    name_translator = ncbi.get_name_translator([scientific])
    if not name_translator or scientific not in name_translator:
        print(f"❌ Error: Scientific name '{scientific}' was not found in NCBI Taxonomy.")
        # Check if genus exists
        genus = scientific.split()[0]
        g_trans = ncbi.get_name_translator([genus])
        if g_trans:
            print(f"💡 Genus '{genus}' was found in NCBI. Please check the species epithet spelling.")
        return False

    taxid = name_translator[scientific][0]
    lineage = ncbi.get_lineage(taxid)

    # Animalia validation
    if 33208 not in lineage:
        print(f"❌ Error: Taxon '{scientific}' (TaxID {taxid}) is NOT in Kingdom Animalia (Metazoa)!")
        return False

    clade = get_clade(lineage, ncbi)
    order_name = get_order_name(lineage, ncbi)

    print(f"✅ Verified via NCBI Taxonomy:")
    print(f"   - TaxID: {taxid}")
    print(f"   - Clade: {clade}")
    print(f"   - Order: {order_name}")
    print(f"   - Ancestral lineage depth: {len(lineage)} nodes")

    # Load and update phylogeny_tree.json
    with open(TREE_PATH) as f:
        tree = json.load(f)

    new_nodes_calibrated = 0
    # Ensure all nodes in lineage exist in tree['nodes']
    for idx, nid in enumerate(lineage):
        nid_str = str(nid)
        if nid_str not in tree["nodes"]:
            # Interpolate divergence time from parent node
            parent_time = None
            for p_idx in range(idx - 1, -1, -1):
                p_nid_str = str(lineage[p_idx])
                if p_nid_str in tree["nodes"]:
                    parent_time = tree["nodes"][p_nid_str].get("time")
                    break
            
            node_time = round(parent_time * 0.72, 1) if (parent_time and parent_time > 0) else 25.0
            
            # Rank and Name
            found_rank = "Unknown"
            actual_name = ncbi.get_taxid_translator([nid]).get(nid, "Unknown")
            found_name = actual_name
            major_name = actual_name
            lin_nid = ncbi.get_lineage(nid)
            for t in reversed(lin_nid):
                r = ncbi.get_rank([t]).get(t, "")
                if r in MAJOR_RANKS:
                    found_rank = r.capitalize()
                    major_name = ncbi.get_taxid_translator([t]).get(t, major_name)
                    if found_name == "Unknown":
                        found_name = major_name
                    break
            if major_name == "Metazoa":
                major_name = "Animalia"

            tree["nodes"][nid_str] = {
                "rank": found_rank,
                "name": found_name,
                "major_name": major_name,
                "time": node_time
            }
            new_nodes_calibrated += 1

    # Add species lineage
    tree["species"][species_key] = lineage
    save_tree_formatted(TREE_PATH, tree)
    print(f"💾 Updated phylogeny_tree.json (added species path + {new_nodes_calibrated} new calibrated nodes)")

    # Update species_list.json
    species_list.append(display_name)
    species_list.sort(key=lambda s: s.lower())
    with open(SPECIES_LIST_PATH, "w") as f:
        json.dump(species_list, f, indent=2)
    print(f"💾 Updated species_list.json (total active: {len(species_list)})")

    # Update species_taxonomy_catalog.json
    with open(CATALOG_JSON_PATH) as f:
        cat_json = json.load(f)
    
    cat_json.append({
        "display": display_name,
        "common": common,
        "scientific": scientific,
        "clade": clade,
        "subclade": order_name
    })
    cat_json.sort(key=lambda x: x["display"].lower())
    with open(CATALOG_JSON_PATH, "w") as f:
        json.dump(cat_json, f, indent=2)
    print(f"💾 Updated species_taxonomy_catalog.json")

    # Update species_catalog.md
    if os.path.exists(CATALOG_MD_PATH):
        with open(CATALOG_MD_PATH, "r") as f:
            md_content = f.read()

        table_row = f"| {common} | *{scientific}* |\n"
        # Find order heading in markdown (e.g. "### Carnivora")
        order_heading = f"### {order_name}\n"
        if order_heading in md_content:
            # Insert into order table
            head_idx = md_content.find(order_heading)
            table_start = md_content.find("| :--- | :--- |\n", head_idx)
            if table_start != -1:
                insert_pos = table_start + len("| :--- | :--- |\n")
                md_content = md_content[:insert_pos] + table_row + md_content[insert_pos:]
                with open(CATALOG_MD_PATH, "w") as f:
                    f.write(md_content)
                print(f"💾 Updated species_catalog.md under '### {order_name}'")
        else:
            # Fallback append to file
            with open(CATALOG_MD_PATH, "a") as f:
                f.write(f"\n| {common} | *{scientific}* |\n")
            print(f"💾 Appended entry to species_catalog.md")

    print(f"\n🎉 Successfully added '{display_name}' to Phylogenle!")
    print(f"   Now playable in both Daily and Unlimited modes!")
    return True

if __name__ == "__main__":
    common, scientific = parse_input()
    add_species(common, scientific)
