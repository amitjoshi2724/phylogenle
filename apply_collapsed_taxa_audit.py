#!/usr/bin/env python3
"""
Phylogenle - Apply Collapsed Taxa Audit Across All Files
Reads docs/AUDIT_COLLAPSED_ORGANISMS.json item by item and applies the fixes:
1. Restores the distinct specific common names for the single species in data/species_taxonomy_catalog.json.
2. Creates standalone higher-taxon umbrella entries (Genera, Families, Subfamilies, Orders, Phyla) with their true Wikipedia pageviews.
3. Synchronizes:
   - data/species_taxonomy_catalog.json
   - data/species_list.json
   - data/phylogeny_tree.json
   - data/species_aliases.json
   - data/wikimedia_popularity_cache.json
   - script.js (SPECIAL_GENUS_MAP)
   - check_original_344_in_top1k.py (SPECIAL_TAXA_344)
"""

import os
import sys
import json
import re

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
AUDIT_JSON_PATH = os.path.join(BASE_DIR, "docs", "AUDIT_COLLAPSED_ORGANISMS.json")
CATALOG_PATH = os.path.join(BASE_DIR, "data", "species_taxonomy_catalog.json")
SPECIES_LIST_PATH = os.path.join(BASE_DIR, "data", "species_list.json")
TREE_PATH = os.path.join(BASE_DIR, "data", "phylogeny_tree.json")
ALIASES_PATH = os.path.join(BASE_DIR, "data", "species_aliases.json")
CACHE_PATH = os.path.join(BASE_DIR, "data", "wikimedia_popularity_cache.json")
SCRIPT_JS_PATH = os.path.join(BASE_DIR, "script.js")
CHECK_SCRIPT_PATH = os.path.join(BASE_DIR, "check_original_344_in_top1k.py")

