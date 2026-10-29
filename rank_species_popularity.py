#!/usr/bin/env python3
"""
Phylogenle - Phase 1A: Empirical Wikimedia Popularity Harvester & Ranker
Harvests Wikidata global sitelinks (Swiki) and English Wikipedia monthly pageviews (Vwiki)
for all organisms in the master catalog.
Outputs independent ranking review documents for hyperparameter calibration.
Deduplicates by primary biological ID (scientific name) and collects alternate names as aliases.
"""

import os
import sys
import json
import time
import csv
import re
import urllib.request
import urllib.parse
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CATALOG_PATH = os.path.join(BASE_DIR, "data", "species_taxonomy_catalog.json")
CACHE_PATH = os.path.join(BASE_DIR, "data", "wikimedia_popularity_cache.json")
ALIASES_PATH = os.path.join(BASE_DIR, "data", "species_aliases.json")
DOCS_DIR = os.path.join(BASE_DIR, "docs")
CSV_PATH = os.path.join(DOCS_DIR, "species_popularity_rankings.csv")
SWIKI_CSV_PATH = os.path.join(DOCS_DIR, "species_ranking_by_swiki.csv")
VWIKI_CSV_PATH = os.path.join(DOCS_DIR, "species_ranking_by_vwiki.csv")

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

def query_wikidata_sitelinks_by_qids(qids):
    """Query wbgetentities for a list of QIDs to get their sitelink counts."""
    if not qids:
        return {}
    results = {}
    for i in range(0, len(qids), 50):
        chunk = qids[i:i + 50]
        url = f"https://www.wikidata.org/w/api.php?action=wbgetentities&ids={'|'.join(chunk)}&props=sitelinks&format=json"
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                data_json = json.loads(resp.read().decode("utf-8"))
                for qid, ent in data_json.get("entities", {}).items():
                    sitelinks = ent.get("sitelinks", {})
                    en_title = sitelinks.get("enwiki", {}).get("title")
                    results[qid] = {
                        "swiki": len(sitelinks),
                        "en_title": en_title,
                    }
        except Exception as e:
            print(f"  QID sitelinks error: {e}")
    return results

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

