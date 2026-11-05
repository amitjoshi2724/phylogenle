#!/usr/bin/env python3
"""
Phylogenle - Species Common Name Override Manager (set_common_name_override.py)
=============================================================================
Allows manual overrides for species common names when the automated shortest-name
or sitelink heuristic did not choose the most ubiquitous/popular vernacular name
(e.g. setting "Honey Badger" instead of "Ratel" for Mellivora capensis).

Overrides are persisted in data/species_common_name_overrides.json and can be
applied idempotently across all dataset files:
  - data/species_taxonomy_catalog.json (updates 'common' and 'display')
  - data/species_list.json (updates autocomplete and search entries)
  - data/phylogeny_tree.json (updates tree['species'] lookup key while preserving lineages)
  - data/species_aliases.json (makes old name an alias to the new name, removes new name from alias keys)
  - data/wikimedia_popularity_cache.json (updates 'common' field)
  - species_catalog_taxonomic.md (regenerates the taxonomic markdown directory)

Usage:
  # Set an override by scientific name:
  python3 set_common_name_override.py "Mellivora capensis" "Honey Badger"

  # Or by current common name:
  python3 set_common_name_override.py "Ratel" "Honey Badger"

  # Or using flags:
  python3 set_common_name_override.py --set "Mellivora capensis" "Honey Badger"

  # List all active overrides:
  python3 set_common_name_override.py --list

  # Remove an override and restore original common name:
  python3 set_common_name_override.py --remove "Mellivora capensis"

  # Apply all current overrides from data/species_common_name_overrides.json to disk:
  python3 set_common_name_override.py --apply

  # Dry-run test (simulates changes without modifying files):
  python3 set_common_name_override.py --set "Mellivora capensis" "Honey Badger" --dry-run
"""

import os
import sys
import json
import argparse
import subprocess

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
OVERRIDES_PATH = os.path.join(DATA_DIR, "species_common_name_overrides.json")
CATALOG_PATH = os.path.join(DATA_DIR, "species_taxonomy_catalog.json")
SPECIES_LIST_PATH = os.path.join(DATA_DIR, "species_list.json")
TREE_PATH = os.path.join(DATA_DIR, "phylogeny_tree.json")
ALIASES_PATH = os.path.join(DATA_DIR, "species_aliases.json")
CACHE_PATH = os.path.join(DATA_DIR, "wikimedia_popularity_cache.json")
BUILD_CATALOG_SCRIPT = os.path.join(BASE_DIR, "build_taxonomic_catalog.py")


def load_json(filepath, default=None):
    if not os.path.exists(filepath):
        return default if default is not None else {}
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[-] Warning: Failed to load {filepath}: {e}")
        return default if default is not None else {}


def save_json(filepath, data, indent=2):
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=indent, ensure_ascii=False)
        f.write("\n")


def save_tree_formatted(tree_path, tree):
    """Write phylogeny_tree.json in the standard single-line-per-entry layout."""
    with open(tree_path, "w", encoding="utf-8") as f:
        f.write('{\n  "species": {\n')
        species_items = list(tree.get("species", {}).items())
        for i, (k, v) in enumerate(species_items):
            comma = "," if i < len(species_items) - 1 else ""
            f.write(f'    {json.dumps(k, ensure_ascii=False)}: {json.dumps(v, ensure_ascii=False)}{comma}\n')
        f.write('  },\n  "nodes": {\n')
        node_items = list(tree.get("nodes", {}).items())
        for i, (k, v) in enumerate(node_items):
            comma = "," if i < len(node_items) - 1 else ""
            f.write(f'    {json.dumps(k, ensure_ascii=False)}: {json.dumps(v, ensure_ascii=False)}{comma}\n')
        f.write('  }\n}\n')


def load_overrides():
    raw = load_json(OVERRIDES_PATH, default={})
    normalized = {}
    for k, v in raw.items():
        if isinstance(v, dict):
            normalized[k] = {
                "common": v.get("common", "").strip(),
                "original_common": v.get("original_common", "").strip()
            }
        elif isinstance(v, str):
            normalized[k] = {
                "common": v.strip(),
                "original_common": ""
            }
    return normalized


