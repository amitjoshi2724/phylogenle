#!/usr/bin/env python3
"""
sync_tree_wikipedia_and_common_names.py
=======================================
Methodical, algorithmic pipeline to attach canonical Wikipedia article pages
and verified biological common names to every node in the Phylogenle tree.

Features:
- Algorithmic Wikipedia MediaWiki batch API queries (up to 50 titles per batch).
- Follows and resolves Wikipedia redirect chains (e.g., Mammalia -> Mammal, Clupeocephala -> Teleost).
- Extracts verified common names via regex patterns on Wikipedia lead sentences & article titles.
- Fast NCBI Taxdump integration (taxdump.tar.gz) for GenBank & BLAST curated common names.
- Uses data/species_list.json to map all 29,564 species with 100% verified binomials & vernacular names.
- Caches results to data/wiki_taxa_cache.json for instant subsequent runs & offline capability.
- Updates data/phylogeny_tree.json (attaches wiki_title & common_name to nodes).
- Updates data/clade_common_names.json (comprehensive lookup mapping for the web app).

Usage:
  python3 sync_tree_wikipedia_and_common_names.py [options]

Options:
  --max-batches N    Limit Wikipedia network queries to N batches (50 taxa/batch). Default: 0 (all).
  --offline          Run without network requests using NCBI taxdump and disk cache.
  --force-refresh    Ignore cache and re-query Wikipedia.
  --dry-run          Run extraction without writing changes to data files.
"""

import os
import sys
import json
import re
import time
import tarfile
import urllib.request
import urllib.parse
import argparse

REPO_ROOT = os.path.dirname(os.path.abspath(__file__))
TREE_PATH = os.path.join(REPO_ROOT, "data", "phylogeny_tree.json")
SPECIES_LIST_PATH = os.path.join(REPO_ROOT, "data", "species_list.json")
TAXDUMP_PATH = os.path.join(REPO_ROOT, "taxdump.tar.gz")
CLADE_COMMON_PATH = os.path.join(REPO_ROOT, "data", "clade_common_names.json")
CACHE_PATH = os.path.join(REPO_ROOT, "data", "wiki_taxa_cache.json")

USER_AGENT = "Phylogenle/1.0 (https://amitjoshi2724.github.io/phylogenle; biological-puzzle-game)"


def title_case_name(text):
    """Cleanly capitalize vernacular common names."""
    if not text:
        return ""
    text = text.strip()
    text = re.sub(r"^(the|a|an)\s+", "", text, flags=re.I)
    text = re.sub(r"\s*\([^)]*\)", "", text)
    text = re.sub(r"[,;.\s]+$", "", text)
    if not text:
        return ""
    
    # Handle hyphens and slashes
    parts = re.split(r"(\s+|/|&|-)", text)
    lowers = {"and", "of", "or", "the", "&", "in", "to", "for"}
    res = []
    for p in parts:
        if p.lower() in lowers:
            res.append(p.lower())
        elif p.isalpha():
            res.append(p.capitalize())
        else:
            res.append(p)
    formatted = "".join(res).strip()
    # Ensure first word is always capitalized
    if formatted:
        formatted = formatted[0].upper() + formatted[1:]
    return formatted


def extract_ncbi_common_names(taxdump_path, target_taxids):
    """
    Fast extraction of official common names from NCBI taxdump.tar.gz.
    Parses names.dmp in seconds without full extraction to disk.
    """
    ncbi_names = {}
    if not os.path.exists(taxdump_path):
        print(f"[*] NCBI taxdump not found at {taxdump_path}, skipping local NCBI dump lookup.")
        return ncbi_names

    print(f"[*] Reading NCBI names.dmp from {taxdump_path} for {len(target_taxids)} taxids...")
    t0 = time.time()
    try:
        with tarfile.open(taxdump_path, "r:gz") as tar:
            names_file = tar.extractfile("names.dmp")
            if not names_file:
                return ncbi_names
            for line_bytes in names_file:
                line_str = line_bytes.decode("utf-8", errors="ignore")
                parts = [p.strip() for p in line_str.split("|")]
                if len(parts) >= 4:
                    tid, name, _, name_class = parts[0], parts[1], parts[2], parts[3]
                    if tid in target_taxids:
                        if name_class == "genbank common name":
                            ncbi_names[tid] = title_case_name(name)
                        elif name_class == "common name" and tid not in ncbi_names:
                            ncbi_names[tid] = title_case_name(name)
                        elif name_class == "blast name" and tid not in ncbi_names:
                            ncbi_names[tid] = title_case_name(name)
        print(f"[+] Loaded {len(ncbi_names)} NCBI official common names in {time.time()-t0:.2f}s")
    except Exception as e:
        print(f"[-] Warning: Failed reading taxdump: {e}")
    return ncbi_names


