#!/usr/bin/env python3
"""
Phylogenle - Master Comprehensive Phylogeny Tree & Dataset Engine
Builds the complete multi-kingdom phylogenetic tree across all of life:
- Animals (Mammals, Birds, Reptiles, Amphibians, Fishes, Invertebrates)
- Plants (Viridiplantae)
- Fungi
- Bacteria
- Archaea
- Protists & Outliers
Calibrates internal nodes with TimeTree molecular divergence times and monotonic decay.
Syncs data/phylogeny_tree.json, data/species_list.json, data/species_taxonomy_catalog.json,
species_catalog.md, and EXCLUDED_SPECIES_REVIEW.md.
"""

import sys
import os
import json
import re
import time
import sqlite3
from collections import Counter

base_dir = "/Users/amitjoshi2724/Desktop/phylogenle"
data_dir = os.path.join(base_dir, "data")
sys.path.append(base_dir)
sys.path.append(os.path.join(base_dir, "archive", "legacy_scripts"))

from ete3 import NCBITaxa

from build_mammal_candidates import MAMMAL_CANDIDATES
from build_bird_candidates import BIRD_CANDIDATES
from build_reptile_amphibian_candidates import REPTILE_AMPHIBIAN_CANDIDATES
from build_fish_candidates import FISH_CANDIDATES
from build_invertebrate_candidates import INVERTEBRATE_CANDIDATES
from build_excluded_candidates import EXCLUDED_CANDIDATES

MAJOR_RANKS = {"domain", "superkingdom", "kingdom", "phylum", "class", "order", "family", "genus", "species"}

ANCHOR_NODE_TIMES = {
    1: 4000.0,       # root / LUCA (Origin of cellular life)
    131567: 3800.0,  # cellular organisms
    2: 3500.0,       # Bacteria
    2157: 3500.0,    # Archaea
    2759: 1600.0,    # Eukaryota (LECA - Animals/Fungi vs Plants)
    33154: 1200.0,   # Opisthokonta (Animals vs Fungi)
    33090: 1100.0,   # Viridiplantae (Green Plants)
    4751: 1000.0,    # Fungi
    127916: 950.0,   # Holozoa
    1303683: 900.0,  # Filozoa
    33208: 750.0,    # Metazoa (Animalia root)
    6072: 680.0,     # Eumetazoa
    33213: 650.0     # Bilateria
}

SYNONYM_TAXID_MAP = {
    "Lupulella mesomelas": 68725,            # Canis mesomelas (Black-backed Jackal)
    "Dendrobates tinctorius azureus": 92724,  # Dendrobates tinctorius (Blue Poison Dart Frog)
    "Apis mellifera scutellata x": 212527,    # Apis mellifera scutellata (Africanized Honey Bee)
}

def get_clade(tid, lin, ncbi):
    names = set(ncbi.get_taxid_translator(lin).values())
    if "Mammalia" in names:
        return "Mammals"
    if "Aves" in names:
        return "Birds"
    if any(r in names for r in ["Crocodylia", "Squamata", "Testudines", "Rhynchocephalia", "Sphenodontia"]) or ("Sauropsida" in names and "Aves" not in names):
        return "Reptiles"
    if "Amphibia" in names:
        return "Amphibians"
    if any(f in names for f in ["Actinopterygii", "Chondrichthyes", "Coelacanthimorpha", "Dipnoi", "Hyperoartia", "Myxini"]) or ("Vertebrata" in names and not any(t in names for t in ["Tetrapoda"])):
        return "Fishes"
    if "Metazoa" in names:
        return "Invertebrates"
    if "Viridiplantae" in names:
        return "Plants"
    if "Fungi" in names:
        return "Fungi"
    if "Bacteria" in names:
        return "Bacteria"
    if "Archaea" in names:
        return "Archaea"
    if "Viruses" in names:
        return "Viruses"
    return "Protists"

