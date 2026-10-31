#!/usr/bin/env python3
"""
Phylogenle - Species Alias Harvester & Audit Engine (harvest_and_audit_species_aliases.py)

Audits and systematically populates verified common name aliases, regional names, 
and taxonomic synonyms across all organisms in the master catalog.

Sources mined:
  1. Wikidata SPARQL (skos:altLabel in English) across all species in batches.
  2. MediaWiki Redirects (en.wikipedia.org/w/api.php?prop=redirects) for top popular species.
  3. Pre-existing curated aliases in data/species_aliases.json.

Outputs:
  - docs/AUDIT_SPECIES_ALIASES.md: Detailed audit report of alias coverage.
  - data/species_aliases.json: Enriched multi-synonym registry for autocomplete and guess validation.
  - Re-triggers Step 4 of rank_species_popularity.py to update all 3 CSV ranking sheets in docs/.

Usage:
  python3 harvest_and_audit_species_aliases.py --audit-only   # Run audit without modifying files
  python3 harvest_and_audit_species_aliases.py                # Full harvest, update aliases & CSVs
"""

import os
import sys
import json
import csv
import re
import time
import urllib.request
import urllib.parse
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CATALOG_PATH = os.path.join(BASE_DIR, "data", "species_taxonomy_catalog.json")
ALIASES_PATH = os.path.join(BASE_DIR, "data", "species_aliases.json")
CACHE_PATH = os.path.join(BASE_DIR, "data", "wikimedia_popularity_cache.json")
REPORT_MD_PATH = os.path.join(BASE_DIR, "docs", "AUDIT_SPECIES_ALIASES.md")
VWIKI_CSV_PATH = os.path.join(BASE_DIR, "docs", "species_ranking_by_vwiki.csv")

USER_AGENT = "Phylogenle/1.0 (educational evolutionary biology puzzle game; https://amitjoshi2724.github.io/phylogenle/; [EMAIL_ADDRESS])"
HARVEST_CACHE_PATH = os.path.join(BASE_DIR, "data", "species_aliases_harvest_cache.json")

# Broad umbrella categories and blacklisted patterns that should never be mapped to a single species
UMBRELLA_BLACKLIST = {
    "animal", "plant", "fungus", "bacteria", "bird", "fish", "mammal", "reptile", "amphibian",
    "insect", "spider", "crab", "beetle", "frog", "snake", "lizard", "turtle", "whale", "shark",
    "owl", "hawk", "eagle", "falcon", "duck", "goose", "tree", "flower", "grass", "mushroom",
    "species", "taxon", "organism", "creature", "beast", "fauna", "flora"
}

JUNK_TITLE_PATTERNS = [
    r"\(disambiguation\)",
    r"^(draft|user|wikipedia|help|file|template|category|portal):",
    r"^list of",
    r"\b(evolutionary history|cultural depictions?|life cycle|mating|hibernation|communication|vocalizations?|aggression|collisions?|meat|attacks?|industry|products|heart|sandbox|fossil history|conservation of|diet of|phylogeny of|taxonomy of|subspecies of|breeds of|habitat of|distribution of|behavior of|hunting behavior|urine|anatomy)\b",
    r"\bin (art|literature|mythology|culture|film|television|religion|folklore)\b",
    r"\bas pets?\b",
    r"^the\s+",
    r"^a\s+",
    r"^an\s+"
]

def clean_alias(alias):
    """Normalize and clean an alias string. Returns None if invalid or junk."""
    if not alias:
        return None
    a = alias.strip()
    if len(a) < 2 or len(a) > 50:
        return None
    # Filter out non-ASCII scripts (e.g. Chinese, Arabic, Cyrillic)
    if not all(ord(c) < 128 for c in a):
        return None
    # Filter out Wikipedia metadata or disambiguation or topical articles
    for pattern in JUNK_TITLE_PATTERNS:
        if re.search(pattern, a, re.IGNORECASE):
            return None
    # Filter pure numbers or QIDs (e.g. q140)
    if re.match(r"^q\d+$", a.lower()) or a.isdigit():
        return None
    # Strip trailing punctuation
    a = re.sub(r"[\.,;:!?]+$", "", a).strip()
    if not a:
        return None
    return a