def save_overrides(overrides):
    # Formatted with readable dict structure
    ordered = dict(sorted(overrides.items(), key=lambda kv: kv[0].lower()))
    save_json(OVERRIDES_PATH, ordered, indent=2)


def find_species_in_catalog(catalog, query):
    """Search catalog by exact scientific name, display name, or common name (case-insensitive)."""
    q = query.strip().lower()

    # 1. Exact match on scientific name
    for s in catalog:
        if s.get("scientific", "").strip().lower() == q:
            return s, []

    # 2. Exact match on display name (e.g. 'Ratel (Mellivora capensis)')
    for s in catalog:
        if s.get("display", "").strip().lower() == q:
            return s, []

    # 3. Match on common name
    common_matches = [s for s in catalog if s.get("common", "").strip().lower() == q]
    if len(common_matches) == 1:
        return common_matches[0], []
    elif len(common_matches) > 1:
        return None, common_matches

    # 4. Partial / binomial match inside parentheses
    if "(" in query and ")" in query:
        inner = query[query.rfind("(") + 1 : query.rfind(")")].strip().lower()
        for s in catalog:
            if s.get("scientific", "").strip().lower() == inner:
                return s, []

    return None, []


def apply_overrides(overrides_dict=None, dry_run=False, verbose=True):
    """Apply all active overrides from data/species_common_name_overrides.json to data files."""
    overrides = overrides_dict if overrides_dict is not None else load_overrides()
    if verbose:
        print(f"[*] Processing {len(overrides)} override(s) from {OVERRIDES_PATH}")

    catalog = load_json(CATALOG_PATH, default=[])
    species_list = load_json(SPECIES_LIST_PATH, default=[])
    tree = load_json(TREE_PATH, default={"species": {}, "nodes": {}})
    aliases = load_json(ALIASES_PATH, default={})
    cache = load_json(CACHE_PATH, default={})

    if not catalog:
        print(f"[-] Error: Could not load {CATALOG_PATH}")
        return False

    cat_by_sci = {s["scientific"].strip(): s for s in catalog}
    species_list_set = set(species_list)
    tree_species = tree.get("species", {})

    modified_count = 0
    alias_updates = 0

    for sci_key, entry in overrides.items():
        new_common = entry.get("common", "").strip()
        if not new_common:
            continue

        target_species = None
        for s in catalog:
            if s["scientific"].strip().lower() == sci_key.lower():
                target_species = s
                break

        if not target_species:
            if verbose:
                print(f"[-] Warning: Scientific name '{sci_key}' from overrides not found in catalog. Skipping.")
            continue

        sci = target_species["scientific"]
        old_common = target_species.get("common", "").strip()
        old_display = target_species.get("display", f"{old_common} ({sci})")
        new_display = f"{new_common} ({sci})"

        if old_common == new_common and old_display == new_display:
            continue  # Already up to date

        if verbose:
            print(f"[+] Overriding: '{old_display}' -> '{new_display}'")

        modified_count += 1

        # 1. Update Catalog
        target_species["common"] = new_common
        target_species["display"] = new_display

        # 2. Update species_list.json
        if old_display in species_list_set:
            species_list_set.remove(old_display)
        species_list_set.add(new_display)

        # 3. Update phylogeny_tree.json ['species']
        old_tree_key = old_display.lower()
        new_tree_key = new_display.lower()
        if old_tree_key in tree_species:
            lineage = tree_species.pop(old_tree_key)
            tree_species[new_tree_key] = lineage

        # 4. Update species_aliases.json
        # The new common name and new display must NOT be alias keys pointing elsewhere
        aliases.pop(new_common.lower(), None)
        aliases.pop(new_display.lower(), None)

        # Make old common name and old display point as aliases to new display
        if old_common and old_common.lower() != new_common.lower():
            aliases[old_common.lower()] = new_display
            alias_updates += 1
        if old_display.lower() != new_display.lower():
            aliases[old_display.lower()] = new_display
            alias_updates += 1

        # Update any existing aliases that pointed to the old display
        for a_key, a_target in list(aliases.items()):
            if a_target == old_display:
                aliases[a_key] = new_display
                alias_updates += 1

        # 5. Update popularity cache if present
        if sci in cache:
            cache[sci]["common"] = new_common

    # Ensure species_list order is sorted deterministically
    sorted_species_list = sorted(list(species_list_set))

    # Clean up any alias keys that might shadow primary names
    primary_names = set()
    for s in catalog:
        primary_names.add(s["display"].lower())
        primary_names.add(s["scientific"].lower())
        if s.get("common"):
            primary_names.add(s["common"].lower())

    for prim in primary_names:
        aliases.pop(prim, None)

    # Sort aliases deterministically
    sorted_aliases = dict(sorted(aliases.items(), key=lambda kv: kv[0]))

    if dry_run:
        print(f"\n[--dry-run] Would update {modified_count} species and {alias_updates} alias links across datasets.")
        return True

    if modified_count > 0 or len(overrides) == 0:
        print(f"[*] Writing updates to {CATALOG_PATH}...")
        save_json(CATALOG_PATH, catalog)

        print(f"[*] Writing updates to {SPECIES_LIST_PATH}...")
        save_json(SPECIES_LIST_PATH, sorted_species_list)

        print(f"[*] Writing updates to {TREE_PATH}...")
        save_tree_formatted(TREE_PATH, tree)

        print(f"[*] Writing updates to {ALIASES_PATH}...")
        save_json(ALIASES_PATH, sorted_aliases)

        if cache:
            save_json(CACHE_PATH, cache)

        # Regenerate species_catalog_taxonomic.md if builder script exists
        if os.path.exists(BUILD_CATALOG_SCRIPT):
            try:
                print(f"[*] Regenerating species_catalog_taxonomic.md...")
                subprocess.run([sys.executable, BUILD_CATALOG_SCRIPT], check=True, capture_output=True)
            except Exception as e:
                print(f"[-] Warning: Failed to rebuild species_catalog_taxonomic.md: {e}")

        print(f"\n[+] Successfully applied {modified_count} override(s) across all game datasets.")
    else:
        if verbose:
            print("[+] All dataset files are already completely in sync with overrides.")

    return True


