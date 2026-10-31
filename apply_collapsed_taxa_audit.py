#!/usr/bin/env python3
"""
Phylogenle - Apply Collapsed Taxa Audit Across All Files
Reads docs/AUDIT_COLLAPSED_ORGANISMS.json item by item and applies the fixes:
1. Restores the distinct specific common names for the single species in data/species_taxonomy_catalog.json.
2. Creates standalone higher-taxon umbrella entries (Genera, Families, Subfamilies, Orders, Phyla) with their true Wikipedia pageviews and Wikidata QIDs.
3. Synchronizes:
   - data/species_taxonomy_catalog.json (including synchronized `display` field)
   - data/species_list.json
   - data/phylogeny_tree.json (full root-to-taxon NCBI lineages under lowercase display keys)
   - data/species_aliases.json
   - data/wikimedia_popularity_cache.json
   - script.js (SPECIAL_GENUS_MAP)
   - check_original_344_in_top1k.py (SPECIAL_TAXA_344)
"""

import os
import sys
import json

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
    node_name_to_id = {n.get("name", "").lower(): int(tid) for tid, n in tree_nodes.items() if n.get("name")}

    tid_to_path = {}
    sci_to_path = {}
    for k, path in tree_species.items():
        if isinstance(path, list) and len(path) >= 2:
            for idx, tid in enumerate(path):
                if tid not in tid_to_path or len(path[: idx + 1]) > len(tid_to_path[tid]):
                    tid_to_path[tid] = path[: idx + 1]
            idx_p = k.find(" (")
            if idx_p != -1 and k.endswith(")"):
                s_low = k[idx_p + 2 : -1].strip().lower()
                sci_to_path[s_low] = path
            else:
                sci_to_path[k.lower()] = path

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

        # A. Restore specific species common name & display
        if sci in cat_by_sci:
            s_entry = cat_by_sci[sci]
            if s_entry["common"] != proper_common:
                print(f"  [Restore Species] {sci}: '{s_entry['common']}' -> '{proper_common}'")
                s_entry["common"] = proper_common
                species_restored_count += 1
            s_entry["display"] = f"{proper_common} ({sci})"
        else:
            print(f"  [Warning] Species {sci} not found in catalog!")
            s_entry = {
                "display": f"{proper_common} ({sci})",
                "common": proper_common,
                "scientific": sci,
                "kingdom": "Animalia",
                "rank": "species",
            }

        # B. Add / Ensure Umbrella Taxon in Catalog
        umb_display = f"{umb_common} ({umb_sci})"
        if umb_sci not in cat_by_sci:
            print(f"  [Add Umbrella] {umb_display} [{umb_rank}]")
            new_record = {
                "display": umb_display,
                "common": umb_common,
                "scientific": umb_sci,
                "kingdom": s_entry.get("kingdom", "Animalia"),
                "phylum": s_entry.get("phylum", ""),
                "class": s_entry.get("class", ""),
                "order": s_entry.get("order", ""),
                "family": s_entry.get("family", "") if umb_rank != "family" else umb_sci,
                "genus": umb_sci if umb_rank == "genus" else None,
                "species": None,
                "rank": umb_rank,
            }
            catalog.append(new_record)
            cat_by_sci[umb_sci] = new_record
            umbrellas_added_count += 1
        else:
            cat_by_sci[umb_sci]["common"] = umb_common
            cat_by_sci[umb_sci]["rank"] = umb_rank
            cat_by_sci[umb_sci]["display"] = umb_display

        # C. Update Popularity Cache using verified QID & swiki (never hardcoded Q1000000 / 60)
        existing_umb_cache = cache.get(umb_sci, {})
        cache[umb_sci] = {
            "common": umb_common,
            "scientific": umb_sci,
            "kingdom": s_entry.get("kingdom", "Animalia"),
            "class": s_entry.get("class", ""),
            "order": s_entry.get("order", ""),
            "family": s_entry.get("family", "") if umb_rank != "family" else umb_sci,
            "qid": item.get("qid") or existing_umb_cache.get("qid"),
            "swiki": item.get("swiki") or existing_umb_cache.get("swiki", 0),
            "en_title": (wiki_art or existing_umb_cache.get("en_title") or "").replace("_", " ") or None,
            "vwiki": umb_views if umb_views else existing_umb_cache.get("vwiki", 0),
            "vwiki_period": "vwiki_20250101_20261231",
            "canonical_verified": True,
        }
        if sci in cache:
            cache[sci]["common"] = proper_common

        # D. Ensure Full Root-to-Taxon Lineage in Phylogeny Tree for both Species and Umbrella
        spec_key = f"{proper_common} ({sci})".lower()
        if spec_key not in tree_species or len(tree_species[spec_key]) < 2:
            if sci.lower() in sci_to_path:
                tree_species[spec_key] = sci_to_path[sci.lower()]
            elif node_name_to_id.get(sci.lower()) in tid_to_path:
                tree_species[spec_key] = tid_to_path[node_name_to_id[sci.lower()]]

        umb_key = umb_display.lower()
        if umb_key not in tree_species or len(tree_species[umb_key]) < 2:
            tid = node_name_to_id.get(umb_sci.lower())
            if tid and tid in tid_to_path:
                tree_species[umb_key] = tid_to_path[tid]
            else:
                # Fallback to family/order node path
                fam_name = (cat_by_sci[umb_sci].get("family") or "").lower()
                fam_tid = node_name_to_id.get(fam_name)
                if fam_tid and fam_tid in tid_to_path:
                    tree_species[umb_key] = tid_to_path[fam_tid]
                elif sci.lower() in sci_to_path:
                    child_p = sci_to_path[sci.lower()]
                    tree_species[umb_key] = child_p[:-1] if len(child_p) > 2 else child_p

        # E. Add Aliases
        aliases[umb_common.lower()] = umb_display
        aliases[umb_sci.lower()] = umb_display
        spec_entry_str = f"{proper_common} ({sci})"
        aliases[proper_common.lower()] = spec_entry_str
        aliases[sci.lower()] = spec_entry_str

    # Synchronize display fields on all catalog entries
    for s in catalog:
        c = (s.get("common") or "").strip()
        sc = (s.get("scientific") or "").strip()
        s["display"] = f"{c} ({sc})" if c else sc

    print(f"\n✅ Restored {species_restored_count} single-species common names.")
    print(f"✅ Added/updated {len(audit_items)} umbrella taxa in catalog, tree, aliases, and cache.")

    # 3. Save Catalog
    with open(CATALOG_PATH, "w", encoding="utf-8") as f:
        json.dump(catalog, f, indent=2, ensure_ascii=False)
    print(f"✅ Saved catalog with {len(catalog):,} entries.")

    # 4. Rebuild Species List
    species_list = sorted(s["display"] for s in catalog)
    with open(SPECIES_LIST_PATH, "w", encoding="utf-8") as f:
        json.dump(species_list, f, indent=2, ensure_ascii=False)
    print(f"✅ Rebuilt species_list with {len(species_list):,} entries.")

    # Remove any orphaned keys from tree_species not in species_list
    valid_keys = {s.lower() for s in species_list}
    tree["species"] = {k: v for k, v in tree_species.items() if k in valid_keys}

    # 5. Save Tree, Aliases, Cache
    with open(TREE_PATH, "w", encoding="utf-8") as f:
        json.dump(tree, f, indent=2, ensure_ascii=False)
    print(f"✅ Saved phylogeny tree with {len(tree['species']):,} species/taxa paths.")

    with open(ALIASES_PATH, "w", encoding="utf-8") as f:
        json.dump(aliases, f, indent=2, ensure_ascii=False)
    print(f"✅ Saved aliases with {len(aliases):,} aliases.")

    with open(CACHE_PATH, "w", encoding="utf-8") as f:
        json.dump(cache, f, indent=2, ensure_ascii=False)
    print("✅ Saved popularity cache.")

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

    # 7. Update check_original_344_in_top1k.py (SPECIAL_TAXA_344)
    if os.path.exists(CHECK_SCRIPT_PATH):
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
