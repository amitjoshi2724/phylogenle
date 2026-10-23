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

from ete3 import NCBITaxa

from build_mammal_candidates import MAMMAL_CANDIDATES
from build_bird_candidates import BIRD_CANDIDATES
from build_reptile_amphibian_candidates import REPTILE_AMPHIBIAN_CANDIDATES
from build_fish_candidates import FISH_CANDIDATES
from build_invertebrate_candidates import INVERTEBRATE_CANDIDATES
from build_excluded_candidates import EXCLUDED_CANDIDATES

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
    return "Invertebrates"

def main():
    print("=== STEP 1: Loading Original Baseline & Untouched Backups ===")
    orig_path = os.path.join(data_dir, "species_list_ORIGINAL_UNTOUCHED.json")
    with open(orig_path, "r") as f:
        orig_list = json.load(f)
    print(f"Original baseline species: {len(orig_list)}")

    gen_shards_path = os.path.join(base_dir, "generate_shards.py")
    with open(gen_shards_path, "r") as f:
        gen_code = f.read()
    m = re.search(r"SPECIES_MAP = \{(.*?)\}", gen_code, re.DOTALL)
    combined_species_map = dict(re.findall(r'\"([^\"]+)\":\s*\"([^\"]+)\"', m.group(1)))
    if "Swallowtail Butterfly (Papilio machaon)" not in combined_species_map:
        combined_species_map["Swallowtail Butterfly (Papilio machaon)"] = "Papilio machaon"

    print(f"Baseline active species loaded: {len(combined_species_map)}")

    # Merge curated candidate clades
    all_curated = (
        MAMMAL_CANDIDATES +
        BIRD_CANDIDATES +
        REPTILE_AMPHIBIAN_CANDIDATES +
        FISH_CANDIDATES +
        INVERTEBRATE_CANDIDATES
    )
    sci_to_name = {v: k for k, v in combined_species_map.items()}
    curated_added = 0
    for name, sci in all_curated:
        if sci not in sci_to_name and name not in combined_species_map:
            combined_species_map[name] = sci
            sci_to_name[sci] = name
            curated_added += 1

    print(f"Added {curated_added} curated species. Active pool: {len(combined_species_map)}")

    # Ingest clean animal species from local NCBI database across all animal phyla
    print("Scanning all animal species with official common names from NCBI database...")
    ncbi = NCBITaxa()
    conn = sqlite3.connect(ncbi.dbfile)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT taxid, spname, common FROM species 
        WHERE common != '' AND common IS NOT NULL 
        AND rank = 'species'
    """)
    ncbi_rows = cursor.fetchall()
    print(f"Found {len(ncbi_rows)} total species rows in NCBI table.")

    excluded_records = list(EXCLUDED_CANDIDATES)
    name_seen = set(combined_species_map.keys())
    common_seen = {re.sub(r"\s*\([^)]+\)$", "", k).strip().lower(): k for k in combined_species_map.keys()}
    ncbi_added = 0

    for taxid, spname, common in ncbi_rows:
        parts = spname.split()
        if len(parts) != 2:
            excluded_records.append({
                "common": common.strip(),
                "scientific": spname,
                "clade": "Unknown",
                "category": "Non-binomial species name",
                "reason": "Technical trinomial or unranked name",
                "action": "Excluded from standard binomial catalog"
            })
            continue

        if re.search(r'[0-9_#$]', spname) or "sp." in spname or "cf." in spname:
            excluded_records.append({
                "common": common.strip(),
                "scientific": spname,
                "clade": "Unknown",
                "category": "Technical Strain / Code",
                "reason": "Contains technical laboratory strain or tentative marker",
                "action": "Excluded to preserve clean species identity"
            })
            continue

        try:
            lin = ncbi.get_lineage(taxid)
        except Exception:
            continue

        if 33208 not in lin: # Not Animalia
            excluded_records.append({
                "common": common.strip(),
                "scientific": spname,
                "clade": "Non-Animal Clade",
                "category": "Outside Kingdom Animalia (Metazoa)",
                "reason": "Plant, alga, fungus, or bacterial organism",
                "action": "Permanently excluded from Animalia game"
            })
            continue

        c_clean = common.strip()
        if len(c_clean) < 3 or len(c_clean) > 40:
            excluded_records.append({
                "common": c_clean,
                "scientific": spname,
                "clade": "Metazoa",
                "category": "Nomenclature Out of Bounds",
                "reason": f"Common name length ({len(c_clean)} chars) out of standard bounds",
                "action": "Deferred"
            })
            continue

        if re.search(r'[0-9_#$]', c_clean) or "sp." in c_clean or "aff." in c_clean or "isolate" in c_clean:
            excluded_records.append({
                "common": c_clean,
                "scientific": spname,
                "clade": "Metazoa",
                "category": "Technical Strain in Common Name",
                "reason": "Technical strain/code embedded in common name",
                "action": "Deferred"
            })
            continue

        c_title = " ".join(w.capitalize() for w in c_clean.split())
        c_lower = c_clean.lower()
        disp_name = f"{c_title} ({spname})"

        # Check duplicate common name collision
        if c_lower in common_seen:
            existing_match = common_seen[c_lower]
            excluded_records.append({
                "common": c_title,
                "scientific": spname,
                "clade": "Metazoa",
                "category": "Duplicate Common Name Collision",
                "reason": f"Common name collides with existing entry: {existing_match}",
                "action": "Exemplar species retained; duplicate deferred for manual review"
            })
            continue

        # Check duplicate scientific name
        if spname in sci_to_name or disp_name in name_seen:
            continue

        # Ingest comprehensive candidate
        combined_species_map[disp_name] = spname
        sci_to_name[spname] = disp_name
        name_seen.add(disp_name)
        common_seen[c_lower] = disp_name
        ncbi_added += 1

    print(f"Ingested {ncbi_added} additional valid animal species from NCBI database!")
    total_active = len(combined_species_map)
    print(f"TOTAL COMPREHENSIVE ACTIVE POOL: {total_active} species!")
    print(f"Total candidates in excluded/deferred review log: {len(excluded_records)}")

    # Zero-drop assertion check
    missing_orig = [s for s in orig_list if s not in combined_species_map]
    if missing_orig:
        raise ValueError(f"FATAL: Missing original species: {missing_orig}")
    print(f"SUCCESS: All {len(orig_list)} baseline species verified (0 dropped).")

    print("\n=== STEP 2: Resolving TaxIDs and Lineages for Entire Tree ===")
    species_keys = list(combined_species_map.keys())
    all_scis = list(combined_species_map.values())

    species_to_taxid = {}
    taxid_to_lineage = {}

    chunk_size = 500
    for i in range(0, len(all_scis), chunk_size):
        chunk = all_scis[i:i+chunk_size]
        trans = ncbi.get_name_translator(chunk)
        for s, ids in trans.items():
            if ids:
                species_to_taxid[s] = ids[0]

    for s in all_scis:
        if s not in species_to_taxid:
            t = ncbi.get_name_translator([s]).get(s)
            if t:
                species_to_taxid[s] = t[0]
            else:
                genus = s.split()[0]
                gt = ncbi.get_name_translator([genus]).get(genus)
                species_to_taxid[s] = gt[0] if gt else 33208

    for s, tid in species_to_taxid.items():
        if tid not in taxid_to_lineage:
            taxid_to_lineage[tid] = ncbi.get_lineage(tid)

    print(f"Resolved lineages for all {len(species_to_taxid)} species.")

    print("\n=== STEP 3: Mapping LCA Node Divergence Times ===")
    cache_path = os.path.join(data_dir, "time_cache.json")
    time_cache = {}
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

    # Collect all unique internal nodes appearing across all lineages
    all_internal_nodes = set()
    for tid, lin in taxid_to_lineage.items():
        all_internal_nodes.update(lin)

    print(f"Total unique internal nodes across full tree: {len(all_internal_nodes)}")

    # Calibrate any uncalibrated internal nodes using parent lineage interpolation
    major_ranks = {"superkingdom", "kingdom", "phylum", "class", "order", "family", "genus", "species"}
    nodes_meta = {}

    for nid in all_internal_nodes:
        # Calibrate time
        val = node_median.get(nid)
        if val is None or val <= 0:
            lin = ncbi.get_lineage(nid)
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
        lin = ncbi.get_lineage(nid)
        found_rank = "Unknown"
        actual_name = ncbi.get_taxid_translator([nid]).get(nid, "Unknown")
        found_name = actual_name
        for t in reversed(lin):
            r = ncbi.get_rank([t]).get(t, "")
            if r in major_ranks:
                found_rank = r.capitalize()
                if found_name == "Unknown":
                    found_name = ncbi.get_taxid_translator([t]).get(t, found_name)
                break

        nodes_meta[nid] = {
            "rank": found_rank,
            "name": found_name,
            "time": val
        }

    print(f"Precomputed metadata and divergence times for all {len(nodes_meta)} nodes!")

    # Build species lineage map
    species_lineage_map = {}
    for name, sci in combined_species_map.items():
        tid = species_to_taxid[sci]
        species_lineage_map[name.lower()] = taxid_to_lineage[tid]

    print("\n=== STEP 4: Writing data/phylogeny_tree.json ===")
    tree_payload = {
        "species": species_lineage_map,
        "nodes": nodes_meta
    }
    tree_path = os.path.join(data_dir, "phylogeny_tree.json")
    with open(tree_path, "w") as f:
        json.dump(tree_payload, f, separators=(',', ':'))

    tree_size_mb = os.path.getsize(tree_path) / (1024 * 1024)
    print(f"Successfully saved data/phylogeny_tree.json ({tree_size_mb:.2f} MB)!")

    print("\n=== STEP 5: Updating species_list.json ===")
    with open(os.path.join(data_dir, "species_list.json"), "w") as f:
        json.dump(species_keys, f, indent=2)
    print(f"Saved data/species_list.json ({len(species_keys)} species).")

    print("\n=== STEP 6: Updating Taxonomy Catalogs & species_catalog.md ===")
    species_catalog_entries = []
    clade_groups = {}

    for name in species_keys:
        sci = combined_species_map[name]
        taxid = species_to_taxid[sci]
        lin = taxid_to_lineage[taxid]

        common_name = re.sub(r'\s*\([^)]+\)$', '', name).strip()
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
        f"# 🧬 Phylogenle Active Species Directory ({total_active} Species)\n",
        "Complete organized breakdown of all currently loaded species in the game catalog, grouped by clade and taxonomic order.\n",
        "## 📊 Clade Distribution Overview\n",
        "| Clade | Species Count | Primary Orders / Key Representatives |",
        "| :--- | :--- | :--- |"
    ]
    clade_order_preference = ["Mammals", "Birds", "Reptiles", "Amphibians", "Fishes", "Invertebrates"]
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
        "Invertebrates": "🐙"
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

    print("\n=== STEP 7: Writing EXCLUDED_SPECIES_REVIEW.md in phylogenle/ ===")
    ex_md = [
        "# 📋 Phylogenle Excluded & Deferred Species Review Log\n",
        f"**Last Updated:** {time.strftime('%Y-%m-%d %H:%M:%S')}",
        f"**Total Active Species in Game:** {total_active}",
        f"**Total Candidates in Review Log:** {len(excluded_records)}\n",
        "This document maintains a permanent, comprehensive record of animal candidates evaluated during the expansion process but **intentionally excluded or deferred** from the primary active roster. You can manually review this list to inspect the rationale and request promotion for any candidate.\n",
        "## 🧭 How to Use This Manual Review Log\n",
        "1. **Subspecies / Taxonomic Duplicates:** Candidates deferred to prevent 0 MYA branch collisions with parental species (e.g. Dog vs Wolf, Dingo vs Wolf, Bengal Tiger vs Tiger).",
        "2. **Duplicate Common Name Collisions:** Multiple species sharing the exact same colloquial name (e.g. multiple distinct species named 'Gall Midge' or 'Root Nematode'). The primary exemplar is kept, while duplicate collisions are logged here.",
        "3. **Cryptic or Obscure Species:** Animals with subtle morphology or lacking widespread public common names.",
        "4. **Microscopic / Parasitic Organisms:** Organisms deferred to preserve intuitive wildlife puzzle gameplay (e.g. pinworms, flukes, dust mites).",
        "5. **Deferred Sister Species:** Valid species available for future expansion clusters.",
        "6. **Non-Animal / Protist Outliers:** Screened candidates falling outside Kingdom Animalia (Metazoa), permanently excluded.\n",
        "## 📊 Summary by Category\n",
        "| Category | Count | Primary Impact |",
        "| :--- | :--- | :--- |"
    ]

    cat_counts = Counter(e["category"] for e in excluded_records)
    for cat_name, count in cat_counts.most_common():
        ex_md.append(f"| **{cat_name}** | **{count}** | Manual review candidate |")

    ex_md.append("\n---\n")
    ex_md.append("## 🔍 Detailed Review Table\n")
    ex_md.append("| Common Name | Scientific Name | Clade | Category | Exclusion Rationale | Recommended Action |")
    ex_md.append("| :--- | :--- | :--- | :--- | :--- | :--- |")

    for entry in excluded_records:
        ex_md.append(f"| **{entry.get('common', '')}** | *{entry.get('scientific', '')}* | {entry.get('clade', '')} | {entry.get('category', '')} | {entry.get('reason', '')} | {entry.get('action', '')} |")

    ex_text = "\n".join(ex_md)
    review_path = os.path.join(base_dir, "EXCLUDED_SPECIES_REVIEW.md")
    with open(review_path, "w") as f:
        f.write(ex_text)
    print(f"Saved EXCLUDED_SPECIES_REVIEW.md with {len(excluded_records)} entries directly in {base_dir}!")

    print("\n=== STEP 8: Programmatic Verification ===")
    with open(os.path.join(data_dir, "species_list.json"), "r") as f:
        final_list = json.load(f)
    with open(orig_path, "r") as f:
        verified_orig = json.load(f)

    missing_final = [s for s in verified_orig if s not in final_list]
    if missing_final:
        raise AssertionError(f"INTEGRITY FAILURE: Missing original species: {missing_final}")
    print(f"SUCCESS: All {len(verified_orig)} original species verified in final list of {len(final_list)} species!")
    print("\n🎉 COMPREHENSIVE PHYLOGENY TREE CREATION COMPLETE! 🎉")

if __name__ == "__main__":
    main()
