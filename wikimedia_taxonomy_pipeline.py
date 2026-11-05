#!/usr/bin/env python3
"""
Phylogenle - Wikimedia Taxonomy Pipeline
========================================
(formerly rank_species_popularity.py — Steps 1-4 are carried over unchanged)

One script that connects everything in Phylogenle to Wikimedia:

  POPULARITY STAGES (catalog species)                     cache: data/wikimedia_popularity_cache.json
    Step 1   Wikidata sitelinks (Swiki) + enwiki title via P225 SPARQL
    Step 2   enwiki canonical-title / redirect fallback with biological QID verification
    Step 2B  Option B: exclusive standalone articles (cultivars, subspecies, domestic forms)
    Step 3   enwiki cumulative pageviews (Vwiki)
    Step 4   Deduplicate by scientific name, write the 3 ranking CSVs in docs/

  TREE STAGES (every non-species node in data/phylogeny_tree.json)   cache: data/tree_wiki_cache.json
    Step 5   Link each node (genus, family, order, ... and unranked subclades) to its
             Wikipedia article. Resolution order, most exact first:
               5A  Wikidata item whose NCBI taxonomy ID (P685) == node taxid   (exact ID join)
               5B  Wikidata item whose scientific name (P225) == node name, and whose P685
                   (if present) does not point at a different NCBI taxon    (homonym-safe)
               5C  enwiki title lookup + redirect chain (query_enwiki_fallback_batch),
                   accepted only if the target is a biological item and either describes
                   this exact taxon or a verified ancestor/descendant in our NCBI lineages
    Step 6   Resolve an English common name for each node from sourced data only
             (no hand-written names, no free-text guessing). Priority:
               1. Wikidata P1843 "taxon common name" (English) on the exact item
               2. enwiki article title when it is a vernacular name of the exact taxon
                  (e.g. Aves -> "Bird", Anura -> "Frog")
               3. NCBI taxdump names.dmp: genbank common name > common name > blast name
    Step 7   Export: attach wiki_title / common_name to data/phylogeny_tree.json nodes
             (species nodes get wiki_title from the Step 2 canonical titles) and regenerate
             data/clade_common_names.json used by the game UI.

STATE / RE-RUN SEMANTICS
  Every stage skips work that is already done, based on what is in the caches:
    - Steps 1-3: same rules as before (missing qid / canonical_verified / vwiki_period).
    - Step 5: a node is re-resolved only if it has no record, its record was made for a
      different node name (tree rebuilt), the resolver version changed, or the record is
      marked "error" (network failure). Transient failures are NEVER cached as "no article"
      — this is the same anti-poisoning rule Step 3 uses (None instead of 0 views).
      Nodes confirmed to have no article are only re-checked with --recheck-missing.
    - Steps 6-7 are pure offline computation from the caches and always run when the tree
      stages run (they take a few seconds).

USAGE
  python3 wikimedia_taxonomy_pipeline.py                     # run everything, skipping completed work
  python3 wikimedia_taxonomy_pipeline.py --csv-only          # Step 4 only (used by harvest_and_audit_species_aliases.py)
  python3 wikimedia_taxonomy_pipeline.py --tree-only         # Steps 5-7 only
  python3 wikimedia_taxonomy_pipeline.py --skip-tree         # Steps 1-4 only (old behaviour)
  python3 wikimedia_taxonomy_pipeline.py --tree-only --offline   # rebuild exports from caches, no network
  python3 wikimedia_taxonomy_pipeline.py --tree-only --recheck-missing
  python3 wikimedia_taxonomy_pipeline.py --tree-only --refresh-tree   # discard tree cache, re-resolve all
  python3 wikimedia_taxonomy_pipeline.py --rediscover-subspecies      # force Step 2B
  Add --dry-run to skip writing phylogeny_tree.json / clade_common_names.json.
"""

import os
import sys
import json
import time
import csv
import re
import tarfile
import argparse
import urllib.request
import urllib.parse
import urllib.error
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CATALOG_PATH = os.path.join(BASE_DIR, "data", "species_taxonomy_catalog.json")
CACHE_PATH = os.path.join(BASE_DIR, "data", "wikimedia_popularity_cache.json")
ALIASES_PATH = os.path.join(BASE_DIR, "data", "species_aliases.json")
OVERRIDES_PATH = os.path.join(BASE_DIR, "data", "species_common_name_overrides.json")
DOCS_DIR = os.path.join(BASE_DIR, "docs")
CSV_PATH = os.path.join(DOCS_DIR, "species_popularity_rankings.csv")
SWIKI_CSV_PATH = os.path.join(DOCS_DIR, "species_ranking_by_swiki.csv")
VWIKI_CSV_PATH = os.path.join(DOCS_DIR, "species_ranking_by_vwiki.csv")

# Tree-stage paths
TREE_PATH = os.path.join(BASE_DIR, "data", "phylogeny_tree.json")
TREE_CACHE_PATH = os.path.join(BASE_DIR, "data", "tree_wiki_cache.json")
CLADE_COMMON_PATH = os.path.join(BASE_DIR, "data", "clade_common_names.json")
TAXDUMP_PATH = os.path.join(BASE_DIR, "taxdump.tar.gz")

USER_AGENT = "Phylogenle/1.0 (educational evolutionary biology puzzle game; https://amitjoshi2724.github.io/phylogenle/; [EMAIL_ADDRESS])"

# ==============================================================================
# CONFIGURATION & PARAMETERS (Easily adjustable for custom reruns)
# ==============================================================================
START_DATE = "20250101"   # Format YYYYMMDD: Start date for Wikipedia traffic
END_DATE   = "20261231"   # Format YYYYMMDD: End date for Wikipedia traffic (aggregates all months up to latest available)
DATE_LABEL = "2025–2026"  # Human-readable label for logs, CSV headers, & reports
CACHE_PERIOD_KEY = f"vwiki_{START_DATE}_{END_DATE}"  # Unique cache invalidation key

MAX_WORKERS = 10          # Conservative worker pool to prevent 429 rate-limiting from Wikimedia REST API
SAVE_INTERVAL = 200       # How often to persist cache to disk during queries

# Bump this whenever the Step 5 resolution rules change: every tree node gets re-resolved
# on the next run (records with an older version are treated as stale).
TREE_RESOLVER_VERSION = 1
TREE_SPARQL_BATCH = 150   # NCBI taxids / names per SPARQL VALUES block
# ==============================================================================