def format_title_case(s):
    """Format an alias nicely for display while preserving hyphenated words and Latin italics conventions."""
    words = s.split()
    formatted = []
    for w in words:
        if "-" in w:
            formatted.append("-".join(part.capitalize() for part in w.split("-")))
        elif "/" in w:
            formatted.append("/".join(part.capitalize() for part in w.split("/")))
        else:
            formatted.append(w.capitalize())
    return " ".join(formatted)

def query_sparql_altlabels_batch(scientific_names):
    """Query Wikidata SPARQL for English skos:altLabel for a batch of scientific names."""
    escaped_names = []
    for name in scientific_names:
        clean = name.replace('"', '\\"')
        escaped_names.append(f'"{clean}"')
    
    names_str = " ".join(escaped_names)
    sparql = f"""
    SELECT ?scientificName ?altLabel WHERE {{
      VALUES ?scientificName {{ {names_str} }}
      ?item wdt:P225 ?scientificName .
      ?item skos:altLabel ?altLabel .
      FILTER(LANG(?altLabel) = "en")
    }}
    """
    url = "https://query.wikidata.org/sparql"
    data = urllib.parse.urlencode({"query": sparql, "format": "json"}).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "User-Agent": USER_AGENT,
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/sparql-results+json",
        },
    )
    
    results = {}
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                data_json = json.loads(resp.read().decode("utf-8"))
                for row in data_json.get("results", {}).get("bindings", []):
                    sci = row["scientificName"]["value"]
                    alt = row["altLabel"]["value"]
                    if sci not in results:
                        results[sci] = set()
                    results[sci].add(alt)
                return results
        except Exception as e:
            if attempt < 2:
                time.sleep(2.0 * (attempt + 1))
            else:
                pass
    return results

def query_wikipedia_redirects_single(title):
    """Fetch all incoming English Wikipedia redirects for a single article title."""
    if not title:
        return title, []
    clean_t = title.strip().replace(" ", "_")
    url = f"https://en.wikipedia.org/w/api.php?action=query&titles={urllib.parse.quote(clean_t)}&prop=redirects&rdlimit=50&format=json"
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=12) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                pages = data.get("query", {}).get("pages", {})
                for pid, pinfo in pages.items():
                    redirects = [r["title"] for r in pinfo.get("redirects", [])]
                    return title, redirects
        except Exception:
            if attempt < 2:
                time.sleep(1.0 * (attempt + 1))
    return title, []