def main():
    print("=" * 70)
    print("🧬 Phylogenle: Phase 1A Wikimedia Popularity Harvester")
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

    # Step 1: Query Wikidata for Swiki and en_title (only for uncached species OR species where qid is None)
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

    # Step 2: Fallback lookup for species missing en_title
    needs_fallback = [
        s for s in species_data
        if not cache.get(s["scientific"], {}).get("en_title")
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
                c = s.get("common", "").strip()
                sci = s.get("scientific", "").strip()
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

            resolved_map = query_enwiki_fallback_batch(titles_to_check)
            if resolved_map:
                qids_to_query = list(set(qid for qid, _ in resolved_map.values() if qid))
                qid_data = query_wikidata_sitelinks_by_qids(qids_to_query) if qids_to_query else {}
                for s in batch:
                    sci = s["scientific"]
                    best_qid = None
                    best_swiki = cache.get(sci, {}).get("swiki", 0)
                    best_title = cache.get(sci, {}).get("en_title")
                    for t in sci_to_titles[sci]:
                        if t in resolved_map:
                            qid, can_title = resolved_map[t]
                            s_count = qid_data.get(qid, {}).get("swiki", 0) if qid else 0
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

            processed = min(i + FB_BATCH, len(needs_fallback))
            if (i // FB_BATCH) % 10 == 0 or processed == len(needs_fallback):
                print_progress(processed, len(needs_fallback), prefix="Resolving Fallbacks")
                save_cache(cache)
            time.sleep(0.2)
        save_cache(cache)
        print("\nStep 2 complete. All redirects and canonical articles resolved.")
    else:
        print("\nStep 2: All canonical titles already resolved. Skipping.")

    # Step 2B: Option B - Discover Exclusive Standalone Articles (Cultivars, Subspecies & Domestic Forms)
    print("\nStep 2B: Option B - Discovering exclusive standalone articles (cultivars, subspecies)...")
    
    # Precompute umbrella words & polytypic genera/families
    polytypic_genera = set()
    polytypic_families = set()
    genus_counts = {}
    family_counts = {}
    for s in species_data:
        g = s.get("genus", "").lower()
        fam = s.get("family", "").lower()
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
    catalog_commons_lower = set(s.get("common", "").lower() for s in species_data if s.get("common"))

    # Map aliases to species
    alias_to_sci = {}
    if os.path.exists(ALIASES_PATH):
        with open(ALIASES_PATH, "r", encoding="utf-8") as f:
            raw_aliases = json.load(f)
        for a, target in raw_aliases.items():
            m = re.search(r"\(([^)]+)\)$", target)
            sci = m.group(1).strip() if m else target.strip()
            comm = target[:m.start()].strip() if m else ""
            if a.lower() == sci.lower() or a.lower() == comm.lower() or "(" in a:
                continue
            clean_a = a.strip()
            clean_lower = clean_a.lower()
            if clean_lower not in alias_to_sci:
                alias_to_sci[clean_lower] = sci

    # Canonical article overrides for domestic & high-profile organisms where Wikidata SPARQL returned redirects or split taxa
    CANONICAL_OVERRIDES = {
        "Canis lupus familiaris": "Dog",
        "Felis catus": "Cat",
        "Vicugna pacos": "Alpaca",
        "Sphenodon punctatus": "Tuatara",
        "Lithobates catesbeianus": "American bullfrog",
        "Cebuella pygmaea": "Pygmy marmoset",
        "Homo sapiens": "Human",
        "Meleagris gallopavo": "Wild turkey",
        "Bufo bufo": "Common toad",
        "Bradypus tridactylus": "Pale-throated sloth",
        "Canis lupus dingo": "Dingo",
        # Special Genuses
        "Giraffa": "Giraffe",
        "Gorilla": "Gorilla",
        "Pongo": "Orangutan",
        "Latimeria": "Coelacanth",
        "Chinchilla": "Chinchilla",
        "Papio": "Baboon",
        "Arapaima": "Arapaima",
        # Individual Species (True species-level articles)
        "Giraffa camelopardalis": "Northern giraffe",
        "Gorilla gorilla": "Western gorilla",
        "Pongo pygmaeus": "Bornean orangutan",
        "Latimeria chalumnae": "West Indian Ocean coelacanth",
        "Chinchilla lanigera": "Long-tailed chinchilla",
        "Papio anubis": "Olive baboon",
        "Arapaima gigas": "Arapaima gigas",
    }
    for o_sci, o_target in CANONICAL_OVERRIDES.items():
        if o_sci in cache and cache[o_sci].get("en_title") != o_target:
            cache[o_sci]["en_title"] = o_target
            cache[o_sci]["vwiki_period"] = None

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
        if is_umbrella(target): continue
        if target in catalog_scis or target.lower() in catalog_commons_lower:
            continue
        candidates.append((sci, prim, a, target, qid))
        qids_to_query.append(qid)

    # Query Wikidata for P31 and P105
    VALID_P31 = {"Q16521", "Q23038290", "Q767728", "Q4886", "Q15926588", "Q11004", "Q55983715", "Q207106", "Q146"}
    HIGHER_RANKS = {"Q35409", "Q36732", "Q38348", "Q16428", "Q2455704", "Q34740"}
    valid_qids = set()
    for i in range(0, len(qids_to_query), 50):
        chunk = qids_to_query[i:i+50]
        url = "https://www.wikidata.org/w/api.php?action=wbgetentities&ids=" + "|".join(chunk) + "&props=claims&format=json"
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                for q, ent in data.get("entities", {}).items():
                    claims = ent.get("claims", {})
                    p31 = set(c.get("mainsnak", {}).get("datavalue", {}).get("value", {}).get("id") for c in claims.get("P31", []))
                    p105 = set(c.get("mainsnak", {}).get("datavalue", {}).get("value", {}).get("id") for c in claims.get("P105", []))
                    if q in ("Q5", "Q146") or ((p31 & VALID_P31) and not (p105 & HIGHER_RANKS)):
                        valid_qids.add(q)
        except Exception as e:
            print(f"  Wikidata rank check error: {e}")

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

    # Step 3: Fetch Wikipedia cumulative pageviews (Vwiki)
    # Target species that don't have current period data OR have suspicious/falsely low views (<= 10)
    print(f"\nStep 3: Checking Wikipedia {DATE_LABEL} cumulative pageviews (Vwiki)...")
    need_views = []
    for s in species_data:
        sci = s["scientific"]
        rec = cache.get(sci, {})
        en_title = rec.get("en_title")
        if en_title:
            is_suspicious_views = (rec.get("vwiki", 0) <= 10)
            is_missing_period = (rec.get("vwiki_period") != CACHE_PERIOD_KEY)
            if is_suspicious_views or is_missing_period:
                need_views.append((sci, en_title, False))
        else:
            if rec.get("vwiki", 0) != 0:
                rec["vwiki"] = 0
        for extra_t, eviews in rec.get("extra_articles", {}).items():
            if eviews <= 10 or rec.get("vwiki_period") != CACHE_PERIOD_KEY:
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

    # Step 4: Deduplicate Catalog by Scientific Name & Output Comprehensive CSV Documents
    print("\nStep 4: Deduplicating by primary species ID and compiling ranking CSV documents...")

    # Load alternative common name aliases from data/species_aliases.json
    sci_to_aliases = {}
    if os.path.exists(ALIASES_PATH):
        with open(ALIASES_PATH, "r", encoding="utf-8") as f:
            raw_aliases = json.load(f)
        for alias_key, canonical_target in raw_aliases.items():
            m = re.search(r"\(([^)]+)\)$", canonical_target)
            if m:
                target_sci = m.group(1).strip()
                target_comm = canonical_target[:m.start()].strip()
            else:
                target_sci = canonical_target.strip()
                target_comm = ""

            clean_a = alias_key.strip()
            # Skip if alias matches scientific name or primary common name
            if clean_a.lower() == target_sci.lower() or clean_a.lower() == target_comm.lower():
                continue
            # Skip formatted display strings with parentheses
            if "(" in clean_a or ")" in clean_a:
                continue
            
            clean_formatted = clean_a.title()
            if target_sci not in sci_to_aliases:
                sci_to_aliases[target_sci] = set()
            sci_to_aliases[target_sci].add(clean_formatted)

    # Group catalog entries by scientific name to eliminate duplicate common name rows
    species_by_sci = {}
    for s in species_data:
        sci = s["scientific"]
        comm = s.get("common", "").strip()
        if sci not in species_by_sci:
            species_by_sci[sci] = {
                "common": comm,
                "all_commons": set([comm]) if comm else set(),
                "scientific": sci,
                "kingdom": s.get("kingdom", ""),
                "class": s.get("class", ""),
                "order": s.get("order", ""),
                "family": s.get("family", ""),
            }
        else:
            if comm:
                species_by_sci[sci]["all_commons"].add(comm)
                curr = species_by_sci[sci]["common"]
                # Keep shorter or more concise common name as primary
                if not curr or len(comm) < len(curr):
                    species_by_sci[sci]["common"] = comm

    print(f"Aggregated {total_species:,} catalog entries into {len(species_by_sci):,} unique biological species.")

    all_ranked = []
    for sci, s in species_by_sci.items():
        rec = cache.get(sci, {})
        combined_aliases = set(s["all_commons"])
        combined_aliases.discard(s["common"])
        if sci in sci_to_aliases:
            combined_aliases.update(sci_to_aliases[sci])
        aliases_list = sorted(list(combined_aliases))
        aliases_str = "; ".join(aliases_list)

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

        all_ranked.append({
            "common": s["common"],
            "scientific": sci,
            "aliases": aliases_str,
            "kingdom": s["kingdom"],
            "class": s["class"],
            "order": s["order"],
            "family": s["family"],
            "swiki": rec.get("swiki", 0),
            "vwiki": total_vwiki,
            "en_title": full_title,
        })

    # Filter out entries with <= 1 language or <= 1 pageview, and blank titles
    # 1. By Swiki: Species with established cross-language presence and verified English article (Swiki > 1 and Vwiki > 1)
    by_swiki = sorted(
        [item for item in all_ranked if item.get("swiki", 0) > 1 and item.get("vwiki", 0) > 1 and bool(item.get("en_title", "").strip())],
        key=lambda x: (x["swiki"], x["vwiki"], x["common"]),
        reverse=True
    )
    swiki_ranks = {item["scientific"]: r + 1 for r, item in enumerate(by_swiki)}

    # 2. By Vwiki: Species with verified English Wikipedia articles and traffic (Vwiki > 1, Swiki > 1, and non-blank title)
    by_vwiki = sorted(
        [item for item in all_ranked if item.get("vwiki", 0) > 1 and item.get("swiki", 0) > 1 and bool(item.get("en_title", "").strip())],
        key=lambda x: (x["vwiki"], x["swiki"], x["common"]),
        reverse=True
    )
    vwiki_ranks = {item["scientific"]: r + 1 for r, item in enumerate(by_vwiki)}

    # 3. Combined: Species with verified presence in both metrics (Swiki > 1 and Vwiki > 1)
    combined_candidates = [
        item for item in all_ranked
        if item.get("swiki", 0) > 1 and item.get("vwiki", 0) > 1 and bool(item.get("en_title", "").strip())
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

if __name__ == "__main__":
    main()