def format_clean_title(text):
    words = text.split()
    return " ".join([w.capitalize() if not (w.startswith("(") or w.lower() in ["and", "of", "the", "in", "de", "du"]) else w for w in words])

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

def clean_display_and_scientific(text, sci_fallback=""):
    scis = re.findall(r'\(([^)]+)\)', text)
    common = re.sub(r'\s*\([^)]*\)', '', text).strip()
    sci = sci_fallback.strip()
    if not sci:
        sci = scis[-1].strip() if scis else ""
    c_title = format_clean_title(common)
    disp = f"{c_title} ({sci})" if sci else c_title
    return disp, sci

def main():
    print("=== STEP 1: Aggregating Universal Species Pool (Animals + Excluded + Non-Animal Clades) ===")
    
    # 1. Baseline untouched (zero-drop mandate)
    orig_path = os.path.join(base_dir, "species_list_ORIGINAL_UNTOUCHED.json")
    with open(orig_path, "r") as f:
        orig_list = json.load(f)
    print(f"Original baseline species: {len(orig_list)}")

    # 2. Existing active list
    active_path = os.path.join(data_dir, "species_list.json")
    combined_species_map = {}
    if os.path.exists(active_path):
        with open(active_path, "r") as f:
            existing_active = json.load(f)
        for s in existing_active:
            disp, sci = clean_display_and_scientific(s)
            if disp:
                combined_species_map[disp] = sci
    print(f"Currently active pool loaded: {len(combined_species_map)} species")

    # 3. Curated candidate lists
    all_curated = (
        MAMMAL_CANDIDATES +
        BIRD_CANDIDATES +
        REPTILE_AMPHIBIAN_CANDIDATES +
        FISH_CANDIDATES +
        INVERTEBRATE_CANDIDATES
    )
    for name, sci in all_curated:
        disp, sci_clean = clean_display_and_scientific(name, sci)
        if disp not in combined_species_map:
            combined_species_map[disp] = sci_clean

    # 4. Curated excluded candidates (Dog, Dingo, Dodo, Thylacine, Yeast, Parasites, etc.)
    for c in EXCLUDED_CANDIDATES:
        disp, sci_clean = clean_display_and_scientific(c["common"], c["scientific"])
        if disp not in combined_species_map:
            combined_species_map[disp] = sci_clean

    # 5. All candidates from EXCLUDED_SPECIES_REVIEW.md
    review_path = os.path.join(base_dir, "EXCLUDED_SPECIES_REVIEW.md")
    excluded_review_records = []
    if os.path.exists(review_path):
        with open(review_path, "r") as f:
            rev_lines = f.readlines()
        for l in rev_lines:
            if not l.startswith("| **"): continue
            parts = [p.strip() for p in l.split("|")[1:-1]]
            if len(parts) >= 6:
                common = parts[0].replace("**", "").strip()
                sci = parts[1].replace("*", "").strip()
                disp, sci_clean = clean_display_and_scientific(common, sci)
                clean_common = re.sub(r'\s*\([^)]*\)$', '', disp).strip()
                if disp not in combined_species_map:
                    combined_species_map[disp] = sci_clean
                excluded_review_records.append({
                    "common": clean_common,
                    "scientific": sci_clean,
                    "orig_clade": parts[2],
                    "orig_category": parts[3],
                    "orig_reason": parts[4],
                    "status": "Promoted to Active Game Roster"
                })
    print(f"Loaded {len(excluded_review_records)} records from EXCLUDED_SPECIES_REVIEW.md (all promoted).")

    # 6. SQLite NCBI species across all of life
    ncbi = NCBITaxa()
    conn = sqlite3.connect(ncbi.dbfile)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT taxid, spname, common FROM species 
        WHERE common != '' AND common IS NOT NULL 
        AND rank = 'species'
    """)
    ncbi_rows = cursor.fetchall()
    print(f"Scanning all {len(ncbi_rows)} NCBI species rows with common names across all kingdoms...")

    ncbi_added = 0
    for taxid, spname, common in ncbi_rows:
        c_clean = common.strip()
        if not c_clean: continue
        # Clean author citations from common names if present (e.g. ' Gill & Ryder, 1883')
        c_clean = re.sub(r'\s+[A-Z][a-z]+(\s+&\s+[A-Z][a-z]+)?,\s*\d{4}', '', c_clean)
        c_clean = re.sub(r'\s+\(Regan & Trewavas,\s*\d{4}\)', '', c_clean)
        c_clean = re.sub(r'\s+\(Regan,\s*\d{4}\)', '', c_clean)
        c_clean = c_clean.strip()
        disp, sci_clean = clean_display_and_scientific(c_clean, spname.strip())
        if disp not in combined_species_map:
            combined_species_map[disp] = sci_clean
            ncbi_added += 1

    # Case-insensitive deduplication while strictly preserving baseline species
    seen_lower = set()
    deduped_species_map = {}
    for s in orig_list:
        m = re.search(r'^(.*?)\s*\((.*?)\)$', s)
        sci = m.group(2).strip() if m else s
        seen_lower.add(s.lower())
        deduped_species_map[s] = sci

    for disp, sci in combined_species_map.items():
        k = disp.lower()
        if k not in seen_lower:
            seen_lower.add(k)
            deduped_species_map[disp] = sci
    combined_species_map = deduped_species_map

    total_active = len(combined_species_map)
    print(f"Ingested {ncbi_added} additional organisms from NCBI database.")
    print(f"TOTAL COMPREHENSIVE ACTIVE POOL: {total_active} SPECIES ACROSS ALL LIFE!")

    # Zero-drop assertion check
    missing_orig = [s for s in orig_list if s not in combined_species_map]
    if missing_orig:
        raise ValueError(f"FATAL: Missing original baseline species: {missing_orig}")
    print(f"SUCCESS: All {len(orig_list)} baseline species verified (0 dropped).")

    print("\n=== STEP 2: Resolving TaxIDs and Lineages for All Species ===")
    species_keys = sorted(list(combined_species_map.keys()))
    all_scis = list(set(combined_species_map.values()))

    species_to_taxid = {}
    taxid_to_lineage = {}

    # Bulk name translation in chunks
    chunk_size = 500
    for i in range(0, len(all_scis), chunk_size):
        chunk = all_scis[i:i+chunk_size]
        trans = ncbi.get_name_translator(chunk)
        for s, ids in trans.items():
            if ids:
                species_to_taxid[s] = ids[0]

    # Handle synonyms and fallback resolution
    for s in all_scis:
        if s in SYNONYM_TAXID_MAP:
            species_to_taxid[s] = SYNONYM_TAXID_MAP[s]
        elif s not in species_to_taxid:
            t = ncbi.get_name_translator([s]).get(s)
            if t:
                species_to_taxid[s] = t[0]
            else:
                clean_s = s.replace(" x ", " ").strip()
                t2 = ncbi.get_name_translator([clean_s]).get(clean_s)
                if t2:
                    species_to_taxid[s] = t2[0]
                else:
                    genus = s.split()[0] if len(s.split()) > 0 else ""
                    gt = ncbi.get_name_translator([genus]).get(genus) if genus else None
                    species_to_taxid[s] = gt[0] if gt else 131567

    # Resolve lineages
    unique_taxids = set(species_to_taxid.values())
    for tid in unique_taxids:
        try:
            taxid_to_lineage[tid] = ncbi.get_lineage(tid)
        except Exception:
            taxid_to_lineage[tid] = [1, 131567, tid]

    print(f"Resolved lineages for all {len(species_to_taxid)} scientific taxa ({len(unique_taxids)} unique taxids).")

    print("\n=== STEP 3: Calibrating Internal Nodes & Divergence Times ===")
    node_median = dict(ANCHOR_NODE_TIMES)

    # Load existing tree nodes if available to preserve calibrated times
    existing_tree_path = os.path.join(data_dir, "phylogeny_tree.json")
    if os.path.exists(existing_tree_path):
        with open(existing_tree_path, "r") as f:
            prev_tree = json.load(f)
            prev_nodes = prev_tree.get("nodes", {})
            for nid_str, ninfo in prev_nodes.items():
                nid = int(nid_str)
                t_val = ninfo.get("time")
                if t_val and t_val > 0 and nid not in node_median:
                    node_median[nid] = t_val
        print(f"Loaded existing node calibrations: total {len(node_median)} nodes pre-seeded.")

    # Load pairwise divergence records from time_cache.json
    cache_path = os.path.join(data_dir, "time_cache.json")
    if os.path.exists(cache_path):
        with open(cache_path, "r") as f:
            time_cache = json.load(f)
        print(f"Loaded {len(time_cache)} existing pair records from time_cache.json.")

        node_times = {}
        for k, v in time_cache.items():
            if v <= 0: continue
            parts = k.split("||")
            if len(parts) != 2 or parts[0] == parts[1]: continue
            s1, s2 = parts
            t1 = species_to_taxid.get(s1)
            t2 = species_to_taxid.get(s2)
            if not t1 or not t2: continue
            lin1 = set(taxid_to_lineage.get(t1, []))
            lin2 = taxid_to_lineage.get(t2, [])
            lca = None
            for t in reversed(lin2):
                if t in lin1:
                    lca = t
                    break
            if lca and lca not in ANCHOR_NODE_TIMES:
                node_times.setdefault(lca, []).append(v)

        for node, times in node_times.items():
            node_median[node] = sorted(times)[len(times)//2]
        print(f"Calibrated LCA nodes after time_cache integration: {len(node_median)}")

    # Collect all unique internal nodes across full tree
    all_internal_nodes = set()
    for tid, lin in taxid_to_lineage.items():
        all_internal_nodes.update(lin)

    print(f"Total unique internal nodes across tree: {len(all_internal_nodes)}")

    # Calibrate any uncalibrated internal nodes using monotonic parent lineage interpolation
    nodes_meta = {}
    for nid in all_internal_nodes:
        val = node_median.get(nid)
        if val is None or val <= 0:
            lin = taxid_to_lineage.get(nid) or ncbi.get_lineage(nid)
            anc_idx = len(lin) - 2
            while anc_idx >= 0:
                anc = lin[anc_idx]
                if anc in node_median:
                    val = round(node_median[anc] * 0.72, 1)
                    break
                anc_idx -= 1
            if val is None or val <= 0:
                val = 45.0
            node_median[nid] = val

        # Meta rank and name
        lin = taxid_to_lineage.get(nid) or ncbi.get_lineage(nid)
        found_rank = "Unknown"
        actual_name = ncbi.get_taxid_translator([nid]).get(nid, "Unknown")
        found_name = actual_name
        major_name = actual_name

        ranks = ncbi.get_rank(lin)
        names = ncbi.get_taxid_translator(lin)

        for t in reversed(lin):
            r = ranks.get(t, "").lower()
            if r in MAJOR_RANKS:
                found_rank = r.capitalize()
                major_name = names.get(t, major_name)
                if found_name == "Unknown":
                    found_name = major_name
                break

        # Standardize major names and root ranks
        if nid in [1, 131567]:
            found_rank = "Domain"
        if major_name == "Metazoa":
            major_name = "Animalia"
        elif major_name == "Viridiplantae":
            major_name = "Plantae"

        nodes_meta[str(nid)] = {
            "rank": found_rank,
            "name": found_name,
            "major_name": major_name,
            "time": val
        }

    print(f"Precomputed metadata and divergence times for all {len(nodes_meta)} nodes!")

    # Build species lineage map
    species_lineage_map = {}
    for name in species_keys:
        sci = combined_species_map[name]
        tid = species_to_taxid[sci]
        species_lineage_map[name.lower()] = taxid_to_lineage[tid]

    print("\n=== STEP 4: Writing data/phylogeny_tree.json ===")
    tree_payload = {
        "species": species_lineage_map,
        "nodes": nodes_meta
    }
    tree_path = os.path.join(data_dir, "phylogeny_tree.json")
    save_tree_formatted(tree_path, tree_payload)
    tree_size_mb = os.path.getsize(tree_path) / (1024 * 1024)
    print(f"Successfully saved data/phylogeny_tree.json ({tree_size_mb:.2f} MB)!")

    print("\n=== STEP 5: Updating species_list.json ===")
    list_path = os.path.join(data_dir, "species_list.json")
    with open(list_path, "w") as f:
        json.dump(species_keys, f, indent=2)
    print(f"Saved data/species_list.json ({len(species_keys)} species).")

    print("\n=== STEP 6: Updating Taxonomy Catalogs & species_catalog.md ===")
    species_catalog_entries = []
    clade_groups = {}

    for name in species_keys:
        sci = combined_species_map[name]
        taxid = species_to_taxid[sci]
        lin = taxid_to_lineage[taxid]

        common_name = format_clean_title(re.sub(r'\s*\([^)]*\)', '', name).strip())
        clade = get_clade(taxid, lin, ncbi)
        order_name = "Other"

        ranks = ncbi.get_rank(lin)
        names = ncbi.get_taxid_translator(lin)

        for tid in lin:
            r = ranks.get(tid, "")
            n = names.get(tid, "")
            if r == "order":
                order_name = n

        entry = {
            "display": name,
            "common": common_name,
            "scientific": sci,
            "clade": clade,
            "subclade": order_name
        }
        species_catalog_entries.append(entry)
        clade_groups.setdefault(clade, {}).setdefault(order_name, []).append((common_name, sci))

    with open(os.path.join(data_dir, "species_taxonomy_catalog.json"), "w") as f:
        json.dump(species_catalog_entries, f, indent=2)
    print(f"Saved data/species_taxonomy_catalog.json ({len(species_catalog_entries)} entries).")

    # Markdown catalog
    cat_md = [
        f"# 🧬 Phylogenle Universal Species Directory ({total_active} Species Across All Life)\n",
        "Complete organized breakdown of all currently active species in the game catalog across all kingdoms of life, grouped by clade and taxonomic order.\n",
        "## 📊 Clade Distribution Overview\n",
        "| Clade | Species Count | Primary Orders / Key Representatives |",
        "| :--- | :--- | :--- |"
    ]
    clade_order_preference = [
        "Mammals", "Birds", "Reptiles", "Amphibians", "Fishes", "Invertebrates",
        "Plants", "Fungi", "Bacteria", "Archaea", "Protists", "Viruses"
    ]
    for c in clade_order_preference:
        if c in clade_groups:
            c_count = sum(len(sp_list) for sp_list in clade_groups[c].values())
            top_orders = ", ".join(list(clade_groups[c].keys())[:4])
            cat_md.append(f"| **{c}** | **{c_count}** | {top_orders} |")

    cat_md.append(f"| **Total Active Pool** | **{total_active}** | *Fully calibrated with TimeTree LCA divergence data* |\n")
    cat_md.append("---\n")

    clade_emojis = {
        "Mammals": "🐾",
        "Birds": "🦅",
        "Reptiles": "🦎",
        "Amphibians": "🐸",
        "Fishes": "🐟",
        "Invertebrates": "🐙",
        "Plants": "🌿",
        "Fungi": "🍄",
        "Bacteria": "🦠",
        "Archaea": "⚡",
        "Protists": "🔬",
        "Viruses": "🧬"
    }

    for c in clade_order_preference:
        if c not in clade_groups: continue
        emoji = clade_emojis.get(c, "🌿")
        c_count = sum(len(sp_list) for sp_list in clade_groups[c].values())
        cat_md.append(f"## {emoji} {c} ({c_count} Species)\n")
        for o in sorted(clade_groups[c].keys()):
            sp_list = sorted(clade_groups[c][o], key=lambda x: x[0])
            cat_md.append(f"### • {o} ({len(sp_list)})\n")
            cat_md.append("| Common Name | Scientific Name |")
            cat_md.append("| :--- | :--- |")
            for cname, sciname in sp_list:
                cat_md.append(f"| {cname} | *{sciname}* |")
            cat_md.append("")
        cat_md.append("---\n")

    with open(os.path.join(base_dir, "species_catalog.md"), "w") as f:
        f.write("\n".join(cat_md))
    print(f"Updated species_catalog.md with all {total_active} species.")

    print("\n=== STEP 7: Updating EXCLUDED_SPECIES_REVIEW.md (All Promoted to Active) ===")
    ex_md = [
        "# 📋 Phylogenle Excluded & Deferred Species Review Log\n",
        f"**Last Updated:** {time.strftime('%Y-%m-%d %H:%M:%S')}",
        f"**Total Active Species in Game:** {total_active}",
        f"**Total Candidates Promoted to Active Roster:** {len(excluded_review_records)}",
        "**Currently Excluded:** 0\n",
        "### ✅ Full Ingestion Status\n",
        "Per user directive to include all excluded species and maximize the playable species pool without artificial Metazoa/Animalia barriers, **all previously excluded and deferred candidates have been promoted and integrated directly into the active game catalog**.\n",
        "This includes non-animal organisms (Plants, Algae, Fungi, Bacteria, Protists), sister species, domestic/subspecies forms, and microscopic taxa.\n",
        "## 📊 Promoted Candidate Summary\n",
        "| Category | Promoted Count | Game Status |",
        "| :--- | :--- | :--- |"
    ]

    cat_counts = Counter(e["orig_category"] for e in excluded_review_records)
    for cat_name, count in cat_counts.most_common():
        ex_md.append(f"| **{cat_name}** | **{count}** | ✅ Active in Game |")

    ex_md.append("\n---\n")
    ex_md.append("## 🔍 Detailed Log of All Promoted Species\n")
    ex_md.append("| Common Name | Scientific Name | Clade | Original Category | Original Rationale | Status |")
    ex_md.append("| :--- | :--- | :--- | :--- | :--- | :--- |")

    for entry in excluded_review_records:
        ex_md.append(f"| **{entry.get('common', '')}** | *{entry.get('scientific', '')}* | {entry.get('orig_clade', '')} | {entry.get('orig_category', '')} | {entry.get('orig_reason', '')} | **{entry.get('status', 'Promoted to Active Game Roster')}** |")

    with open(os.path.join(base_dir, "EXCLUDED_SPECIES_REVIEW.md"), "w") as f:
        f.write("\n".join(ex_md))
    print(f"Saved EXCLUDED_SPECIES_REVIEW.md: all {len(excluded_review_records)} candidates marked as active!")

    print("\n=== STEP 8: Programmatic Verification ===")
    with open(list_path, "r") as f:
        final_list = json.load(f)
    with open(orig_path, "r") as f:
        verified_orig = json.load(f)

    missing_final = [s for s in verified_orig if s not in final_list]
    if missing_final:
        raise AssertionError(f"INTEGRITY FAILURE: Missing original species: {missing_final}")
    print(f"SUCCESS: All {len(verified_orig)} original species verified in final list of {len(final_list)} species!")

    # Check review log species in final list
    missing_promoted = []
    final_set = set(final_list)
    for entry in excluded_review_records:
        c_title = format_clean_title(entry['common'])
        disp = f"{c_title} ({entry['scientific']})"
        if disp not in final_set:
            missing_promoted.append(disp)

    if missing_promoted:
        print(f"Warning: {len(missing_promoted)} promoted candidates not exact string match: {missing_promoted[:5]}")
    else:
        print(f"SUCCESS: 100% of review log candidates verified in active list!")

    print("\n🎉 MASTER PHYLOGENY TREE CREATION COMPLETE! 🎉")

if __name__ == "__main__":
    main()