def cmd_set(target_query, new_common_name, dry_run=False):
    catalog = load_json(CATALOG_PATH, default=[])
    species, ambig = find_species_in_catalog(catalog, target_query)

    if ambig:
        print(f"[-] Ambiguous common name '{target_query}' matches {len(ambig)} species:")
        for s in ambig[:10]:
            print(f"    - {s.get('display')} [{s.get('scientific')}]")
        print("Please specify the scientific name (e.g. python3 set_common_name_override.py \"Scientific Name\" \"New Common Name\").")
        return False

    if not species:
        print(f"[-] Error: Could not find any species matching '{target_query}' in catalog.")
        return False

    sci = species["scientific"]
    current_common = species.get("common", "")
    new_common = new_common_name.strip()

    if not new_common:
        print("[-] Error: New common name cannot be empty.")
        return False

    overrides = load_overrides()
    orig = overrides.get(sci, {}).get("original_common") or current_common

    overrides[sci] = {
        "common": new_common,
        "original_common": orig
    }

    print(f"[+] Recording override for {sci}: '{current_common}' -> '{new_common}' (Original: '{orig}')")
    if not dry_run:
        save_overrides(overrides)

    return apply_overrides(overrides_dict=overrides, dry_run=dry_run)


def cmd_remove(target_query, dry_run=False):
    catalog = load_json(CATALOG_PATH, default=[])
    species, ambig = find_species_in_catalog(catalog, target_query)

    overrides = load_overrides()

    sci_to_remove = None
    if species:
        sci = species["scientific"]
        if sci in overrides:
            sci_to_remove = sci
    else:
        # Check direct key match in overrides
        for k in overrides:
            if k.lower() == target_query.strip().lower():
                sci_to_remove = k
                break

    if not sci_to_remove:
        print(f"[-] Error: No active override found for '{target_query}'.")
        return False

    override_entry = overrides[sci_to_remove]
    orig_common = override_entry.get("original_common", "")

    print(f"[+] Removing override for {sci_to_remove} (Restoring original: '{orig_common}')")

    # If original_common is known, restore it in the catalog temporarily before re-applying
    if orig_common:
        for s in catalog:
            if s["scientific"] == sci_to_remove:
                old_display = s["display"]
                s["common"] = orig_common
                new_display = f"{orig_common} ({sci_to_remove})"
                s["display"] = new_display

                # Update species_list
                species_list = load_json(SPECIES_LIST_PATH, default=[])
                if old_display in species_list:
                    species_list.remove(old_display)
                species_list.append(new_display)
                species_list.sort()
                if not dry_run:
                    save_json(SPECIES_LIST_PATH, species_list)

                # Update phylogeny_tree
                tree = load_json(TREE_PATH, default={"species": {}, "nodes": {}})
                if old_display.lower() in tree.get("species", {}):
                    lineage = tree["species"].pop(old_display.lower())
                    tree["species"][new_display.lower()] = lineage
                    if not dry_run:
                        save_tree_formatted(TREE_PATH, tree)

                # Update aliases
                aliases = load_json(ALIASES_PATH, default={})
                current_comm = override_entry.get("common", "")
                if current_comm:
                    aliases[current_comm.lower()] = new_display
                aliases.pop(orig_common.lower(), None)
                for a_k, a_t in list(aliases.items()):
                    if a_t == old_display:
                        aliases[a_k] = new_display
                if not dry_run:
                    save_json(ALIASES_PATH, aliases)
                break

        if not dry_run:
            save_json(CATALOG_PATH, catalog)

    if not dry_run:
        overrides.pop(sci_to_remove, None)
        save_overrides(overrides)

    print(f"[+] Override for {sci_to_remove} successfully removed.")
    return apply_overrides(overrides_dict=overrides, dry_run=dry_run)