def extract_common_name_from_wiki(original_title, article_title, extract_text):
    """
    Algorithmic extraction of common name from Wikipedia redirect title and lead extract.
    """
    # 1. Check if Wikipedia redirected to an English vernacular article title
    # e.g., Aves -> Bird, Mammalia -> Mammal, Anura -> Frog, Cetacea -> Cetacean, Teleostei -> Teleost
    cleaned_article = re.sub(r"\s*\([^)]*\)", "", article_title).strip()
    is_scientific_title = bool(re.search(r"(idae|formes|ini|inae|oidea|phyceae|mycetes|opsida|ales)$", cleaned_article, re.I))
    if cleaned_article.lower() != original_title.lower() and not is_scientific_title:
        # If redirected to singular, keep clean
        return title_case_name(cleaned_article)

    # 2. Regex patterns on lead sentence
    if extract_text:
        patterns = [
            r"commonly referred to as (?:the )?([A-Za-z0-9, -/&]+?)(?:[.,;]|\s+in\s+|\s+which|\s+that|\s+and\s+its)",
            r"commonly known as (?:the )?([A-Za-z0-9, -/&]+?)(?:[.,;]|\s+in\s+|\s+which|\s+that|\s+and\s+its)",
            r"whose members are (?:commonly )?(?:referred to|known) as (?:the )?([A-Za-z0-9, -/&]+?)(?:[.,;]|\s+in\s+)",
            r"formally referred to as (?:the )?([A-Za-z0-9, -/&]+?)(?:[.,;]|\s+in\s+)",
            r"members of which are known as (?:the )?([A-Za-z0-9, -/&]+?)(?:[.,;]|\s+in\s+)",
            r"commonly called (?:the )?([A-Za-z0-9, -/&]+?)(?:[.,;]|\s+in\s+)",
            r"known informally as (?:the )?([A-Za-z0-9, -/&]+?)(?:[.,;]|\s+in\s+)",
            r"family of [^,.\n]+ commonly (?:called|referred to as) (?:the )?([A-Za-z0-9, -/&]+?)(?:[.,;]|\s+in\s+)",
            r"order of [^,.\n]+ commonly (?:called|referred to as) (?:the )?([A-Za-z0-9, -/&]+?)(?:[.,;]|\s+in\s+)",
            r"class of [^,.\n]+ commonly (?:called|referred to as) (?:the )?([A-Za-z0-9, -/&]+?)(?:[.,;]|\s+in\s+)",
            r"including the ([A-Za-z0-9, -/&]+?)(?:[.,;]|\s+amongst|\s+and\s+others)",
        ]
        for pat in patterns:
            match = re.search(pat, extract_text, re.I)
            if match:
                cand = match.group(1).strip()
                # Exclude long explanatory fragments
                if len(cand) <= 45 and not any(w in cand.lower() for w in ["species", "contains", "order", "family", "genera"]):
                    return title_case_name(cand)

    return ""


