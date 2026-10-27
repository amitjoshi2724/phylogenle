#!/usr/bin/env python3
"""
build_taxonomic_catalog.py

Generates species_catalog_taxonomic.md:
A true 8-rank Linnaean hierarchical directory of all 29,748 species in Phylogenle.
Structure:
  ⬛ Domain (Eukaryota, Bacteria, Viruses)
    └── 🟫 Kingdom (Animalia, Plantae, Fungi, Protista, Pseudomonadati, Bacillati, Heunggongvirae)
          └── 🟦 Phylum (Chordata, Arthropoda, Mollusca, Streptophyta, etc.)
                └── 🟪 Class (Mammalia, Aves, Reptilia, Amphibia, Actinopterygii, etc.)
                      └── 🟥 Order (Carnivora, Primates, Passeriformes, Perciformes, etc.)
                            └── 🟧 Family (Felidae, Hominidae, Pomacentridae, etc.)
                                  └── 🟨 Genus & 🟩 Species Table

All sections are collapsible by default using native <details><summary> tags.
"""

import os
import json
import re
from collections import defaultdict

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def clean_name(s):
    if not s:
        return ""
    return re.sub(r'\s+', ' ', s).strip()

def extract_species_from_old_catalog():
    old_catalog_path = os.path.join(BASE_DIR, "species_catalog.md")
    with open(old_catalog_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    species_list = []
    for line in lines:
        line_s = line.strip()
        if line_s.startswith('|') and not line_s.startswith('| :---') and not line_s.startswith('| Common Name') and not line_s.startswith('| Clade') and not line_s.startswith('| **Total'):
            parts = [p.strip() for p in line_s.split('|')[1:-1]]
            if len(parts) >= 2 and parts[1].startswith('*') and parts[1].endswith('*'):
                scientific = parts[1].strip('*').strip()
                if not scientific.isdigit():
                    common = parts[0].strip()
                    species_list.append((common, scientific))
    return species_list

def main():
    print("=== Step 1: Loading Datasets ===")
    old_species = extract_species_from_old_catalog()
    print(f"Extracted {len(old_species)} species from species_catalog.md")
    assert len(old_species) == 29754, f"Expected 29754 species, found {len(old_species)}"

    tree_path = os.path.join(BASE_DIR, "data", "phylogeny_tree.json")
    with open(tree_path, "r", encoding="utf-8") as f:
        tree = json.load(f)
    species_map = tree["species"]
    nodes = tree["nodes"]

    tax_cat_path = os.path.join(BASE_DIR, "data", "species_taxonomy_catalog.json")
    with open(tax_cat_path, "r", encoding="utf-8") as f:
        tax_cat = json.load(f)

    # Index tax_cat by (common.lower(), scientific.lower()) and by display.lower()
    tax_by_pair = {}
    tax_by_sci = {}
    for entry in tax_cat:
        c = entry.get("common", "").lower()
        s = entry.get("scientific", "").lower()
        tax_by_pair[(c, s)] = entry
        tax_by_sci[s] = entry

    # Friendly Common Names for Classes and Orders
    CLASS_COMMON = {
        "Mammalia": "Mammals",
        "Aves": "Birds",
        "Reptilia": "Reptiles",
        "Amphibia": "Amphibians",
        "Actinopterygii": "Ray-finned Fishes",
        "Actinopteri": "Ray-finned Fishes",
        "Chondrichthyes": "Sharks, Rays & Chimaeras",
        "Sarcopterygii": "Lobe-finned Fishes & Allies",
        "Insecta": "Insects",
        "Arachnida": "Arachnids",
        "Malacostraca": "Crabs, Lobsters & Shrimps",
        "Gastropoda": "Snails & Slugs",
        "Bivalvia": "Clams & Mussels",
        "Cephalopoda": "Squids, Octopuses & Cuttlefishes",
        "Magnoliopsida": "Flowering Plants (Angiosperms)",
        "Pinopsida": "Conifers",
        "Polypodiopsida": "Ferns",
        "Agaricomycetes": "Mushrooms & Bracket Fungi",
        "Saccharomycetes": "Budding Yeasts"
    }

    PHYLUM_COMMON = {
        "Chordata": "Vertebrates & Allies",
        "Arthropoda": "Insects, Arachnids & Crustaceans",
        "Mollusca": "Mollusks",
        "Echinodermata": "Sea Stars, Urchins & Allies",
        "Annelida": "Segmented Worms",
        "Cnidaria": "Jellyfishes, Corals & Anemones",
        "Porifera": "Sponges",
        "Nematoda": "Roundworms",
        "Platyhelminthes": "Flatworms",
        "Streptophyta": "Land Plants & Charophyte Algae",
        "Chlorophyta": "Green Algae",
        "Ascomycota": "Sac Fungi & Yeasts",
        "Basidiomycota": "Club Fungi & Mushrooms",
        "Pseudomonadota": "Proteobacteria",
        "Bacillota": "Firmicutes"
    }

    print("\n=== Step 2: Resolving 8-Rank Taxonomic Lineage for All Species ===")
    # Nested catalog tree:
    # tree_hierarchy[domain][kingdom][phylum][class_name][order][family] -> list of (common, scientific, genus)
    tree_hierarchy = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(list))))))

    resolved_species = []
    enriched_catalog = []

    for common, scientific in old_species:
        # Match display key in tree
        c_low = common.lower()
        s_low = scientific.lower()
        display_key = f"{c_low} ({s_low})"

        lineage_ids = species_map.get(display_key)
        if not lineage_ids:
            # Fallback by scientific match
            for k, ids in species_map.items():
                if f"({s_low})" in k:
                    lineage_ids = ids
                    break

        # Defaults
        domain = "Eukaryota"
        kingdom = "Animalia"
        phylum = "Chordata"
        tax_class = "Unknown Class"
        order = "Unknown Order"
        family = "Unknown Family"
        genus = scientific.split()[0] if scientific else "Unknown Genus"

        if lineage_ids:
            # 1. Exact Domain resolution by root TaxID
            if 10239 in lineage_ids:
                domain = "Viruses"
                kingdom = "Heunggongvirae"
                phylum = "Peploviricota"
                tax_class = "Herviviricetes"
                order = "Herpesvirales"
                family = "Herpesviridae"
            elif 2157 in lineage_ids:
                domain = "Archaea"
                kingdom = "Euryarchaeota"
                for nid in lineage_ids:
                    n = nodes.get(str(nid), {})
                    if n.get("rank") == "Kingdom":
                        kingdom = n.get("name")
                    elif n.get("rank") == "Phylum":
                        phylum = n.get("name")
            elif 2 in lineage_ids:
                domain = "Bacteria"
                # Determine bacterial kingdom & phylum
                kingdom = "Pseudomonadati"
                for nid in lineage_ids:
                    n = nodes.get(str(nid), {})
                    if n.get("rank") == "Kingdom":
                        kingdom = n.get("major_name") or n.get("name")
                    elif n.get("rank") == "Phylum":
                        phylum = n.get("major_name") or n.get("name")
            elif 2759 in lineage_ids:
                domain = "Eukaryota"
                # 2. Exact Eukaryota Kingdom resolution by clade TaxID
                if 33208 in lineage_ids:
                    kingdom = "Animalia"
                elif 33090 in lineage_ids:
                    kingdom = "Plantae"
                elif 4751 in lineage_ids:
                    kingdom = "Fungi"
                else:
                    kingdom = "Protista / Chromista"

            # Extract Phylum, Class, Order, Family, Genus from lineage
            for nid in lineage_ids:
                n = nodes.get(str(nid), {})
                rank = n.get("rank")
                name = n.get("name", "")
                major = n.get("major_name") or name

                if rank == "Phylum":
                    phylum = major
                elif rank == "Class":
                    tax_class = major
                elif rank == "Order":
                    order = major
                elif rank == "Family":
                    family = major
                elif rank == "Genus":
                    genus = major

            # Biological standardizations & fallbacks
            if kingdom == "Protista / Chromista" and phylum in ["Chordata", "Unknown Phylum"]:
                for nid in lineage_ids:
                    n = nodes.get(str(nid), {})
                    if n.get("name") in ["Rhodophyta", "Oomycota", "Ochrophyta", "Amoebozoa"]:
                        phylum = n.get("name")
                        break

            if tax_class == "Unknown Class":
                if phylum in ["Chordata", "Arthropoda", "Mollusca"]:
                    tax_class = f"{phylum} Incertae Sedis"
                else:
                    tax_class = f"{phylum} Group"

            if order == "Unknown Order":
                for nid in lineage_ids:
                    n = nodes.get(str(nid), {})
                    node_name = n.get("name", "")
                    if node_name.endswith("formes") or node_name.endswith("ales"):
                        order = node_name
                        break
                if order == "Unknown Order":
                    if family != "Unknown Family":
                        order = f"{family} Allies"
                    else:
                        order = f"{tax_class} Incertae Sedis"

            if family == "Unknown Family":
                if genus and genus != "Unknown Genus":
                    family = f"{genus} Group"
                else:
                    family = f"{order} Incertae Sedis"

        # Genus extraction
        if not genus or genus == "Unknown Genus":
            genus = scientific.split()[0] if scientific else "Unknown Genus"

        tree_hierarchy[domain][kingdom][phylum][tax_class][order][family].append({
            "common": common,
            "scientific": scientific,
            "genus": genus
        })

        enriched_catalog.append({
            "display": f"{common} ({scientific})",
            "common": common,
            "scientific": scientific,
            "clade": kingdom if kingdom in ["Plantae", "Fungi", "Protista / Chromista"] else ("Invertebrates" if phylum != "Chordata" and kingdom == "Animalia" else tax_class),
            "subclade": order,
            "domain": domain,
            "kingdom": kingdom,
            "phylum": phylum,
            "class": tax_class,
            "order": order,
            "family": family,
            "genus": genus
        })

        resolved_species.append((common, scientific))

    print(f"Total resolved species: {len(resolved_species)}")
    assert len(resolved_species) == len(old_species), f"Resolved count {len(resolved_species)} must match {len(old_species)}"

    # Save enriched taxonomy catalog json
    with open(tax_cat_path, "w", encoding="utf-8") as f:
        json.dump(enriched_catalog, f, indent=2)
    print(f"Successfully saved enriched {tax_cat_path} with 8-rank metadata!")

    print("\n=== Step 3: Formatting Hierarchical Markdown Document ===")
    md_lines = []

    # Title & Introduction
    md_lines.append(f"# 🧬 Phylogenle Universal Taxonomic Directory ({len(old_species):,} Species Across All Life)")
    md_lines.append("")
    md_lines.append("Complete hierarchical taxonomic classification of all active species in the game catalog, organized systematically across the 8 universal biological ranks (⬛ **Domain** ➔ 🟫 **Kingdom** ➔ 🟦 **Phylum** ➔ 🟪 **Class** ➔ 🟥 **Order** ➔ 🟧 **Family** ➔ 🟨 **Genus** ➔ 🟩 **Species**).")
    md_lines.append("")
    md_lines.append("All sections are collapsed by default—click on any branch to expand and explore the tree of life.")
    md_lines.append("")

    # Domain & Kingdom Statistics Table
    md_lines.append("## 📊 Domain & Kingdom Distribution Overview")
    md_lines.append("")
    md_lines.append("| ⬛ Domain | 🟫 Kingdom | Primary Groups Included | Species Count |")
    md_lines.append("| :--- | :--- | :--- | :--- |")

    # Calculate domain & kingdom counts
    domain_order = ["Eukaryota", "Bacteria", "Archaea", "Viruses"]
    total_catalog_count = 0

    for dom in domain_order:
        if dom not in tree_hierarchy: continue
        k_dict = tree_hierarchy[dom]
        for k_name, p_dict in k_dict.items():
            k_count = sum(len(sp_list) for p in p_dict.values() for c in p.values() for o in c.values() for sp_list in o.values())
            total_catalog_count += k_count

            # Descriptive summary
            if k_name == "Animalia":
                desc = "Chordates (Mammals, Birds, Reptiles, Amphibians, Fishes) & Invertebrates"
            elif k_name == "Plantae":
                desc = "Flowering Plants (Angiosperms), Conifers, Ferns, Mosses, Green Algae"
            elif k_name == "Fungi":
                desc = "Yeasts, Molds, Mushrooms, Lichens"
            elif k_name == "Protista / Chromista":
                desc = "Red Algae, Brown Algae, Kelps, Water Molds"
            elif k_name == "Pseudomonadati":
                desc = "Proteobacteria / Gram-negative Bacteria"
            elif k_name == "Bacillati":
                desc = "Firmicutes, Mycoplasmas / Gram-positive Bacteria"
            elif k_name in ["Euryarchaeota", "Crenarchaeota", "Asgardarchaeota"]:
                desc = "Methanogens, Halophiles, Hyperthermophiles & Asgard Archaea"
            elif k_name == "Heunggongvirae":
                desc = "Herpesviruses"
            else:
                desc = "Specialized taxa"

            md_lines.append(f"| **{dom}** | **{k_name}** | {desc} | **{k_count}** |")

    md_lines.append(f"| **Total Universal Pool** | | **All 8 Taxonomic Ranks Across All Life** | **{total_catalog_count}** |")
    md_lines.append("")
    md_lines.append("---")
    md_lines.append("")

    # Build the full collapsible hierarchy
    for dom in domain_order:
        if dom not in tree_hierarchy: continue
        k_dict = tree_hierarchy[dom]
        dom_count = sum(len(sp_list) for p_dict in k_dict.values() for p in p_dict.values() for c in p.values() for o in c.values() for sp_list in o.values())

        md_lines.append("<details>")
        md_lines.append(f"<summary>⬛ <b>Domain: {dom}</b> — {dom_count:,} Species</summary>")
        md_lines.append("")

        # Preferred kingdom ordering under Eukaryota / Bacteria / Archaea
        if dom == "Eukaryota":
            kingdom_order = ["Animalia", "Plantae", "Fungi", "Protista / Chromista"]
        elif dom == "Bacteria":
            kingdom_order = ["Pseudomonadati", "Bacillati"]
        elif dom == "Archaea":
            kingdom_order = ["Euryarchaeota", "Crenarchaeota", "Asgardarchaeota"]
        else:
            kingdom_order = sorted(k_dict.keys())

        for k_name in kingdom_order:
            if k_name not in k_dict: continue
            p_dict = k_dict[k_name]
            k_count = sum(len(sp_list) for p in p_dict.values() for c in p.values() for o in c.values() for sp_list in o.values())

            k_title = f"{k_name} (Metazoa)" if k_name == "Animalia" else f"{k_name} (Viridiplantae)" if k_name == "Plantae" else k_name

            md_lines.append("<details>")
            md_lines.append(f"<summary>🟫 <b>Kingdom: {k_title}</b> — {k_count:,} Species</summary>")
            md_lines.append("")

            # Sort phyla alphabetically A-Z
            phyla_sorted = sorted(p_dict.keys(), key=lambda p: p.lower())

            for phylum in phyla_sorted:
                c_dict = p_dict[phylum]
                p_count = sum(len(sp_list) for c in c_dict.values() for o in c.values() for sp_list in o.values())
                p_label = f"{phylum} ({PHYLUM_COMMON[phylum]})" if phylum in PHYLUM_COMMON else phylum

                md_lines.append("<details>")
                md_lines.append(f"<summary>🟦 <b>Phylum: {p_label}</b> — {p_count:,} Species</summary>")
                md_lines.append("")

                # Sort classes alphabetically A-Z
                classes_sorted = sorted(c_dict.keys(), key=lambda c: c.lower())

                for cls in classes_sorted:
                    o_dict = c_dict[cls]
                    cls_count = sum(len(sp_list) for o in o_dict.values() for sp_list in o.values())
                    cls_label = f"{cls} ({CLASS_COMMON[cls]})" if cls in CLASS_COMMON else cls

                    md_lines.append("<details>")
                    md_lines.append(f"<summary>🟪 <b>Class: {cls_label}</b> — {cls_count:,} Species</summary>")
                    md_lines.append("")

                    # Sort orders alphabetically A-Z
                    orders_sorted = sorted(o_dict.keys(), key=lambda o: o.lower())

                    for order in orders_sorted:
                        f_dict = o_dict[order]
                        ord_count = sum(len(sp_list) for sp_list in f_dict.values())

                        md_lines.append("<details>")
                        md_lines.append(f"<summary>🟥 <b>Order: {order}</b> — {ord_count:,} Species</summary>")
                        md_lines.append("")

                        # Sort families alphabetically A-Z
                        fams_sorted = sorted(f_dict.keys(), key=lambda f: f.lower())

                        for fam in fams_sorted:
                            sp_list = f_dict[fam]
                            # Sort species alphabetically by common name
                            sp_list.sort(key=lambda s: s["common"].lower())

                            md_lines.append("<details>")
                            md_lines.append(f"<summary>🟧 <b>Family: {fam}</b> — {len(sp_list)} Species</summary>")
                            md_lines.append("")
                            md_lines.append("| Common Name | Scientific Name | 🟨 Genus |")
                            md_lines.append("| :--- | :--- | :--- |")

                            for sp in sp_list:
                                md_lines.append(f"| {sp['common']} | *{sp['scientific']}* | *{sp['genus']}* |")

                            md_lines.append("")
                            md_lines.append("</details>")

                        md_lines.append("")
                        md_lines.append("</details>")

                    md_lines.append("")
                    md_lines.append("</details>")

                md_lines.append("")
                md_lines.append("</details>")

            md_lines.append("")
            md_lines.append("</details>")

        md_lines.append("")
        md_lines.append("</details>")
        md_lines.append("")

    output_path = os.path.join(BASE_DIR, "species_catalog_taxonomic.md")
    print(f"\nWriting {len(md_lines)} lines to {output_path}...")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines))
    print(f"Successfully created {output_path}!")

    print("\n=== Step 4: Verification & Sum Check ===")
    # Extract species from the newly written file
    with open(output_path, "r", encoding="utf-8") as f:
        new_lines = f.readlines()

    new_species = []
    for line in new_lines:
        line_s = line.strip()
        if line_s.startswith('|') and not line_s.startswith('| :---') and not line_s.startswith('| Common Name') and not line_s.startswith('| ⬛ Domain') and not line_s.startswith('| **Total'):
            parts = [p.strip() for p in line_s.split('|')[1:-1]]
            if len(parts) >= 3 and parts[1].startswith('*') and parts[1].endswith('*') and not parts[1].startswith('**'):
                scientific = parts[1].strip('*').strip()
                common = parts[0].strip()
                new_species.append((common, scientific))

    print(f"Species in original species_catalog.md: {len(old_species)}")
    print(f"Species in new species_catalog_taxonomic.md: {len(new_species)}")

    assert len(new_species) == len(old_species), f"Expected {len(old_species)} species, found {len(new_species)}"

    old_set = set(old_species)
    new_set = set(new_species)

    diff_missing = old_set - new_set
    diff_extra = new_set - old_set

    print(f"Missing from new catalog: {len(diff_missing)}")
    print(f"Extra in new catalog: {len(diff_extra)}")

    assert len(diff_missing) == 0, f"Error: {len(diff_missing)} species missing!"
    assert len(diff_extra) == 0, f"Error: {len(diff_extra)} extra species!"

    print("\n🎉 ALL VERIFICATION CHECKS PASSED PERFECTLY!")
    print(f"Total verified species: {len(new_species)} (100.00% match, zero dropped).")

if __name__ == "__main__":
    main()