def load_cache():
    if os.path.exists(CACHE_PATH):
        try:
            with open(CACHE_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Warning: could not load cache: {e}")
    return {}

def save_cache(cache):
    with open(CACHE_PATH, "w", encoding="utf-8") as f:
        json.dump(cache, f, indent=2, ensure_ascii=False)

def query_wikidata_batch(scientific_names):
    """Query Wikidata SPARQL via POST for a batch of scientific names (P225)."""
    escaped_names = []
    for name in scientific_names:
        clean = name.replace('"', '\\"')
        escaped_names.append(f'"{clean}"')
    
    names_str = " ".join(escaped_names)
    sparql = f"""
    SELECT ?scientificName ?item ?sitelinks ?enTitle WHERE {{
      VALUES ?scientificName {{ {names_str} }}
      ?item wdt:P225 ?scientificName .
      ?item wikibase:sitelinks ?sitelinks .
      OPTIONAL {{
        ?article schema:about ?item ;
                 schema:isPartOf <https://en.wikipedia.org/> ;
                 schema:name ?enTitle .
      }}
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
            with urllib.request.urlopen(req, timeout=35) as resp:
                data_json = json.loads(resp.read().decode("utf-8"))
                for row in data_json.get("results", {}).get("bindings", []):
                    sci = row["scientificName"]["value"]
                    sitelinks = int(row["sitelinks"]["value"])
                    qid = row["item"]["value"].split("/")[-1]
                    en_title = row.get("enTitle", {}).get("value")
                    
                    # Keep highest sitelinks if duplicate taxon item exists
                    if sci not in results or sitelinks > results[sci]["swiki"]:
                        results[sci] = {
                            "qid": qid,
                            "swiki": sitelinks,
                            "en_title": en_title,
                        }
                return results
        except Exception as e:
            if attempt < 2:
                time.sleep(2 ** attempt)
            else:
                print(f"  SPARQL batch error ({len(scientific_names)} names) after 3 attempts: {e}")
    return results

def query_enwiki_fallback_batch(titles):
    """Query MediaWiki API for titles to find their wikibase_item (QID) and resolved canonical title.
    Accurately maps original input titles across normalized spellings and redirects.
    Chunks requests into slices of <= 35 titles to strictly honor MediaWiki limit of 50."""
    if not titles:
        return {}
    
    results = {}
    CHUNK_SIZE = 35
    for i in range(0, len(titles), CHUNK_SIZE):
        chunk = titles[i:i + CHUNK_SIZE]
        url = "https://en.wikipedia.org/w/api.php"
        data = urllib.parse.urlencode({
            "action": "query",
            "titles": "|".join(chunk),
            "prop": "pageprops",
            "redirects": "1",
            "format": "json",
        }).encode("utf-8")
        
        req = urllib.request.Request(
            url,
            data=data,
            headers={"User-Agent": USER_AGENT, "Content-Type": "application/x-www-form-urlencoded"},
        )
        
        for attempt in range(3):
            try:
                with urllib.request.urlopen(req, timeout=15) as resp:
                    data_json = json.loads(resp.read().decode("utf-8"))
                    pages = data_json.get("query", {}).get("pages", {})
                    canonical_map = {}
                    for pid, pinfo in pages.items():
                        if pid != "-1" and "pageprops" in pinfo:
                            qid = pinfo["pageprops"].get("wikibase_item")
                            canonical_title = pinfo.get("title")
                            if qid and canonical_title:
                                canonical_map[canonical_title] = (qid, canonical_title)
                                canonical_map[canonical_title.lower()] = (qid, canonical_title)

                    alias_to_target = {}
                    for norm in data_json.get("query", {}).get("normalized", []):
                        alias_to_target[norm["from"]] = norm["to"]
                        alias_to_target[norm["from"].lower()] = norm["to"]
                    for red in data_json.get("query", {}).get("redirects", []):
                        alias_to_target[red["from"]] = red["to"]
                        alias_to_target[red["from"].lower()] = red["to"]

                    for t in chunk:
                        curr = t
                        for _ in range(5):
                            if curr in canonical_map:
                                results[t] = canonical_map[curr]
                                break
                            if curr.lower() in canonical_map:
                                results[t] = canonical_map[curr.lower()]
                                break
                            if curr in alias_to_target:
                                curr = alias_to_target[curr]
                            elif curr.lower() in alias_to_target:
                                curr = alias_to_target[curr.lower()]
                            else:
                                break
                    break
            except Exception as e:
                if attempt < 2:
                    time.sleep(2.0 * (attempt + 1))
                else:
                    print(f"  EnWiki fallback batch error: {e}")
    return results

BIOLOGICAL_P31 = {
    "Q16521", "Q23038290", "Q310890", "Q47487597", "Q713623",
    "Q55983715", "Q4886", "Q15926588", "Q207106", "Q146", "Q5"
}
DISAMBIGUATION_P31 = {"Q4167410", "Q22808320", "Q15407973"}
HIGHER_RANKS = {
    "Q35409", "Q36732", "Q38348", "Q16428", "Q2455704", "Q34740",
    "Q5867051", "Q5867959", "Q5868144", "Q2889003", "Q2136103", "Q713623"
}

def format_title_case(s):
    """Title-case an English vernacular name without capitalizing letters after apostrophes."""
    if not s:
        return ""
    return re.sub(
        r"[A-Za-z]+('[A-Za-z]+)?",
        lambda m: m.group(0)[0].upper() + m.group(0)[1:].lower(),
        s,
    )

def extract_scientific_from_display(display_str):
    """Extract scientific name from 'Common Name (Scientific Name)' safely with nested parens."""
    if not display_str:
        return "", ""
    idx = display_str.find(" (")
    if idx != -1 and display_str.endswith(")"):
        return display_str[:idx].strip(), display_str[idx + 2 : -1].strip()
    return "", display_str.strip()

def query_wikidata_sitelinks_by_qids(qids):
    """Query wbgetentities for a list of QIDs to get sitelink counts and verify biological P31/P225 claims.

    Also returns (additive keys, ignored by the popularity steps):
      p685  - set of NCBI taxonomy IDs on the item (used by Step 5C to verify redirect targets)
      p1843 - list of (text, lang) English taxon common names (used by Step 6)
    """
    if not qids:
        return {}
    results = {}
    for i in range(0, len(qids), 50):
        chunk = qids[i:i + 50]
        url = f"https://www.wikidata.org/w/api.php?action=wbgetentities&ids={'|'.join(chunk)}&props=sitelinks|claims&format=json"
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                data_json = json.loads(resp.read().decode("utf-8"))
                for qid, ent in data_json.get("entities", {}).items():
                    sitelinks = ent.get("sitelinks", {})
                    en_title = sitelinks.get("enwiki", {}).get("title")
                    claims = ent.get("claims", {})
                    p31 = {
                        c.get("mainsnak", {}).get("datavalue", {}).get("value", {}).get("id")
                        for c in claims.get("P31", [])
                        if isinstance(c.get("mainsnak", {}).get("datavalue", {}).get("value"), dict)
                    }
                    p105 = {
                        c.get("mainsnak", {}).get("datavalue", {}).get("value", {}).get("id")
                        for c in claims.get("P105", [])
                        if isinstance(c.get("mainsnak", {}).get("datavalue", {}).get("value"), dict)
                    }
                    p225 = {
                        c.get("mainsnak", {}).get("datavalue", {}).get("value")
                        for c in claims.get("P225", [])
                        if isinstance(c.get("mainsnak", {}).get("datavalue", {}).get("value"), str)
                    }
                    p685 = {
                        c.get("mainsnak", {}).get("datavalue", {}).get("value")
                        for c in claims.get("P685", [])
                        if isinstance(c.get("mainsnak", {}).get("datavalue", {}).get("value"), str)
                    }
                    p1843 = _best_rank_monolingual(claims.get("P1843", []))
                    is_bio = bool((p31 & BIOLOGICAL_P31) or p225 or qid in ("Q5", "Q146")) and not bool(p31 & DISAMBIGUATION_P31)
                    results[qid] = {
                        "swiki": len(sitelinks),
                        "en_title": en_title,
                        "is_bio": is_bio,
                        "p225": p225,
                        "p105": p105,
                        "p685": p685,
                        "p1843": p1843,
                    }
        except Exception as e:
            print(f"  QID sitelinks error: {e}")
    return results

def _best_rank_monolingual(statements):
    """Return [(text, lang)] for English monolingual statements, honoring Wikidata ranks
    the same way SPARQL's wdt: does (preferred-rank statements win; deprecated are dropped)."""
    live = [s for s in statements if s.get("rank") != "deprecated"]
    preferred = [s for s in live if s.get("rank") == "preferred"]
    out = []
    for s in (preferred or live):
        val = s.get("mainsnak", {}).get("datavalue", {}).get("value")
        if isinstance(val, dict) and str(val.get("language", "")).lower().startswith("en"):
            out.append((val.get("text", ""), val.get("language", "")))
    return out

def print_progress(current, total, prefix="Progress", bar_length=30, extra=""):
    """Render a live single-line terminal progress bar."""
    percent = (current / total) * 100 if total > 0 else 0
    filled = int(bar_length * current // total) if total > 0 else 0
    bar = "█" * filled + "░" * (bar_length - filled)
    msg = f"\r  {prefix}: [{bar}] {current:,}/{total:,} ({percent:5.1f}%) {extra}"
    sys.stdout.write(msg[:100].ljust(100))
    sys.stdout.flush()
    if current >= total:
        sys.stdout.write("\n")

def fetch_single_pageview(title, start_date=START_DATE, end_date=END_DATE):
    """Fetch multi-year cumulative pageviews for an English Wikipedia article.
    Resilient retry with exponential backoff on 429/503/timeouts.
    Returns (title, views). Returns (title, None) on transient failure so cache is NOT corrupted with 0."""
    if not title:
        return title, 0
    clean_title = urllib.parse.quote(title.strip().replace(" ", "_"), safe="")
    url = f"https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/en.wikipedia.org/all-access/all-agents/{clean_title}/monthly/{start_date}/{end_date}"
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    
    for attempt in range(6):
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                items = data.get("items", [])
                total_views = sum(item.get("views", 0) for item in items)
                return title, total_views
        except urllib.error.HTTPError as e:
            if e.code == 404:
                # Article legitimately does not exist or has 0 pageviews
                return title, 0
            if e.code in (429, 502, 503):
                # Exponential backoff on rate limits
                backoff = min(2.0 ** attempt, 16.0)
                time.sleep(backoff)
            else:
                return title, 0
        except Exception:
            # Network drop or socket timeout; back off and retry
            backoff = min(1.0 * (attempt + 1), 6.0)
            time.sleep(backoff)
    
    # If 6 attempts failed, return None so we don't poison cache with 0 views
    return title, None


# ==============================================================================
# POPULARITY STAGES (Steps 1-4) — logic unchanged from rank_species_popularity.py,
# only split out of main() into functions so stages can be selected by flags.
# ==============================================================================

def step1_resolve_wikidata_sitelinks(species_data, cache):
    """Step 1: Query Wikidata for Swiki and en_title (only for uncached species OR species where qid is None)."""
    missing_wikidata = [
        s for s in species_data 
        if s["scientific"] not in cache 
        or cache[s["scientific"]].get("qid") is None 
        or "swiki" not in cache[s["scientific"]]
    ]
    if missing_wikidata:
        print(f"\nStep 1: Resolving Wikidata sitelinks for {len(missing_wikidata):,} species...")
        BATCH_SIZE = 120
        for i in range(0, len(missing_wikidata), BATCH_SIZE):
            batch = missing_wikidata[i:i + BATCH_SIZE]
            sci_names = [s["scientific"] for s in batch]
            batch_results = query_wikidata_batch(sci_names)
            for s in batch:
                sci = s["scientific"]
                if sci in batch_results:
                    cache[sci] = {
                        "common": s.get("common", ""),
                        "scientific": sci,
                        "kingdom": s.get("kingdom", ""),
                        "class": s.get("class", ""),
                        "order": s.get("order", ""),
                        "family": s.get("family", ""),
                        "qid": batch_results[sci]["qid"],
                        "swiki": batch_results[sci]["swiki"],
                        "en_title": batch_results[sci]["en_title"],
                    }
                else:
                    if sci not in cache or cache[sci].get("qid") is None:
                        cache[sci] = {
                            "common": s.get("common", ""),
                            "scientific": sci,
                            "kingdom": s.get("kingdom", ""),
                            "class": s.get("class", ""),
                            "order": s.get("order", ""),
                            "family": s.get("family", ""),
                            "qid": None,
                            "swiki": 0,
                            "en_title": None,
                        }
            processed = min(i + BATCH_SIZE, len(missing_wikidata))
            if (i // BATCH_SIZE) % 5 == 0 or processed == len(missing_wikidata):
                print(f"  Processed {processed:,} / {len(missing_wikidata):,} species in Step 1...")
                save_cache(cache)
            time.sleep(0.15)
        save_cache(cache)
        print("Step 1 complete.")
    else:
        print("\nStep 1: All Wikidata sitelinks already resolved. Skipping.")

def step2_resolve_canonical_titles(species_data, cache):
    """Step 2: Fallback lookup for species where title has not been canonical-verified."""
    needs_fallback = [
        s for s in species_data
        if not cache.get(s["scientific"], {}).get("canonical_verified")
    ]
    if needs_fallback:
        print(f"\nStep 2: Checking Wikipedia fallbacks & canonical titles for {len(needs_fallback):,} species...")
        FB_BATCH = 25
        for i in range(0, len(needs_fallback), FB_BATCH):
            batch = needs_fallback[i:i + FB_BATCH]
            titles_to_check = []
            sci_to_titles = {}
            for s in batch:
                titles = []
                c = (s.get("common") or "").strip()
                sci = (s.get("scientific") or "").strip()
                cached_title = cache.get(sci, {}).get("en_title")
                if cached_title:
                    titles.append(cached_title)
                if c:
                    titles.append(c)
                    # Sentence-cased variant: e.g. "Bluespotted corydoras", "Blackhand sole"
                    titles.append(c[0].upper() + c[1:].lower())
                    if "-" in c:
                        c_no = c.replace("-", " ")
                        titles.append(c_no)
                        titles.append(c_no[0].upper() + c_no[1:].lower())
                if sci:
                    titles.append(sci)
                    if sci.endswith("ii"):
                        titles.append(sci[:-1])
                    elif sci.endswith("us"):
                        titles.append(sci[:-2] + "a")
                    elif sci.endswith("a"):
                        titles.append(sci[:-1] + "us")
                clean_titles = list(dict.fromkeys(titles))
                titles_to_check.extend(clean_titles)
                sci_to_titles[s["scientific"]] = clean_titles

            all_catalog_scis = {sp["scientific"] for sp in species_data}
            resolved_map = query_enwiki_fallback_batch(titles_to_check)
            if resolved_map:
                qids_to_query = list(set(qid for qid, _ in resolved_map.values() if qid))
                qid_data = query_wikidata_sitelinks_by_qids(qids_to_query) if qids_to_query else {}
                for s in batch:
                    sci = s["scientific"]
                    s_rank = s.get("rank", "Species")
                    best_qid = None
                    best_swiki = cache.get(sci, {}).get("swiki", 0)
                    best_title = cache.get(sci, {}).get("en_title")
                    has_step1_qid = bool(cache.get(sci, {}).get("qid"))
                    for t in sci_to_titles[sci]:
                        if t in resolved_map:
                            qid, can_title = resolved_map[t]
                            qmeta = qid_data.get(qid, {}) if qid else {}
                            if not qmeta.get("is_bio"):
                                continue
                            p225_set = qmeta.get("p225", set())
                            p105_set = qmeta.get("p105", set())
                            # Reject if candidate QID's P225 belongs to a different catalog taxon
                            if p225_set and sci not in p225_set:
                                if any(other in all_catalog_scis for other in p225_set):
                                    continue
                                if s_rank == "Species" and (p105_set & HIGHER_RANKS):
                                    continue
                                if has_step1_qid:
                                    continue
                            s_count = qmeta.get("swiki", 0)
                            if s_count > best_swiki or not best_title:
                                best_swiki = max(best_swiki, s_count)
                                best_qid = qid
                                best_title = can_title
                    if best_title:
                        if best_title != cache[sci].get("en_title"):
                            cache[sci]["en_title"] = best_title
                            cache[sci]["vwiki_period"] = None  # Invalidate cached views on title change
                    if best_qid and best_swiki > cache.get(sci, {}).get("swiki", 0):
                        cache[sci]["qid"] = best_qid
                        cache[sci]["swiki"] = best_swiki
            for s in batch:
                sci = s["scientific"]
                if sci in cache:
                    cache[sci]["canonical_verified"] = True

            processed = min(i + FB_BATCH, len(needs_fallback))
            if (i // FB_BATCH) % 10 == 0 or processed == len(needs_fallback):
                print_progress(processed, len(needs_fallback), prefix="Resolving Fallbacks")
                save_cache(cache)
            time.sleep(0.2)
        save_cache(cache)
        print("\nStep 2 complete. All redirects and canonical articles resolved.")
    else:
        print("\nStep 2: All canonical titles already resolved. Skipping.")

def step2b_discover_extra_articles(species_data, cache, rediscover=False):
    """Step 2B: Option B - Discover Exclusive Standalone Articles (Cultivars, Subspecies & Domestic Forms)."""
    existing_extra_count = sum(len(rec.get("extra_articles", {})) for rec in cache.values())
    if existing_extra_count > 0 and not rediscover:
        print(f"\nStep 2B: {existing_extra_count} exclusive standalone articles already discovered and cached. Skipping.")
        return

    print("\nStep 2B: Option B - Discovering exclusive standalone articles (cultivars, subspecies)...")
    
    # Precompute umbrella words & polytypic genera/families
    polytypic_genera = set()
    polytypic_families = set()
    genus_counts = {}
    family_counts = {}
    for s in species_data:
        g = (s.get("genus") or "").lower()
        fam = (s.get("family") or "").lower()
        if g: genus_counts[g] = genus_counts.get(g, 0) + 1
        if fam: family_counts[fam] = family_counts.get(fam, 0) + 1
    for g, c in genus_counts.items():
        if c > 1: polytypic_genera.add(g)
    for fam, c in family_counts.items():
        if c > 1: polytypic_families.add(fam)

    umbrella_words = {
        "elephant", "salmon", "crow", "tuna", "shark", "whale", "dolphin", "frog", "toad",
        "snake", "lizard", "turtle", "tortoise", "bear", "duck", "goose", "owl", "eagle",
        "hawk", "falcon", "sparrow", "finch", "warbler", "thrush", "pigeon", "dove",
        "bat", "mouse", "rat", "squirrel", "deer", "antelope", "gazelle", "monkey", "baboon",
        "beetle", "butterfly", "moth", "ant", "bee", "wasp", "fly", "spider", "crab", "lobster",
        "shrimp", "snail", "slug", "clam", "mussel", "oyster", "squid", "octopus", "jellyfish",
        "coral", "anemone", "worm", "sponge", "tree", "flower", "grass", "fern", "moss",
        "mushroom", "fungus", "lichen", "alga", "algae", "bacteria", "bacterium", "virus",
        "fish", "bird", "mammal", "reptile", "amphibian", "insect", "animal", "plant",
        "dory", "timber wolf", "panther", "puma", "feline", "gator", "bullfrog", "buffalo", "bison", "alligator", "cod",
        "penguin", "otter", "zebra", "crocodile", "anaconda", "raven", "manta ray", "mako shark", "clownfish",
        "hammerhead shark", "badger", "echidna", "wolf", "grey wolf", "gray wolf", "sirenia", "trout"
    }

    def is_umbrella(t):
        cl = t.strip().lower()
        return (cl in umbrella_words or cl in polytypic_genera or cl in polytypic_families)

    catalog_scis = set(s["scientific"] for s in species_data)
    catalog_commons_lower = set((s.get("common") or "").lower() for s in species_data if s.get("common"))
    all_primary_en_titles = set(
        (rec.get("en_title") or "").strip().lower()
        for rec in cache.values()
        if rec.get("en_title")
    )

    # Map aliases to species
    alias_to_sci = {}
    if os.path.exists(ALIASES_PATH):
        with open(ALIASES_PATH, "r", encoding="utf-8") as f:
            raw_aliases = json.load(f)
        for a, target in raw_aliases.items():
            comm, sci = extract_scientific_from_display(target)
            if a.lower() == sci.lower() or a.lower() == comm.lower() or "(" in a:
                continue
            clean_a = a.strip()
            clean_lower = clean_a.lower()
            if clean_lower not in alias_to_sci:
                alias_to_sci[clean_lower] = sci

    # Resolve candidate aliases
    resolved_aliases = query_enwiki_fallback_batch(list(alias_to_sci.keys()))
    candidates = []
    qids_to_query = []
    for a, sci in alias_to_sci.items():
        if is_umbrella(a): continue
        res = resolved_aliases.get(a)
        if not res: continue
        qid, target = res
        if not target or not qid: continue
        prim = cache.get(sci, {}).get("en_title", "")
        if target.strip().lower() == prim.strip().lower(): continue
        if target.strip().lower() in all_primary_en_titles: continue
        if is_umbrella(target): continue
        if target in catalog_scis or target.lower() in catalog_commons_lower:
            continue
        candidates.append((sci, prim, a, target, qid))
        qids_to_query.append(qid)

    # Query Wikidata for P31 and P105
    VALID_P31 = {"Q16521", "Q23038290", "Q767728", "Q4886", "Q15926588", "Q11004", "Q55983715", "Q207106", "Q146"}
    valid_qids = set()
    for i in range(0, len(qids_to_query), 50):
        chunk = qids_to_query[i:i+50]
        url = "https://www.wikidata.org/w/api.php?action=wbgetentities&ids=" + "|".join(chunk) + "&props=claims&format=json"
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        for attempt in range(3):
            try:
                with urllib.request.urlopen(req, timeout=15) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                    for q, ent in data.get("entities", {}).items():
                        claims = ent.get("claims", {})
                        p31 = set(c.get("mainsnak", {}).get("datavalue", {}).get("value", {}).get("id") for c in claims.get("P31", []) if isinstance(c.get("mainsnak", {}).get("datavalue", {}).get("value"), dict))
                        p105 = set(c.get("mainsnak", {}).get("datavalue", {}).get("value", {}).get("id") for c in claims.get("P105", []) if isinstance(c.get("mainsnak", {}).get("datavalue", {}).get("value"), dict))
                        if q in ("Q5", "Q146") or ((p31 & VALID_P31) and not (p105 & HIGHER_RANKS) and not (p31 & DISAMBIGUATION_P31)):
                            valid_qids.add(q)
                break
            except Exception as e:
                if attempt < 2:
                    time.sleep(2.0 * (attempt + 1))
                else:
                    print(f"  Wikidata rank check error after 3 attempts: {e}")

    extra_articles_count = 0
    for sci, prim, a, target, qid in candidates:
        if qid in valid_qids:
            if "extra_articles" not in cache[sci]:
                cache[sci]["extra_articles"] = {}
            if target not in cache[sci]["extra_articles"]:
                cache[sci]["extra_articles"][target] = 0
                extra_articles_count += 1

    save_cache(cache)
    print(f"Step 2B complete: Discovered {extra_articles_count} exclusive standalone articles for Option B rollup.")

def step3_fetch_pageviews(species_data, cache):
    """Step 3: Fetch Wikipedia cumulative pageviews (Vwiki). Targets species without current period data."""
    print(f"\nStep 3: Checking Wikipedia {DATE_LABEL} cumulative pageviews (Vwiki)...")
    need_views = []
    for s in species_data:
        sci = s["scientific"]
        rec = cache.get(sci, {})
        en_title = rec.get("en_title")
        if en_title:
            is_missing_period = (rec.get("vwiki_period") != CACHE_PERIOD_KEY)
            if is_missing_period:
                need_views.append((sci, en_title, False))
        else:
            if rec.get("vwiki", 0) != 0:
                rec["vwiki"] = 0
        for extra_t, eviews in rec.get("extra_articles", {}).items():
            if rec.get("vwiki_period") != CACHE_PERIOD_KEY:
                need_views.append((sci, extra_t, True))

    unique_titles = {}
    for sci, title, is_extra in need_views:
        clean_t = title.strip()
        if clean_t not in unique_titles:
            unique_titles[clean_t] = []
        unique_titles[clean_t].append((sci, is_extra))

    total_unique = len(unique_titles)
    print(f"Total unique Wikipedia articles to query/repair: {total_unique:,}")

    if total_unique > 0:
        t_start = time.time()
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            futures = {executor.submit(fetch_single_pageview, t): t for t in unique_titles}
            count = 0
            for fut in as_completed(futures):
                t, views = fut.result()
                if views is not None:
                    for sci, is_extra in unique_titles[t]:
                        if is_extra:
                            if "extra_articles" not in cache[sci]:
                                cache[sci]["extra_articles"] = {}
                            cache[sci]["extra_articles"][t] = views
                        else:
                            cache[sci]["vwiki"] = views
                        cache[sci]["vwiki_period"] = CACHE_PERIOD_KEY
                count += 1
                
                # Live dynamic terminal progress bar
                elapsed = time.time() - t_start
                rate = count / elapsed if elapsed > 0 else 0
                eta_sec = int((total_unique - count) / rate) if rate > 0 else 0
                eta_str = f"{eta_sec // 60}m {eta_sec % 60}s" if eta_sec > 60 else f"{eta_sec}s"
                extra = f"| {rate:.1f} req/s | ETA: {eta_str}"
                print_progress(count, total_unique, prefix=f"Fetching Views ({DATE_LABEL})", extra=extra)

                if count % SAVE_INTERVAL == 0 or count == total_unique:
                    save_cache(cache)

        save_cache(cache)
        print(f"\nStep 3 complete. All metrics cached to {CACHE_PATH}.")
    else:
        print(f"All {DATE_LABEL} pageviews already cached and valid! Skipping Step 3.")

def compile_ranking_csvs(species_data, cache):
    """Step 4: Deduplicate Catalog by Scientific Name & Output Comprehensive CSV Documents."""
    print("\nStep 4: Deduplicating by primary species ID and compiling ranking CSV documents...")
    from harvest_and_audit_species_aliases import build_vocabularies, is_clean_vernacular_alias

    dict_words, catalog_eng_words, latin_words, _ = build_vocabularies(species_data)

    # Load alternative common name aliases from data/species_aliases.json
    sci_to_aliases = {}
    if os.path.exists(ALIASES_PATH):
        with open(ALIASES_PATH, "r", encoding="utf-8") as f:
            raw_aliases = json.load(f)
        for alias_key, canonical_target in raw_aliases.items():
            target_comm, target_sci = extract_scientific_from_display(canonical_target)
            clean_a = alias_key.strip()
            # Only include clean human vernacular aliases in the human-facing CSV column
            if not is_clean_vernacular_alias(clean_a, target_comm, target_sci, dict_words, catalog_eng_words, latin_words):
                continue
            clean_formatted = format_title_case(clean_a)
            sci_to_aliases.setdefault(target_sci, set()).add(clean_formatted)

    # Load manual common name overrides if defined
    overrides = {}
    if os.path.exists(OVERRIDES_PATH):
        try:
            with open(OVERRIDES_PATH, "r", encoding="utf-8") as f:
                raw_ov = json.load(f)
                for k, v in raw_ov.items():
                    val = v.get("common", "").strip() if isinstance(v, dict) else str(v).strip()
                    if val:
                        overrides[k.strip().lower()] = val
        except Exception as e:
            print(f"Warning: could not read overrides from {OVERRIDES_PATH}: {e}")

    # Group catalog entries by scientific name to eliminate duplicate common name rows
    total_species = len(species_data)
    species_by_sci = {}
    for s in species_data:
        sci = s["scientific"]
        comm = (s.get("common") or "").strip()
        sci_low = sci.lower()
        if sci_low in overrides:
            comm = overrides[sci_low]

        if sci not in species_by_sci:
            species_by_sci[sci] = {
                "common": comm,
                "all_commons": set([comm]) if comm else set(),
                "scientific": sci,
                "kingdom": s.get("kingdom", ""),
                "class": s.get("class", ""),
                "order": s.get("order", ""),
                "family": s.get("family", ""),
                "rank": s.get("rank", "Species"),
            }
        else:
            if comm:
                species_by_sci[sci]["all_commons"].add(comm)
                curr = species_by_sci[sci]["common"]
                if sci_low in overrides:
                    species_by_sci[sci]["common"] = overrides[sci_low]
                elif not curr or len(comm) < len(curr):
                    species_by_sci[sci]["common"] = comm

    print(f"Aggregated {total_species:,} catalog entries into {len(species_by_sci):,} unique biological species.")

    # Enforce 1-to-1 primary en_title ownership invariant across all species
    title_groups = {}
    for sci in species_by_sci:
        rec = cache.get(sci, {})
        en_t = (rec.get("en_title") or "").strip()
        if en_t:
            title_groups.setdefault(en_t, []).append(sci)

    losing_scis = set()
    for en_t, scis in title_groups.items():
        if len(scis) > 1:
            t_low = en_t.lower()
            def owner_score(sc):
                sp = species_by_sci[sc]
                rk = sp.get("rank", "Species")
                comm_low = (sp.get("common") or "").lower()
                return (
                    1 if sc.lower() == t_low else 0,
                    1 if comm_low == t_low else 0,
                    1 if rk != "Species" else 0,
                    cache.get(sc, {}).get("swiki", 0),
                    -len(sc),
                )
            scis_sorted = sorted(scis, key=owner_score, reverse=True)
            for loser in scis_sorted[1:]:
                losing_scis.add(loser)

    all_ranked = []
    for sci, s in species_by_sci.items():
        rec = cache.get(sci, {})
        combined_aliases = set(s["all_commons"])
        combined_aliases.discard(s["common"])
        if sci in sci_to_aliases:
            combined_aliases.update(sci_to_aliases[sci])
        aliases_list = sorted(list(combined_aliases))
        aliases_str = "; ".join(aliases_list)

        if sci in losing_scis:
            total_vwiki = 0
            full_title = ""
            swiki_val = 0
        else:
            base_vwiki = rec.get("vwiki", 0)
            extra_articles_dict = rec.get("extra_articles", {})
            extra_views = sum(extra_articles_dict.values())
            total_vwiki = base_vwiki + extra_views

            primary_title = rec.get("en_title", "")
            if extra_articles_dict:
                extra_titles_str = ", ".join(sorted(extra_articles_dict.keys()))
                full_title = f"{primary_title} (+ {extra_titles_str})" if primary_title else extra_titles_str
            else:
                full_title = primary_title
            swiki_val = rec.get("swiki", 0)

        all_ranked.append({
            "common": s["common"],
            "scientific": sci,
            "aliases": aliases_str,
            "kingdom": s["kingdom"],
            "class": s["class"],
            "order": s["order"],
            "family": s["family"],
            "swiki": swiki_val,
            "vwiki": total_vwiki,
            "en_title": full_title,
        })

    # Filter out entries with <= 1 language or <= 1 pageview, and blank titles
    # 1. By Swiki: Species with established cross-language presence and verified English article (Swiki > 1 and Vwiki > 1)
    by_swiki = sorted(
        [item for item in all_ranked if item.get("swiki", 0) > 1 and item.get("vwiki", 0) > 1 and bool((item.get("en_title") or "").strip())],
        key=lambda x: (x["swiki"], x["vwiki"], x["common"]),
        reverse=True
    )
    swiki_ranks = {item["scientific"]: r + 1 for r, item in enumerate(by_swiki)}

    # 2. By Vwiki: Species with verified English Wikipedia articles and traffic (Vwiki > 1, Swiki > 1, and non-blank title)
    by_vwiki = sorted(
        [item for item in all_ranked if item.get("vwiki", 0) > 1 and item.get("swiki", 0) > 1 and bool((item.get("en_title") or "").strip())],
        key=lambda x: (x["vwiki"], x["swiki"], x["common"]),
        reverse=True
    )
    vwiki_ranks = {item["scientific"]: r + 1 for r, item in enumerate(by_vwiki)}

    # 3. Combined: Species with verified presence in both metrics (Swiki > 1 and Vwiki > 1)
    combined_candidates = [
        item for item in all_ranked
        if item.get("swiki", 0) > 1 and item.get("vwiki", 0) > 1 and bool((item.get("en_title") or "").strip())
    ]
    by_combined = sorted(combined_candidates, key=lambda x: (x["swiki"], x["vwiki"], x["common"]), reverse=True)

    # 1. Write Comprehensive Ranking by Swiki CSV (All unique species ranked #1 to #N by Swiki)
    print(f"Writing comprehensive Swiki rankings to {SWIKI_CSV_PATH}...")
    with open(SWIKI_CSV_PATH, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "Rank_Swiki", "Swiki (Languages)", "Common Name", "Scientific Name", 
            "Alternative Names / Aliases", "Kingdom", "Class", "Order", "Family", 
            "Wikipedia Title", f"Vwiki ({DATE_LABEL} Cumulative Views)"
        ])
        for r_s, item in enumerate(by_swiki, 1):
            writer.writerow([
                r_s,
                item.get("swiki", 0),
                item.get("common") or "",
                item.get("scientific") or "",
                item.get("aliases") or "",
                item.get("kingdom") or "",
                item.get("class") or "",
                item.get("order") or "",
                item.get("family") or "",
                item.get("en_title") or "",
                item.get("vwiki", 0)
            ])

    # 2. Write Comprehensive Ranking by Vwiki CSV (All unique species ranked #1 to #N by Vwiki)
    print(f"Writing comprehensive Vwiki rankings to {VWIKI_CSV_PATH}...")
    with open(VWIKI_CSV_PATH, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "Rank_Vwiki", f"Vwiki ({DATE_LABEL} Cumulative Views)", "Common Name", "Scientific Name", 
            "Alternative Names / Aliases", "Kingdom", "Class", "Order", "Family", 
            "Wikipedia Title", "Swiki (Languages)"
        ])
        for r_v, item in enumerate(by_vwiki, 1):
            writer.writerow([
                r_v,
                item.get("vwiki", 0),
                item.get("common") or "",
                item.get("scientific") or "",
                item.get("aliases") or "",
                item.get("kingdom") or "",
                item.get("class") or "",
                item.get("order") or "",
                item.get("family") or "",
                item.get("en_title") or "",
                item.get("swiki", 0)
            ])

    # 3. Write Master Popularity Rankings CSV (All unique species with both Swiki & Vwiki ranks)
    print(f"Writing combined popularity dataset to {CSV_PATH}...")
    with open(CSV_PATH, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "Rank_Swiki", "Rank_Vwiki", "Common Name", "Scientific Name", 
            "Alternative Names / Aliases", "Kingdom", "Class", "Order", "Family", 
            "Swiki (Languages)", f"Vwiki ({DATE_LABEL} Cumulative Views)", "Wikipedia Title"
        ])
        for item in by_combined:
            r_s = swiki_ranks.get(item["scientific"], "")
            r_v = vwiki_ranks.get(item["scientific"], "")
            writer.writerow([
                r_s,
                r_v,
                item.get("common") or "",
                item.get("scientific") or "",
                item.get("aliases") or "",
                item.get("kingdom") or "",
                item.get("class") or "",
                item.get("order") or "",
                item.get("family") or "",
                item.get("swiki", 0),
                item.get("vwiki", 0),
                item.get("en_title") or ""
            ])

    print("\n" + "=" * 70)
    print("✅ Complete! All 3 comprehensive ranking documents written:")
    print(f"  1. By Swiki: {SWIKI_CSV_PATH} ({len(by_swiki):,} verified species with Swiki > 1)")
    print(f"  2. By Vwiki: {VWIKI_CSV_PATH} ({len(by_vwiki):,} verified species with Vwiki > 1 and valid title)")
    print(f"  3. Combined: {CSV_PATH} ({len(by_combined):,} verified species with both Swiki & Vwiki > 1)")
    print("=" * 70)
    print("\nPhase 1A Harvester & Ranker completed successfully!")


# ==============================================================================
# TREE STAGES (Steps 5-7): Wikipedia articles + common names for every tree node
# ==============================================================================

def load_tree_cache():
    if os.path.exists(TREE_CACHE_PATH):
        try:
            with open(TREE_CACHE_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Warning: could not load tree cache: {e}")
    return {}

def save_tree_cache(tree_cache):
    # Sorted by taxid so diffs between runs are readable
    ordered = dict(sorted(tree_cache.items(), key=lambda kv: int(kv[0]) if kv[0].isdigit() else 0))
    with open(TREE_CACHE_PATH, "w", encoding="utf-8") as f:
        json.dump(ordered, f, indent=1, ensure_ascii=False)

def save_tree_formatted(tree_path, tree):
    """Write phylogeny_tree.json in the same one-entry-per-line layout build_phylogeny_tree.py uses
    (much smaller than indent=2 and still diff-friendly)."""
    with open(tree_path, "w", encoding="utf-8") as f:
        f.write('{\n  "species": {\n')
        species_items = list(tree["species"].items())
        for i, (k, v) in enumerate(species_items):
            comma = "," if i < len(species_items) - 1 else ""
            f.write(f'    {json.dumps(k, ensure_ascii=False)}: {json.dumps(v, ensure_ascii=False)}{comma}\n')
        f.write('  },\n  "nodes": {\n')
        node_items = list(tree["nodes"].items())
        for i, (k, v) in enumerate(node_items):
            comma = "," if i < len(node_items) - 1 else ""
            f.write(f'    {json.dumps(k, ensure_ascii=False)}: {json.dumps(v, ensure_ascii=False)}{comma}\n')
        f.write('  }\n}\n')

def build_parent_map(tree):
    """Child taxid -> parent taxid (both str), derived from the NCBI lineages stored per species."""
    parent = {}
    for lineage in tree.get("species", {}).values():
        lin = [str(t) for t in lineage]
        for i in range(1, len(lin)):
            parent.setdefault(lin[i], lin[i - 1])
    return parent

def ancestors_of(taxid, parent):
    """Set of all ancestor taxids of `taxid` according to the parent map."""
    out = set()
    cur = parent.get(taxid)
    while cur and cur not in out:
        out.add(cur)
        cur = parent.get(cur)
    return out

def is_lineage_related(node_taxid, target_taxids, parent):
    """True if any of target_taxids is an ancestor of node_taxid, or node_taxid is an ancestor of it.
    Used to accept a Wikipedia redirect onto a different taxon only when it is the same lineage
    (e.g. Clupeocephala -> 'Teleost' article, whose item is Teleostei, an ancestor)."""
    node_anc = ancestors_of(node_taxid, parent)
    for t in target_taxids:
        if t in node_anc:
            return True
        if node_taxid in ancestors_of(t, parent):
            return True
    return False

def _sparql_post(sparql, timeout=60):
    """POST a SPARQL query. Returns (ok, bindings). ok=False means a network/server failure,
    which callers must NOT interpret as 'no results' (anti-poisoning)."""
    data = urllib.parse.urlencode({"query": sparql, "format": "json"}).encode("utf-8")
    req = urllib.request.Request(
        "https://query.wikidata.org/sparql",
        data=data,
        headers={
            "User-Agent": USER_AGENT,
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/sparql-results+json",
        },
    )
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return True, json.loads(resp.read().decode("utf-8")).get("results", {}).get("bindings", [])
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503, 504) and attempt < 3:
                time.sleep(min(2.0 ** (attempt + 1), 20.0))
                continue
            print(f"  SPARQL HTTP {e.code}: {e.reason}")
            return False, []
        except Exception as e:
            if attempt < 3:
                time.sleep(2.0 * (attempt + 1))
                continue
            print(f"  SPARQL error after retries: {e}")
            return False, []
    return False, []

# Shared SELECT body: item metadata + enwiki title + English common names (best-rank via wdt:)
_TAXON_ITEM_FIELDS = """
  ?item wikibase:sitelinks ?sitelinks .
  OPTIONAL { ?item wdt:P225 ?sci . }
  OPTIONAL { ?item wdt:P685 ?ncbiOnItem . }
  OPTIONAL {
    ?article schema:about ?item ;
             schema:isPartOf <https://en.wikipedia.org/> ;
             schema:name ?enTitle .
  }
  OPTIONAL { ?item wdt:P1843 ?cn . FILTER(LANGMATCHES(LANG(?cn), "en")) }
"""

def _collect_items(bindings, key_var):
    """Fold SPARQL rows (one per combination of optional values) into
    {key: {qid: {swiki, en_title, p225:set, p685:set, p1843:set((text, lang))}}}."""
    out = {}
    for row in bindings:
        key = row[key_var]["value"]
        qid = row["item"]["value"].rsplit("/", 1)[-1]
        rec = out.setdefault(key, {}).setdefault(qid, {
            "swiki": int(row["sitelinks"]["value"]),
            "en_title": None, "p225": set(), "p685": set(), "p1843": set(),
        })
        if "enTitle" in row:
            rec["en_title"] = row["enTitle"]["value"]
        if "sci" in row:
            rec["p225"].add(row["sci"]["value"])
        if "ncbiOnItem" in row:
            rec["p685"].add(row["ncbiOnItem"]["value"])
        if "cn" in row:
            rec["p1843"].add((row["cn"]["value"], row["cn"].get("xml:lang", "")))
    return out

def query_wikidata_by_ncbi_taxids(taxids):
    """Step 5A: exact join on NCBI taxonomy ID (Wikidata P685). Returns (ok, {taxid: {qid: rec}})."""
    values = " ".join(f'"{t}"' for t in taxids)
    sparql = f"""
    SELECT ?ncbi ?item ?sitelinks ?sci ?ncbiOnItem ?enTitle ?cn WHERE {{
      VALUES ?ncbi {{ {values} }}
      ?item wdt:P685 ?ncbi .
      {_TAXON_ITEM_FIELDS}
    }}"""
    ok, bindings = _sparql_post(sparql)
    return ok, _collect_items(bindings, "ncbi") if ok else {}

def query_wikidata_by_scientific_names(names):
    """Step 5B: join on scientific name (P225). Returns (ok, {name: {qid: rec}})."""
    values = " ".join('"' + n.replace("\\", "\\\\").replace('"', '\\"') + '"' for n in names)
    sparql = f"""
    SELECT ?name ?item ?sitelinks ?sci ?ncbiOnItem ?enTitle ?cn WHERE {{
      VALUES ?name {{ {values} }}
      ?item wdt:P225 ?name .
      {_TAXON_ITEM_FIELDS}
    }}"""
    ok, bindings = _sparql_post(sparql)
    return ok, _collect_items(bindings, "name") if ok else {}

def _pick_item(items):
    """Among several Wikidata items for one key, prefer one with an enwiki article, then most sitelinks."""
    if not items:
        return None, None
    qid = max(items, key=lambda q: (1 if items[q]["en_title"] else 0, items[q]["swiki"]))
    return qid, items[qid]

def _tree_work_list(tree, tree_cache, recheck_missing):
    """Which non-species nodes need (re)resolution. See module docstring for the rules."""
    work = []
    for tid, node in tree["nodes"].items():
        name = (node.get("name") or "").strip()
        if node.get("rank") == "Species" or not name or name.lower() in ("root", "?"):
            continue
        rec = tree_cache.get(tid)
        if (rec is None
                or rec.get("name") != name
                or rec.get("resolver_version") != TREE_RESOLVER_VERSION
                or rec.get("status") == "error"
                or (recheck_missing and rec.get("status") == "no_article")):
            work.append(tid)
    return work

def step5_link_tree_nodes(tree, tree_cache, recheck_missing=False, max_batches=0):
    """Step 5: Attach a Wikipedia article (and Wikidata item) to every non-species tree node."""
    nodes = tree["nodes"]
    work = _tree_work_list(tree, tree_cache, recheck_missing)
    if not work:
        print("\nStep 5: All tree nodes already linked (or confirmed article-less). Skipping.")
        return
    if max_batches > 0:
        work = work[:max_batches * TREE_SPARQL_BATCH]
    print(f"\nStep 5: Linking {len(work):,} tree nodes to Wikipedia...")
    parent = build_parent_map(tree)

    # Working records for this run, keyed by taxid
    pending = {}
    for tid in work:
        pending[tid] = {
            "name": nodes[tid]["name"].strip(),
            "rank": nodes[tid].get("rank", ""),
            "status": None, "match": None,
            "qid": None, "en_title": None, "swiki": 0,
            "p225": [], "p1843": [],
            "resolver_version": TREE_RESOLVER_VERSION,
        }
    errored = set()

    # ---- 5A: exact NCBI taxid join -------------------------------------------------
    for i in range(0, len(work), TREE_SPARQL_BATCH):
        chunk = work[i:i + TREE_SPARQL_BATCH]
        ok, found = query_wikidata_by_ncbi_taxids(chunk)
        if not ok:
            errored.update(chunk)
        else:
            for tid in chunk:
                qid, item = _pick_item(found.get(tid, {}))
                if not qid:
                    continue
                r = pending[tid]
                r.update(qid=qid, swiki=item["swiki"], p225=sorted(item["p225"]),
                         p1843=sorted(item["p1843"]))
                if item["en_title"]:
                    r.update(status="linked", match="ncbi_taxid", en_title=item["en_title"])
        print_progress(min(i + TREE_SPARQL_BATCH, len(work)), len(work), prefix="5A NCBI-ID join")
        time.sleep(0.3)

    # ---- 5B: scientific-name join (only for nodes with no exact Wikidata item at all) ----
    need_b = [t for t in work if t not in errored and not pending[t]["qid"]]
    if need_b:
        for i in range(0, len(need_b), TREE_SPARQL_BATCH):
            chunk = need_b[i:i + TREE_SPARQL_BATCH]
            ok, found = query_wikidata_by_scientific_names([pending[t]["name"] for t in chunk])
            if not ok:
                errored.update(chunk)
            else:
                for tid in chunk:
                    items = found.get(pending[tid]["name"], {})
                    # Homonym safety: drop items that carry a *different* NCBI taxid.
                    items = {q: it for q, it in items.items() if not it["p685"] or tid in it["p685"]}
                    # If several unrelated items still share the name, we cannot tell which is ours.
                    if len(items) != 1:
                        continue
                    qid, item = next(iter(items.items()))
                    r = pending[tid]
                    r.update(qid=qid, swiki=item["swiki"], p225=sorted(item["p225"]),
                             p1843=sorted(item["p1843"]))
                    if item["en_title"]:
                        r.update(status="linked", match="scientific_name", en_title=item["en_title"])
            print_progress(min(i + TREE_SPARQL_BATCH, len(need_b)), len(need_b), prefix="5B name join  ")
            time.sleep(0.3)

    # ---- 5C: enwiki title + redirect resolution (reuses the debugged Step 2 helpers) ----
    need_c = [t for t in work if t not in errored and not pending[t]["en_title"]]
    if need_c:
        print(f"  5C: enwiki redirect lookup for {len(need_c):,} nodes without a direct article...")
        names = list(dict.fromkeys(pending[t]["name"] for t in need_c))
        resolved = query_enwiki_fallback_batch(names)
        qmeta = query_wikidata_sitelinks_by_qids(sorted({q for q, _ in resolved.values() if q}))
        for tid in need_c:
            r = pending[tid]
            hit = resolved.get(r["name"])
            if not hit:
                continue
            qid, title = hit
            meta = qmeta.get(qid)
            if not meta or not meta.get("is_bio"):
                continue  # disambiguation page, person, place, etc.
            same_taxon = r["name"] in meta["p225"] and (not meta["p685"] or tid in meta["p685"])
            if same_taxon:
                # Article is about this exact taxon (title lookup found it although Wikidata lacked a sitelink)
                r.update(status="linked", match="scientific_name", en_title=title, qid=r["qid"] or qid,
                         swiki=max(r["swiki"], meta["swiki"]))
                if not r["p1843"]:
                    r["p1843"] = sorted(set(meta["p1843"]))
                if not r["p225"]:
                    r["p225"] = sorted(meta["p225"])
            elif r["name"] in meta["p225"]:
                continue  # same spelling, different NCBI taxon -> homonym page about another organism
            elif meta["p685"] and is_lineage_related(tid, meta["p685"], parent):
                # Wikipedia merges this clade into a related taxon's article. Link the page, but keep
                # common names restricted to the exact item (Step 6 ignores redirect targets).
                r.update(status="linked", match="enwiki_redirect", en_title=title,
                         redirect_qid=qid)

    # ---- Commit results: anything not linked and not errored is a confirmed "no article" ----
    linked = no_article = 0
    for tid, r in pending.items():
        if tid in errored:
            prev = tree_cache.get(tid)
            # Keep a previously good record if the node name is unchanged; otherwise mark for retry.
            if not (prev and prev.get("name") == r["name"] and prev.get("status") == "linked"):
                tree_cache[tid] = {"name": r["name"], "rank": r["rank"], "status": "error",
                                   "resolver_version": TREE_RESOLVER_VERSION}
            continue
        if r["status"] != "linked":
            r["status"] = "no_article"
            no_article += 1
        else:
            linked += 1
        tree_cache[tid] = r
    save_tree_cache(tree_cache)
    print(f"Step 5 complete: {linked:,} linked, {no_article:,} without an English article, "
          f"{len(errored):,} network errors (will retry next run).")

# ---------------- Step 6: common names ----------------------------------------------

NCBI_COMMON_CLASSES = ("genbank common name", "common name", "blast name")
# Endings that mark a single word as a Latin taxon name rather than an English vernacular
_LATIN_SUFFIX_RE = re.compile(
    r"(idae|inae|ini|oidea|iformes|formes|ales|aceae|phyta|mycota|opsida|phyceae|mycetes|"
    r"morpha|ia|ida|oda|ota|ata|ea|ae|es|us|um|i)$", re.I)

def scan_ncbi_names(taxdump_path, taxids=None, lookup_strings=None):
    """One pass over names.dmp inside taxdump.tar.gz (no extraction to disk).
    Returns:
      common: {taxid: {name_class: first_name}} for NCBI_COMMON_CLASSES, restricted to `taxids`
      sci_hits: subset of `lookup_strings` that NCBI lists as a scientific name / synonym of any taxon
    """
    common, sci_hits = {}, set()
    if not os.path.exists(taxdump_path):
        print(f"  NCBI taxdump not found at {taxdump_path}; NCBI common names unavailable.")
        return common, sci_hits
    lookup_lower = {s.lower(): s for s in (lookup_strings or ())}
    with tarfile.open(taxdump_path, "r:gz") as tar:
        fh = tar.extractfile("names.dmp")
        for raw in fh:
            parts = raw.decode("utf-8", errors="ignore").split("\t|\t")
            if len(parts) < 4:
                continue
            tid, name, name_class = parts[0], parts[1], parts[3].rstrip("\t|\n")
            if taxids is not None and tid in taxids and name_class in NCBI_COMMON_CLASSES:
                common.setdefault(tid, {}).setdefault(name_class, name)
            if lookup_lower and name_class not in NCBI_COMMON_CLASSES and name.lower() in lookup_lower:
                sci_hits.add(lookup_lower[name.lower()])
    return common, sci_hits

def strip_disambiguator(title):
    """'Drum (fish)' -> 'Drum'."""
    return re.sub(r"\s*\([^)]*\)\s*$", "", title or "").strip()

def looks_scientific(title, known_scientific):
    """Decide whether an article title is a scientific name rather than an English vernacular."""
    t = strip_disambiguator(title)
    if not t or t in known_scientific:
        return True
    # Common English vernaculars that end in Latin-like suffixes
    if t.lower() in ("fungus", "virus", "citrus", "crocus", "octopus", "platypus", "walrus", "asparagus", "hibiscus", "eucalyptus"):
        return False
    # Single capitalized word with a Latin taxon ending, e.g. 'Osteichthyes', 'Hominidae'
    return (" " not in t) and bool(_LATIN_SUFFIX_RE.search(t))

def sentence_case(s):
    """Capitalize only the first letter; keep the source's casing otherwise ('ray-finned fishes' -> 'Ray-finned fishes')."""
    s = (s or "").strip()
    return s[:1].upper() + s[1:] if s else s

def pick_common_name(rec, ncbi_entry, known_scientific):
    """Return (common_name, source) for one tree node from sourced candidates only, or ("", None).
    rec: Step 5 cache record. ncbi_entry: {name_class: name} from names.dmp for this taxid."""
    name = (rec.get("name") or "").strip()

    def acceptable(c):
        return c and c.strip().lower() != name.lower()

    # 1. Wikidata P1843 on the exact item (never taken from a redirect target)
    p1843 = [tuple(x) for x in rec.get("p1843") or []]
    if p1843:
        # Plain 'en' before regional variants, then shortest, then alphabetical (deterministic)
        p1843.sort(key=lambda tl: (tl[1].lower() != "en", len(tl[0]), tl[0].lower()))
        for text, _lang in p1843:
            if acceptable(text):
                return sentence_case(text), "wikidata_P1843"

    # 2. Vernacular article title of the exact taxon (Aves -> 'Bird')
    if rec.get("status") == "linked" and rec.get("match") in ("ncbi_taxid", "scientific_name"):
        title = strip_disambiguator(rec.get("en_title"))
        p225 = set(rec.get("p225") or [])
        if acceptable(title) and title not in p225 and not looks_scientific(title, known_scientific):
            return sentence_case(title), "enwiki_title"

    # 3. NCBI curated names for this exact taxid
    for cls, label in (("genbank common name", "ncbi_genbank"),
                       ("common name", "ncbi_common"),
                       ("blast name", "ncbi_blast")):
        cand = (ncbi_entry or {}).get(cls)
        if acceptable(cand):
            return sentence_case(cand), label
    return "", None

def step6_resolve_common_names(tree, tree_cache):
    """Step 6: compute common_name + source for every non-species node (offline, from caches)."""
    print("\nStep 6: Resolving common names from Wikidata / Wikipedia / NCBI...")
    t0 = time.time()
    target_taxids = {tid for tid, n in tree["nodes"].items() if n.get("rank") != "Species"}
    candidate_titles = {strip_disambiguator(r["en_title"]) for r in tree_cache.values()
                        if r.get("en_title")}
    ncbi_common, ncbi_sci_hits = scan_ncbi_names(TAXDUMP_PATH, target_taxids, candidate_titles)
    # Titles that are themselves taxon names anywhere in our tree are scientific too
    known_scientific = ncbi_sci_hits | {n.get("name", "") for n in tree["nodes"].values()}

    results, by_source = {}, {}
    for tid in target_taxids:
        node = tree["nodes"][tid]
        rec = tree_cache.get(tid) or {"name": node.get("name", "")}
        if rec.get("name") != node.get("name"):
            rec = {"name": node.get("name", "")}  # stale record (tree rebuilt): NCBI-only until Step 5 reruns
        common, source = pick_common_name(rec, ncbi_common.get(tid), known_scientific)
        if common:
            results[tid] = (common, source)
            by_source[source] = by_source.get(source, 0) + 1
    print(f"Step 6 complete in {time.time() - t0:.1f}s: {len(results):,}/{len(target_taxids):,} "
          f"non-species nodes have a common name. By source: {by_source}")
    return results

# ---------------- Step 7: export ----------------------------------------------------

def step7_export(tree, tree_cache, common_names, popularity_cache, dry_run=False):
    """Step 7: write wiki_title / common_name onto tree nodes and regenerate clade_common_names.json.

    Fields written (stale values from earlier runs are always cleared first):
      non-species nodes: wiki_title (if linked), common_name (if resolved)
      species nodes:     wiki_title from Step 2's canonical enwiki title (if known)
    """
    print("\nStep 7: Exporting to phylogeny_tree.json and clade_common_names.json...")
    linked = commons = species_titles = 0
    clade_map, clashes = {}, set()

    # Pre-seed with foundational clade names so baseline game definitions (e.g. animalia, plantae, fungi, actinopteri) are never lost
    foundational_path = os.path.join(BASE_DIR, "data", "foundational_clade_common_names.json")
    if os.path.exists(foundational_path):
        try:
            with open(foundational_path, "r", encoding="utf-8") as f:
                clade_map.update(json.load(f))
        except Exception:
            pass
    elif os.path.exists(CLADE_COMMON_PATH):
        try:
            with open(CLADE_COMMON_PATH, "r", encoding="utf-8") as f:
                clade_map.update(json.load(f))
        except Exception:
            pass

    seen_taxa_by_name = {}
    for tid, node in tree["nodes"].items():
        node.pop("wiki_title", None)
        node.pop("common_name", None)
        name = node.get("name", "")
        if node.get("rank") == "Species":
            title = (popularity_cache.get(name) or {}).get("en_title")
            if title:
                node["wiki_title"] = title
                species_titles += 1
            continue
        rec = tree_cache.get(tid)
        if rec and rec.get("name") == name and rec.get("status") == "linked" and rec.get("en_title"):
            node["wiki_title"] = rec["en_title"]
            linked += 1
        if tid in common_names:
            node["common_name"] = common_names[tid][0]
            commons += 1
            key = name.lower()
            # Homonym clash: two distinct phylogenetic nodes sharing the exact same name
            if key in seen_taxa_by_name and seen_taxa_by_name[key] != tid and clade_map.get(key) != node["common_name"]:
                clashes.add(key)
            else:
                seen_taxa_by_name[key] = tid
                clade_map[key] = node["common_name"]

            # If node represents a major rank, map major_name too (e.g. Metazoa -> Animalia)
            major = (node.get("major_name") or "").strip()
            if major:
                mkey = major.lower()
                if mkey not in clade_map or mkey == key:
                    clade_map[mkey] = node["common_name"]

    for key in clashes:
        clade_map.pop(key, None)

    print(f"  Non-species nodes linked to Wikipedia: {linked:,}")
    print(f"  Non-species nodes with common names:   {commons:,}")
    print(f"  Species nodes with canonical titles:   {species_titles:,}")
    print(f"  clade_common_names.json entries:       {len(clade_map):,} ({len(clashes)} homonym clashes dropped)")
    if dry_run:
        print("  --dry-run: not writing files.")
        return
    save_tree_formatted(TREE_PATH, tree)
    with open(CLADE_COMMON_PATH, "w", encoding="utf-8") as f:
        json.dump(dict(sorted(clade_map.items())), f, indent=2, ensure_ascii=False)
    print(f"  Wrote {TREE_PATH}\n  Wrote {CLADE_COMMON_PATH}")

def run_tree_stages(args, popularity_cache):
    if not os.path.exists(TREE_PATH):
        print(f"Error: tree not found at {TREE_PATH}")
        sys.exit(1)
    with open(TREE_PATH, "r", encoding="utf-8") as f:
        tree = json.load(f)
    tree_cache = {} if args.refresh_tree else load_tree_cache()
    print(f"\nLoaded {len(tree['nodes']):,} tree nodes; {len(tree_cache):,} cached node links")
    if args.offline:
        print("\nStep 5: --offline, using cached links only.")
    else:
        step5_link_tree_nodes(tree, tree_cache, args.recheck_missing, args.max_tree_batches)
    common_names = step6_resolve_common_names(tree, tree_cache)
    step7_export(tree, tree_cache, common_names, popularity_cache, args.dry_run)


# ==============================================================================
# ENTRY POINT
# ==============================================================================

def parse_args(argv=None):
    p = argparse.ArgumentParser(description="Phylogenle Wikimedia taxonomy pipeline (see module docstring).")
    p.add_argument("--csv-only", action="store_true", help="Only Step 4 (rebuild ranking CSVs from cache).")
    p.add_argument("--rediscover-subspecies", action="store_true", help="Force Step 2B even if cached.")
    p.add_argument("--skip-tree", action="store_true", help="Run Steps 1-4 only.")
    p.add_argument("--tree-only", action="store_true", help="Run Steps 5-7 only.")
    p.add_argument("--offline", action="store_true",
                   help="No network: skip Steps 1-3 and 5, rebuild Step 4/6/7 outputs from caches.")
    p.add_argument("--recheck-missing", action="store_true",
                   help="Step 5: re-query nodes previously confirmed to have no English article.")
    p.add_argument("--refresh-tree", action="store_true", help="Step 5: ignore tree cache and re-resolve every node.")
    p.add_argument("--max-tree-batches", type=int, default=0,
                   help=f"Step 5: only process N batches of {TREE_SPARQL_BATCH} nodes (0 = all).")
    p.add_argument("--dry-run", action="store_true", help="Step 7: don't write tree / clade_common_names.json.")
    return p.parse_args(argv)

def main(argv=None):
    args = parse_args(argv)
    print("=" * 70)
    print("🧬 Phylogenle: Wikimedia Taxonomy Pipeline")
    print("=" * 70)

    if not os.path.exists(CATALOG_PATH):
        print(f"Error: Catalog not found at {CATALOG_PATH}")
        sys.exit(1)

    with open(CATALOG_PATH, "r", encoding="utf-8") as f:
        species_data = json.load(f)

    total_species = len(species_data)
    print(f"Loaded {total_species:,} species records from {CATALOG_PATH}")

    cache = load_cache()
    print(f"Loaded {len(cache):,} species records from cache")

    # --csv-only fast mode (used by harvest_and_audit_species_aliases.py)
    if args.csv_only:
        print("\n[--csv-only mode]: Skipping network harvesting and compiling CSVs directly from cache & aliases...")
        compile_ranking_csvs(species_data, cache)
        return

    if not args.tree_only:
        if args.offline:
            print("\n--offline: skipping network Steps 1-3.")
        else:
            step1_resolve_wikidata_sitelinks(species_data, cache)
            step2_resolve_canonical_titles(species_data, cache)
            step2b_discover_extra_articles(species_data, cache, args.rediscover_subspecies)
            step3_fetch_pageviews(species_data, cache)
        compile_ranking_csvs(species_data, cache)

    if not args.skip_tree:
        run_tree_stages(args, cache)

if __name__ == "__main__":
    main()