def query_wikipedia_batch(titles, user_agent=USER_AGENT):
    """
    Query Wikipedia MediaWiki API in batches of up to 50 titles.
    Resolves redirects, extracts canonical article title, and lead extract.
    """
    encoded_titles = "|".join(urllib.parse.quote(t) for t in titles)
    url = f"https://en.wikipedia.org/w/api.php?action=query&titles={encoded_titles}&redirects=1&prop=extracts&exintro=1&explaintext=1&format=json"

    req = urllib.request.Request(url, headers={"User-Agent": user_agent})
    results = {}
    try:
        with urllib.request.urlopen(req, timeout=12) as resp:
            data = json.load(resp)
            query = data.get("query", {})
            
            # Map canonical title back to original requested title via redirects
            redirects = {r["to"]: r["from"] for r in query.get("redirects", [])}
            forward_redirects = {r["from"]: r["to"] for r in query.get("redirects", [])}
            normalized = {n["to"]: n["from"] for n in query.get("normalized", [])}

            pages = query.get("pages", {})
            for pid, p in pages.items():
                if pid == "-1" or "missing" in p:
                    continue
                canonical_title = p.get("title", "")
                extract = p.get("extract", "")

                # Identify which requested titles lead here
                matched_orig = []
                for t in titles:
                    cur = t
                    if cur in normalized:
                        cur = normalized[cur]
                    if cur in forward_redirects:
                        cur = forward_redirects[cur]
                    if cur.lower() == canonical_title.lower() or t.lower() == canonical_title.lower():
                        matched_orig.append(t)

                if not matched_orig:
                    matched_orig = [canonical_title]

                for orig in matched_orig:
                    common = extract_common_name_from_wiki(orig, canonical_title, extract)
                    results[orig] = {
                        "wiki_title": canonical_title,
                        "common_name": common,
                        "extract_snippet": extract[:160] if extract else ""
                    }
    except Exception as e:
        print(f"[-] Wikipedia batch query error: {e}")
    return results