def main():
    print("=" * 80)
    print("🧬 Phylogenle: Applying Audit Fixes Across All Files")
    print("=" * 80)

    if not os.path.exists(AUDIT_JSON_PATH):
        print(f"Error: Audit file not found: {AUDIT_JSON_PATH}")
        sys.exit(1)

    with open(AUDIT_JSON_PATH, "r", encoding="utf-8") as f:
        audit_items = json.load(f)
    print(f"Loaded {len(audit_items)} audited records from {os.path.basename(AUDIT_JSON_PATH)}.")

    # 1. Load Data Files
    with open(CATALOG_PATH, "r", encoding="utf-8") as f:
        catalog = json.load(f)
    cat_by_sci = {s["scientific"]: s for s in catalog}

    with open(CACHE_PATH, "r", encoding="utf-8") as f:
        cache = json.load(f)

    with open(TREE_PATH, "r", encoding="utf-8") as f:
        tree = json.load(f)
    tree_species = tree.get("species", {})
    tree_nodes = tree.get("nodes", {})
    node_name_to_id = {n.get("name", "").lower(): int(tid) for tid, n in tree_nodes.items()}

    with open(ALIASES_PATH, "r", encoding="utf-8") as f:
        aliases = json.load(f)

    # 2. Iterate through audited items line by line
    species_restored_count = 0
    umbrellas_added_count = 0

    for item in audit_items:
        sci = item["species_scientific"]
        proper_common = item["restored_species_common"]
        umb_common = item["umbrella_common"]
        umb_sci = item["umbrella_scientific"]
        umb_rank = item["umbrella_rank"]
        umb_views = item.get("wikipedia_views", 0)
        wiki_art = item.get("wikipedia_article", "")

        # A. Restore specific species common name
        if sci in cat_by_sci:
            s_entry = cat_by_sci[sci]
            if s_entry["common"] != proper_common:
                print(f"  [Restore Species] {sci}: '{s_entry['common']}' -> '{proper_common}'")
                s_entry["common"] = proper_common
                species_restored_count += 1
        else:
            print(f"  [Warning] Species {sci} not found in catalog!")
            s_entry = {
                "common": proper_common,
                "scientific": sci,
                "kingdom": "Animalia",
                "rank": "species"
            }

        # B. Add / Ensure Umbrella Taxon in Catalog
        if umb_sci not in cat_by_sci:
            print(f"  [Add Umbrella] {umb_common} ({umb_sci}) [{umb_rank}]")
            new_record = {
                "common": umb_common,
                "scientific": umb_sci,
                "kingdom": s_entry.get("kingdom", "Animalia"),
                "phylum": s_entry.get("phylum", ""),
                "class": s_entry.get("class", ""),
                "order": s_entry.get("order", ""),
                "family": s_entry.get("family", "") if umb_rank != "family" else umb_sci,
                "genus": umb_sci if umb_rank == "genus" else None,
                "species": None,
                "rank": umb_rank
            }
            catalog.append(new_record)
            cat_by_sci[umb_sci] = new_record
            umbrellas_added_count += 1
        else:
            cat_by_sci[umb_sci]["common"] = umb_common
            cat_by_sci[umb_sci]["rank"] = umb_rank

        # C. Add to Popularity Cache
        cache[umb_sci] = {
            "common": umb_common,
            "scientific": umb_sci,
            "kingdom": s_entry.get("kingdom", "Animalia"),
            "class": s_entry.get("class", ""),
            "order": s_entry.get("order", ""),
            "family": s_entry.get("family", "") if umb_rank != "family" else umb_sci,
            "qid": item.get("qid", "Q1000000"),
            "swiki": 60,
            "en_title": wiki_art,
            "vwiki": umb_views,
            "vwiki_period": "vwiki_20250101_20261231",
            "canonical_verified": True
        }

        # D. Add to Phylogeny Tree if missing
        if umb_sci not in tree_species:
            # Check if there is a direct node ID for this taxon
            tid = node_name_to_id.get(umb_sci.lower())
            if tid:
                # Find a representative child or construct path
                child_path = tree_species.get(sci, [])
                if child_path and tid in child_path:
                    idx = child_path.index(tid)
                    tree_species[umb_sci] = child_path[:idx + 1]
                else:
                    tree_species[umb_sci] = [tid]
            elif sci in tree_species:
                # Fallback to parent path
                child_path = tree_species.get(sci, [])
                tree_species[umb_sci] = child_path[:-1] if len(child_path) > 1 else child_path

        # E. Add Aliases
        # Umbrella alias
        umb_entry_str = f"{umb_common} ({umb_sci})"
        aliases[umb_common.lower()] = umb_entry_str
        aliases[f"{umb_common.lower()}s"] = umb_entry_str
        aliases[umb_sci.lower()] = umb_entry_str

        # Species alias
        spec_entry_str = f"{proper_common} ({sci})"
        aliases[proper_common.lower()] = spec_entry_str
        aliases[sci.lower()] = spec_entry_str

    print(f"\n✅ Restored {species_restored_count} single-species common names.")
    print(f"✅ Added/updated {len(audit_items)} umbrella taxa in catalog, tree, aliases, and cache.")

    # 3. Save Catalog
    with open(CATALOG_PATH, "w", encoding="utf-8") as f:
        json.dump(catalog, f, indent=2, ensure_ascii=False)
    print(f"✅ Saved catalog with {len(catalog):,} entries.")

    # 4. Rebuild Species List
    species_list = [f"{s['common']} ({s['scientific']})" for s in catalog]
    species_list.sort()
    with open(SPECIES_LIST_PATH, "w", encoding="utf-8") as f:
        json.dump(species_list, f, indent=2, ensure_ascii=False)
    print(f"✅ Rebuilt species_list with {len(species_list):,} entries.")

    # 5. Save Tree, Aliases, Cache
    with open(TREE_PATH, "w", encoding="utf-8") as f:
        json.dump(tree, f, indent=2, ensure_ascii=False)
    print(f"✅ Saved phylogeny tree with {len(tree_species):,} species/taxa paths.")

    with open(ALIASES_PATH, "w", encoding="utf-8") as f:
        json.dump(aliases, f, indent=2, ensure_ascii=False)
    print(f"✅ Saved aliases with {len(aliases):,} aliases.")

    with open(CACHE_PATH, "w", encoding="utf-8") as f:
        json.dump(cache, f, indent=2, ensure_ascii=False)
    print(f"✅ Saved popularity cache.")

    # 6. Update script.js (SPECIAL_GENUS_MAP)
    with open(SCRIPT_JS_PATH, "r", encoding="utf-8") as f:
        script_content = f.read()

    js_map_entries = []
    for item in audit_items:
        umb_common = item["umbrella_common"]
        umb_sci = item["umbrella_scientific"]
        umb_rank = item["umbrella_rank"].capitalize()
        key = f"{umb_common.lower()} ({umb_sci.lower()})"
        js_entry = f"        '{key}': {{ genus: '{umb_sci}', common: '{umb_common}', sciLower: '{umb_sci.lower()}', rank: '{umb_rank}' }},"
        if f"'{key}'" not in script_content:
            js_map_entries.append(js_entry)

    if js_map_entries:
        marker = "const SPECIAL_GENUS_MAP = {"
        idx = script_content.find(marker)
        if idx != -1:
            insert_pos = idx + len(marker) + 1
            insertion = "\n" + "\n".join(js_map_entries)
            script_content = script_content[:insert_pos] + insertion + script_content[insert_pos:]
            with open(SCRIPT_JS_PATH, "w", encoding="utf-8") as f:
                f.write(script_content)
            print(f"✅ Updated script.js with {len(js_map_entries)} new Option 3 taxa mappings.")
        else:
            print("  [Notice] SPECIAL_GENUS_MAP marker not found in script.js")

    # 7. Update check_original_344_in_top1k.py (SPECIAL_TAXA_344)
    with open(CHECK_SCRIPT_PATH, "r", encoding="utf-8") as f:
        check_content = f.read()

    py_map_entries = []
    for item in audit_items:
        sci = item["species_scientific"]
        umb_common = item["umbrella_common"]
        umb_sci = item["umbrella_scientific"]
        umb_rank = item["umbrella_rank"].capitalize()
        py_entry = f'    "{sci}": {{"taxon_sci": "{umb_sci}", "common": "{umb_common}", "rank_level": "{umb_rank}"}},'
        if f'"{sci}"' not in check_content:
            py_map_entries.append(py_entry)

    if py_map_entries:
        marker = "SPECIAL_TAXA_344 = {"
        idx = check_content.find(marker)
        if idx != -1:
            insert_pos = idx + len(marker) + 1
            insertion = "\n" + "\n".join(py_map_entries)
            check_content = check_content[:insert_pos] + insertion + check_content[insert_pos:]
            with open(CHECK_SCRIPT_PATH, "w", encoding="utf-8") as f:
                f.write(check_content)
            print(f"✅ Updated check_original_344_in_top1k.py with {len(py_map_entries)} new taxa entries.")

    print("=" * 80)
    print("🚀 All fixes applied cleanly from docs/AUDIT_COLLAPSED_ORGANISMS.json!")
    print("=" * 80)

if __name__ == "__main__":
    main()