def cmd_list():
    overrides = load_overrides()
    if not overrides:
        print("[*] No custom common name overrides defined in data/species_common_name_overrides.json")
        print("    Add one with: python3 set_common_name_override.py \"Scientific Name\" \"New Common Name\"")
        return

    print("=" * 80)
    print(f"🧬 Active Species Common Name Overrides ({len(overrides)} total)")
    print("=" * 80)
    print(f"{'Scientific Name':<32} {'Override Common Name':<26} {'Original Common Name':<20}")
    print("-" * 80)
    for sci, data in sorted(overrides.items()):
        comm = data.get("common", "")
        orig = data.get("original_common", "")
        print(f"{sci:<32} {comm:<26} {orig:<20}")
    print("=" * 80)


def main():
    parser = argparse.ArgumentParser(
        description="Manage manual species common name overrides for Phylogenle.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 set_common_name_override.py "Mellivora capensis" "Honey Badger"
  python3 set_common_name_override.py "Ratel" "Honey Badger"
  python3 set_common_name_override.py --list
  python3 set_common_name_override.py --remove "Mellivora capensis"
  python3 set_common_name_override.py --apply
        """
    )
    parser.add_argument("target", nargs="?", help="Scientific name, current common name, or display string")
    parser.add_argument("new_common", nargs="?", help="New desired common name (e.g. 'Honey Badger')")
    parser.add_argument("--set", nargs=2, metavar=("TARGET", "NEW_NAME"), help="Set an override")
    parser.add_argument("--remove", "--delete", metavar="TARGET", help="Remove an override and restore original")
    parser.add_argument("--list", action="store_true", help="List all defined overrides")
    parser.add_argument("--apply", action="store_true", help="Re-apply all overrides from JSON to dataset files")
    parser.add_argument("--dry-run", action="store_true", help="Simulate actions without writing to disk")

    args = parser.parse_args()

    if args.list:
        cmd_list()
        return

    if args.apply:
        apply_overrides(dry_run=args.dry_run)
        return

    if args.remove:
        cmd_remove(args.remove, dry_run=args.dry_run)
        return

    if args.set:
        cmd_set(args.set[0], args.set[1], dry_run=args.dry_run)
        return

    if args.target and args.new_common:
        cmd_set(args.target, args.new_common, dry_run=args.dry_run)
        return

    parser.print_help()


if __name__ == "__main__":
    main()