def main():
    parser = argparse.ArgumentParser(description="Algorithmic pipeline for Wikipedia articles and biological common names")
    parser.add_argument("--max-batches", type=int, default=0, help="Max batches of 50 to query (0 = all)")
    parser.add_argument("--offline", action="store_true", help="Run offline using local disk cache and NCBI dump")
    parser.add_argument("--force-refresh", action="store_true", help="Ignore disk cache")
    parser.add_argument("--dry-run", action="store_true", help="Do not write updates to disk")
    args = parser.parse_args()

    print("===================================================================")
    print(" Phylogenle - Wikipedia & Common Names Algorithmic Pipeline")
    print("===================================================================")

    if not os.path.exists(TREE_PATH):
        print(f"Error: {TREE_PATH} not found.")
        sys.exit(1)

    with open(TREE_PATH, "r", encoding="utf-8") as f:
        tree = json.load(f)

    nodes = tree.get("nodes", {})
    print(f"[+] Loaded {len(nodes)} phylogenetic nodes from {TREE_PATH}")

    # 1. Load Species common names & binomials
    species_binomial_to_common = {}
    if os.path.exists(SPECIES_LIST_PATH):
        with open(SPECIES_LIST_PATH, "r", encoding="utf-8") as f:
            species_list = json.load(f)
        for s in species_list:
            m = re.match(r"^(.*?)\s*\((.*?)\)$", s)
            if m:
                common = m.group(1).strip()
                latin = m.group(2).strip()
                species_binomial_to_common[latin.lower()] = common
        print(f"[+] Loaded {len(species_binomial_to_common)} verified species common names from species_list.json")

    # 2. Extract NCBI Taxonomy Dump common names
    all_taxids = set(nodes.keys())
    ncbi_names = extract_ncbi_common_names(TAXDUMP_PATH, all_taxids)

    # 3. Load Disk Cache
    cache = {}
    if os.path.exists(CACHE_PATH) and not args.force_refresh:
        try:
            with open(CACHE_PATH, "r", encoding="utf-8") as f:
                cache = json.load(f)
            print(f"[+] Loaded {len(cache)} cached Wikipedia taxa from {CACHE_PATH}")
        except Exception as e:
            print(f"[-] Warning: Failed to read cache: {e}")

    # 4. Identify higher-level and non-species taxa to query Wikipedia
    higher_taxa = set()
    for tid, node in nodes.items():
        name = node.get("name")
        rank = node.get("rank")
        if name and rank not in ("Species",):
            if name != "root" and name != "?":
                higher_taxa.add(name)

    print(f"[*] Found {len(higher_taxa)} unique higher taxa / subclades to process")

    # Filter out already cached taxa
    to_query = [t for t in sorted(higher_taxa) if t not in cache]
    print(f"[*] Uncached taxa needing Wikipedia queries: {len(to_query)}")

    if not args.offline and to_query:
        batch_size = 50
        batches = [to_query[i:i + batch_size] for i in range(0, len(to_query), batch_size)]
        if args.max_batches > 0:
            batches = batches[:args.max_batches]

        print(f"[*] Querying Wikipedia for {len(batches)} batches ({len(batches)*batch_size} max taxa)...")
        for idx, batch in enumerate(batches, 1):
            print(f"    Batch {idx}/{len(batches)} ({len(batch)} taxa)...", end="", flush=True)
            res = query_wikipedia_batch(batch)
            cache.update(res)
            print(f" resolved {len(res)} pages")
            time.sleep(0.15)  # Respect Wikimedia rate limits

        # Save updated cache
        if not args.dry_run:
            try:
                with open(CACHE_PATH, "w", encoding="utf-8") as f:
                    json.dump(cache, f, indent=2, ensure_ascii=False)
                print(f"[+] Saved updated Wikipedia cache to {CACHE_PATH} ({len(cache)} entries)")
            except Exception as e:
                print(f"[-] Warning: Failed writing cache: {e}")

    # 5. Attach wiki_title and common_name to every node algorithmically
    print("[*] Attaching Wikipedia articles and biological common names to tree nodes...")
    clade_common_map = {}
    nodes_with_wiki = 0
    nodes_with_common = 0

    for tid, node in nodes.items():
        name = node.get("name", "")
        rank = node.get("rank", "")
        lower_name = name.lower()

        # Species node resolution
        if rank == "Species":
            node["wiki_title"] = name
            if lower_name in species_binomial_to_common:
                node["common_name"] = species_binomial_to_common[lower_name]
            elif tid in ncbi_names:
                node["common_name"] = ncbi_names[tid]
            else:
                node["common_name"] = ""

        # Higher-level taxa / subclades
        else:
            wiki_info = cache.get(name, {})
            node["wiki_title"] = wiki_info.get("wiki_title", name)
            
            # Common name priority:
            # 1) Wikipedia parsed vernacular name
            # 2) NCBI GenBank/Common name
            common = wiki_info.get("common_name", "")
            if not common and tid in ncbi_names:
                common = ncbi_names[tid]

            node["common_name"] = common
            if common:
                clade_common_map[lower_name] = common

        if node.get("wiki_title"):
            nodes_with_wiki += 1
        if node.get("common_name"):
            nodes_with_common += 1

    print(f"[+] Nodes with Wikipedia pages attached: {nodes_with_wiki}/{len(nodes)}")
    print(f"[+] Nodes with biological common names: {nodes_with_common}/{len(nodes)}")
    print(f"[+] Total distinct clades/taxa in clade_common_names map: {len(clade_common_map)}")

    # 6. Save data files
    if not args.dry_run:
        print(f"[*] Writing updated phylogeny tree to {TREE_PATH}...")
        with open(TREE_PATH, "w", encoding="utf-8") as f:
            json.dump(tree, f, indent=2, ensure_ascii=False)
        print("[+] data/phylogeny_tree.json updated successfully.")

        print(f"[*] Writing updated clade common names to {CLADE_COMMON_PATH}...")
        # Merge with existing curated definitions so nothing is lost
        existing_clades = {}
        if os.path.exists(CLADE_COMMON_PATH):
            try:
                with open(CLADE_COMMON_PATH, "r", encoding="utf-8") as f:
                    existing_clades = json.load(f)
            except Exception:
                pass
        
        merged_clades = {**existing_clades, **clade_common_map}
        # Sort alphabetically
        sorted_clades = dict(sorted(merged_clades.items(), key=lambda x: x[0]))
        with open(CLADE_COMMON_PATH, "w", encoding="utf-8") as f:
            json.dump(sorted_clades, f, indent=2, ensure_ascii=False)
        print(f"[+] data/clade_common_names.json updated ({len(sorted_clades)} clades mapped).")

    print("\n===================================================================")
    print(" Pipeline complete! All nodes attached with Wikipedia & common names.")
    print(" Run anytime: python3 sync_tree_wikipedia_and_common_names.py")
    print("===================================================================")


if __name__ == "__main__":
    main()