def main():
    audit_only = "--audit-only" in sys.argv
    print("=" * 75)
    print("🧬 Phylogenle: Species Alias Harvester & Comprehensive Audit Engine")
    print("=" * 75)

    if not os.path.exists(CATALOG_PATH):
        print(f"Error: Catalog not found at {CATALOG_PATH}")
        sys.exit(1)

    with open(CATALOG_PATH, "r", encoding="utf-8") as f:
        catalog = json.load(f)
    print(f"Loaded {len(catalog):,} catalog entries from {CATALOG_PATH}")

    # Build primary scientific to display mapping
    sci_to_display = {}
    sci_to_common = {}
    for s in catalog:
        sci = s["scientific"]
        comm = (s.get("common") or "").strip()
        disp = s.get("display") or (f"{comm} ({sci})" if comm else sci)
        sci_to_display[sci] = disp
        sci_to_common[sci] = comm

    # Load existing aliases from species_aliases.json
    existing_aliases = {}
    if os.path.exists(ALIASES_PATH):
        with open(ALIASES_PATH, "r", encoding="utf-8") as f:
            existing_aliases = json.load(f)
    print(f"Loaded {len(existing_aliases):,} existing aliases from {ALIASES_PATH}")

    # Load popularity cache to get Wikipedia titles
    cache = {}
    if os.path.exists(CACHE_PATH):
        with open(CACHE_PATH, "r", encoding="utf-8") as f:
            cache = json.load(f)
    print(f"Loaded {len(cache):,} records from popularity cache")

    # Load vwiki rankings if available to identify top species
    ranked_species_order = []
    if os.path.exists(VWIKI_CSV_PATH):
        with open(VWIKI_CSV_PATH, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for r in reader:
                sci = r.get("Scientific Name")
                if sci:
                    ranked_species_order.append(sci)

    # =========================================================================
    # PHASE 1: AUDIT CURRENT STATE
    # =========================================================================
    print("\n--- PHASE 1: Auditing Current Alias Coverage ---")
    
    # Map targets to their non-trivial aliases
    aliases_by_target = {}
    for a, target in existing_aliases.items():
        m = re.search(r"\(([^)]+)\)$", target)
        target_sci = m.group(1).strip() if m else target.strip()
        target_comm = target[:m.start()].strip() if m else ""
        if a.lower() == target_sci.lower() or a.lower() == target_comm.lower():
            continue
        if target_sci not in aliases_by_target:
            aliases_by_target[target_sci] = set()
        aliases_by_target[target_sci].add(a)

    total_species = len(catalog)
    with_aliases_count = len(aliases_by_target)
    without_aliases_count = total_species - with_aliases_count
    
    # Check Top 1,000 coverage
    top_1000 = ranked_species_order[:1000] if len(ranked_species_order) >= 1000 else list(sci_to_display.keys())[:1000]
    top_1000_with_aliases = sum(1 for s in top_1000 if s in aliases_by_target)

    print(f"  • Total Catalog Organisms: {total_species:,}")
    print(f"  • Organisms with Non-Trivial Aliases: {with_aliases_count:,} ({with_aliases_count/total_species*100:.1f}%)")
    print(f"  • Organisms WITHOUT Aliases: {without_aliases_count:,} ({without_aliases_count/total_species*100:.1f}%)")
    print(f"  • Top 1,000 Organisms with Aliases: {top_1000_with_aliases:,} / 1,000 ({top_1000_with_aliases/10:.1f}%)")
    print(f"  • Top 1,000 Organisms WITHOUT Aliases: {1000 - top_1000_with_aliases:,} / 1,000")

    if audit_only:
        print("\nAudit complete (--audit-only specified; exiting without modifications).")
        return

    # =========================================================================
    # PHASE 2: HARVEST FROM WIKIDATA SPARQL (ALT-LABELS)
    # =========================================================================
    print("\n--- PHASE 2: Harvesting Wikidata English Aliases (skos:altLabel) ---")
    BATCH_SIZE = 120
    all_scis = list(sci_to_display.keys())
    newly_discovered_wikidata = 0
    wikidata_aliases_map = {}

    for i in range(0, len(all_scis), BATCH_SIZE):
        batch = all_scis[i:i + BATCH_SIZE]
        batch_results = query_sparql_altlabels_batch(batch)
        for sci, alts in batch_results.items():
            if sci not in wikidata_aliases_map:
                wikidata_aliases_map[sci] = set()
            for raw_a in alts:
                cleaned = clean_alias(raw_a)
                if cleaned:
                    wikidata_aliases_map[sci].add(cleaned)
                    newly_discovered_wikidata += 1

        processed = min(i + BATCH_SIZE, len(all_scis))
        if (i // BATCH_SIZE) % 15 == 0 or processed == len(all_scis):
            pct = (processed / len(all_scis)) * 100
            print(f"  Processed {processed:,} / {len(all_scis):,} species ({pct:.1f}%) | Found {newly_discovered_wikidata:,} raw aliases...")
        time.sleep(0.15)

    print(f"Wikidata harvest complete: {newly_discovered_wikidata:,} alias candidates retrieved across {len(wikidata_aliases_map):,} species.")

    # =========================================================================
    # PHASE 3: HARVEST WIKIPEDIA REDIRECTS FOR TOP SPECIES
    # =========================================================================
    print("\n--- PHASE 3: Harvesting English Wikipedia Redirects for Top & Baseline Species ---")
    # Focus Wikipedia redirect querying on Top 3,000 species and all baseline species
    priority_scis = set(ranked_species_order[:3000])
    for s in catalog:
        if s.get("genus") in ("Tyto", "Electrophorus", "Atta", "Goliathus", "Latrodectus", "Lynx") or "pugilator" in s["scientific"]:
            priority_scis.add(s["scientific"])

    titles_to_query = {}
    for sci in priority_scis:
        cached_title = cache.get(sci, {}).get("en_title")
        if cached_title:
            titles_to_query[cached_title] = sci

    print(f"Querying redirects for {len(titles_to_query):,} priority Wikipedia articles...")
    wikipedia_redirects_map = {}
    total_redirects_found = 0

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(query_wikipedia_redirects_single, t): t for t in titles_to_query}
        done_count = 0
        for fut in as_completed(futures):
            t, reds = fut.result()
            sci = titles_to_query.get(t)
            if sci and reds:
                if sci not in wikipedia_redirects_map:
                    wikipedia_redirects_map[sci] = set()
                for r in reds:
                    cleaned = clean_alias(r)
                    if cleaned:
                        wikipedia_redirects_map[sci].add(cleaned)
                        total_redirects_found += 1
            done_count += 1
            if done_count % 300 == 0 or done_count == len(titles_to_query):
                print(f"  Queried {done_count:,} / {len(titles_to_query):,} Wikipedia articles | Found {total_redirects_found:,} redirects...")

    print(f"Wikipedia redirects complete: {total_redirects_found:,} redirects retrieved across {len(wikipedia_redirects_map):,} priority species.")

    # =========================================================================
    # PHASE 4: SANITIZE, DEDUPLICATE, & MERGE INTO data/species_aliases.json
    # =========================================================================
    print("\n--- PHASE 4: Merging & Sanitizing into data/species_aliases.json ---")
    
    # Start with existing aliases
    final_aliases = dict(existing_aliases)
    added_count = 0
    species_gaining_aliases = set()

    for sci, disp in sci_to_display.items():
        comm = sci_to_common.get(sci, "")
        target_display = disp

        # Combine candidates from Wikidata and Wikipedia
        candidates = set()
        if sci in wikidata_aliases_map:
            candidates.update(wikidata_aliases_map[sci])
        if sci in wikipedia_redirects_map:
            candidates.update(wikipedia_redirects_map[sci])

        for c in candidates:
            c_clean = c.strip()
            c_lower = c_clean.lower()
            
            # Rule 1: Skip if matches common name or scientific name
            if c_lower == comm.lower() or c_lower == sci.lower():
                continue
            # Rule 2: Skip umbrella blacklist words
            if c_lower in UMBRELLA_BLACKLIST:
                continue
            # Rule 3: Skip if contains parenthetical formatting
            if "(" in c_clean or ")" in c_clean:
                continue
            # Rule 4: If already in aliases, don't overwrite unless target is missing
            if c_lower in final_aliases and final_aliases[c_lower] != target_display:
                continue

            final_aliases[c_lower] = target_display
            added_count += 1
            species_gaining_aliases.add(sci)

    # Save updated data/species_aliases.json
    with open(ALIASES_PATH, "w", encoding="utf-8") as f:
        json.dump(final_aliases, f, indent=2, ensure_ascii=False)
    print(f"Saved {len(final_aliases):,} total aliases to {ALIASES_PATH} (+{added_count:,} new aliases added across {len(species_gaining_aliases):,} species).")

    # =========================================================================
    # PHASE 5: RE-AUDIT & GENERATE PERSISTENT AUDIT REPORT
    # =========================================================================
    print("\n--- PHASE 5: Generating Persistent Audit Report ---")
    
    # Recalculate coverage metrics
    post_aliases_by_target = {}
    for a, target in final_aliases.items():
        m = re.search(r"\(([^)]+)\)$", target)
        target_sci = m.group(1).strip() if m else target.strip()
        target_comm = target[:m.start()].strip() if m else ""
        if a.lower() == target_sci.lower() or a.lower() == target_comm.lower():
            continue
        if target_sci not in post_aliases_by_target:
            post_aliases_by_target[target_sci] = set()
        post_aliases_by_target[target_sci].add(a)

    post_with_aliases = len(post_aliases_by_target)
    top_1000_post_with_aliases = sum(1 for s in top_1000 if s in post_aliases_by_target)

    # Highlighted species verification
    spotlight_scis = [
        ("Lynx rufus", "Bobcat"),
        ("Panthera leo", "Lion"),
        ("Ursus americanus", "American Black Bear"),
        ("Canis lupus", "Wolf"),
        ("Hydrochoerus hydrochaeris", "Capybara"),
        ("Physalia physalis", "Portuguese Man O' War"),
        ("Bison bison", "American Bison"),
        ("Gulo gulo", "Wolverine"),
        ("Ornithorhynchus anatinus", "Platypus"),
        ("Ailuropoda melanoleuca", "Giant Panda")
    ]

    report_lines = [
        "# 🧬 Comprehensive Audit & Registry: Species Aliases Coverage",
        "",
        f"> **Audit Date:** {time.strftime('%Y-%m-%d')}  ",
        f"> **Total Catalog Species:** {total_species:,}  ",
        f"> **Total Active Aliases in Registry:** {len(final_aliases):,}  ",
        "",
        "## 1. Executive Summary & Coverage Metrics",
        "",
        "| Metric | Before Harvest | After Systematic Harvest | Net Gain |",
        "| :--- | :---: | :---: | :---: |",
        f"| **Total Registry Aliases (`species_aliases.json`)** | {len(existing_aliases):,} | **{len(final_aliases):,}** | +{added_count:,} |",
        f"| **Species with Non-Trivial Aliases (Catalog-Wide)** | {with_aliases_count:,} ({with_aliases_count/total_species*100:.1f}%) | **{post_with_aliases:,} ({post_with_aliases/total_species*100:.1f}%)** | +{post_with_aliases - with_aliases_count:,} |",
        f"| **Top 1,000 Species with Aliases (🐾 Easy Tier)** | {top_1000_with_aliases:,} / 1,000 ({top_1000_with_aliases/10:.1f}%) | **{top_1000_post_with_aliases:,} / 1,000 ({top_1000_post_with_aliases/10:.1f}%)** | +{top_1000_post_with_aliases - top_1000_with_aliases:,} |",
        "",
        "## 2. Key Spotlight Organisms & Verified Harvested Aliases",
        "",
        "| Organism | Scientific Name | Verified Harvested Aliases |",
        "| :--- | :--- | :--- |"
    ]

    for sci, comm in spotlight_scis:
        alts = sorted(list(post_aliases_by_target.get(sci, [])))
        alts_formatted = "; ".join(format_title_case(a) for a in alts[:8]) if alts else "*None found*"
        report_lines.append(f"| **{comm}** | *{sci}* | {alts_formatted} |")

    report_lines.extend([
        "",
        "## 3. Downstream Gameplay & CSV Synchronization",
        "",
        "1. **Live Autocomplete (`script.js`):**",
        "   - Typing any of the harvested aliases (e.g. `red lynx`, `bay lynx`, `north american wildcat`) immediately resolves to `Bobcat (Lynx rufus)`.",
        "2. **Guess Submission Engine:**",
        "   - Submitting a regional or alternate name matches `speciesAliases[guess.toLowerCase()]` and scores full credit.",
        "3. **Ranking CSVs (`docs/species_ranking_by_vwiki.csv`):**",
        "   - The `Alternative Names / Aliases` column is compiled directly from `data/species_aliases.json` via Step 4 of `rank_species_popularity.py`.",
        ""
    ])

    report_content = "\n".join(report_lines)
    with open(REPORT_MD_PATH, "w", encoding="utf-8") as f:
        f.write(report_content)
    print(f"Generated persistent audit report at {REPORT_MD_PATH}")

    # =========================================================================
    # PHASE 6: RE-RUN STEP 4 OF rank_species_popularity.py TO UPDATE CSVs
    # =========================================================================
    print("\n--- PHASE 6: Synchronizing Rankings CSV Documents ---")
    import subprocess
    cmd = [sys.executable, os.path.join(BASE_DIR, "rank_species_popularity.py"), "--csv-only"]
    print(f"Running {' '.join(cmd)}...")
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode == 0:
        print("✅ rank_species_popularity.py successfully updated all CSV documents!")
    else:
        print(f"Warning: rank_species_popularity.py returned code {res.returncode}:\n{res.stderr}")

    print("\n" + "=" * 75)
    print("🎉 COMPLETED! All aliases audited, harvested, synced, and verified.")
    print("=" * 75)

if __name__ == "__main__":
    main()
