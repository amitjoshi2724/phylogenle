# 🧬 Architecture & Operations: `rank_species_popularity.py`

> **Document Version:** 1.0  
> **Target Audience:** Core Contributors & Maintainers  
> **Script Path:** [`rank_species_popularity.py`](file:///Users/amitjoshi2724/Desktop/phylogenle/rank_species_popularity.py)  
> **Last Updated:** 2026-10-30  

---

## 1. Executive Summary & Purpose

In **Phylogenle**, players deduce an unknown daily mystery organism by exploring evolutionary divergence points on a phylogenetic tree. To ensure the game is fun and accessible, organisms are sorted into difficulty tiers:
- 🐾 **Easy Tier** (Top 1,000 most recognizable organisms)
- 🌿 **Normal Tier** (Ranks 1,001 – 2,000)
- 🔬 **Advanced Tier** (Ranks 2,001 – 5,000)
- ⚡ **Master Tier** (Ranks 5,001 – 26,000+)

Without empirical popularity data, an obscure deep-sea polychaete worm or soil bacterium would have the exact same likelihood of appearing in Easy Tier as a Tiger, Blue Whale, or Giant Sequoia.

`rank_species_popularity.py` is the **Phase 1A Empirical Harvester & Ranker**. It harvests two independent empirical signals for every organism in the master catalog ([`data/species_taxonomy_catalog.json`](file:///Users/amitjoshi2724/Desktop/phylogenle/data/species_taxonomy_catalog.json)):

1. **$S_{\text{wiki}}$ (Wikidata Sitelinks):** The total number of different language Wikipedia editions that have dedicated an article to this organism (a measure of global, cross-cultural recognition).
2. **$V_{\text{wiki}}$ (English Wikipedia Pageviews):** The cumulative human traffic (monthly granularity over a multi-year window, currently **2025–2026**) across English Wikipedia.

It then deduplicates entries by primary biological species ID (scientific name), rolls up domestic forms and subspecies, and exports three comprehensive ranking documents to [`docs/`](file:///Users/amitjoshi2724/Desktop/phylogenle/docs/).

---

## 2. The "Only Do What Needs to Be Done" Philosophy

Running API queries across **26,320+ species** against Wikimedia’s public infrastructure from scratch would take **hours** and quickly trigger rate-limits (HTTP 429) if not carefully engineered.

The script operates on an **Incremental Delta Engine** backed by a persistent cache ([`data/wikimedia_popularity_cache.json`](file:///Users/amitjoshi2724/Desktop/phylogenle/data/wikimedia_popularity_cache.json)). When you run the script, it evaluates every step against the existing cache and skips any work that has already been verified.

```mermaid
flowchart TD
    Start([Run rank_species_popularity.py]) --> Load[Load Catalog & Local Cache]
    Load --> S1Check{Any species missing<br/>QID or Swiki?}
    S1Check -- Yes --> S1[Step 1: Batch Wikidata SPARQL<br/>Query ONLY uncached]
    S1Check -- No --> S1Skip[Step 1: SKIP - All resolved]
    
    S1 --> S2Check{Any species missing<br/>canonical verified title?}
    S1Skip --> S2Check
    
    S2Check -- Yes --> S2[Step 2: EnWiki Fallback & Redirects<br/>Query ONLY unverified]
    S2Check -- No --> S2Skip[Step 2: SKIP - All resolved]
    
    S2 --> S2B[Step 2B: Discover Cultivars & Subspecies<br/>Rollup traffic via aliases]
    S2Skip --> S2B
    
    S2B --> S3Check{Any article where<br/>vwiki_period != CURRENT?}
    S3Check -- Yes --> S3[Step 3: Threaded REST Pageviews<br/>Fetch ONLY stale or new titles]
    S3Check -- No --> S3Skip[Step 3: SKIP - All pageviews valid]
    
    S3 --> S4[Step 4: Deduplicate by Scientific ID,<br/>Sum Views & Generate CSVs]
    S3Skip --> S4
    S4 --> End([Done! Outputs updated])
```

### 2.1 The Cache Data Schema
Every organism entry in [`data/wikimedia_popularity_cache.json`](file:///Users/amitjoshi2724/Desktop/phylogenle/data/wikimedia_popularity_cache.json) contains:
```json
"Panthera tigris": {
  "common": "Tiger",
  "scientific": "Panthera tigris",
  "kingdom": "Animalia",
  "class": "Mammalia",
  "order": "Carnivora",
  "family": "Felidae",
  "qid": "Q19939",
  "swiki": 196,
  "en_title": "Tiger",
  "canonical_verified": true,
  "vwiki": 6542100,
  "vwiki_period": "vwiki_20250101_20261231",
  "extra_articles": {
    "Bengal tiger": 1243100,
    "Siberian tiger": 951000
  }
}
```

### 2.2 Delta Filtering Criteria per Step
| Step | What Triggers Work? | Filter Logic in Code |
| :--- | :--- | :--- |
| **Step 1 (Wikidata SPARQL)** | Species not in cache, or `qid is None`, or missing `swiki`. | `s["scientific"] not in cache or cache[s["scientific"]].get("qid") is None or "swiki" not in cache[s["scientific"]]` |
| **Step 2 (Wikipedia Canonical)** | Species has no `en_title` or has not been `canonical_verified`. | `not cache.get(s["scientific"], {}).get("en_title") or not cache.get(s["scientific"], {}).get("canonical_verified")` |
| **Step 3 (Wikimedia Pageviews)** | Article has `vwiki_period != CACHE_PERIOD_KEY` or `vwiki == 0` on an un-queried title. | `rec.get("vwiki_period") != CACHE_PERIOD_KEY` |

### 2.3 Automatic Invalidation Hooks
If Step 2 detects that an organism's article was renamed or redirected to a better canonical title (for example, from a scientific synonym to an English common name):
```python
if best_title != cache[sci].get("en_title"):
    cache[sci]["en_title"] = best_title
    cache[sci]["vwiki_period"] = None  # Immediately invalidates cached views!
```
By setting `vwiki_period = None`, Step 3 will automatically harvest pageviews for the new article title during the very next run.

### 2.4 Cache Poisoning Defense
If a network disconnect, socket timeout, or 503 service error occurs during traffic fetching:
- The script retries up to **6 times** with exponential backoff (`2^attempt` seconds).
- If all 6 attempts fail, the helper returns `(title, None)`.
- The harvester checks `if views is not None:`. If it is `None`, **it does NOT write `views = 0` to the cache** and does NOT set `vwiki_period`. This prevents transient network glitches from permanently poisoning high-popularity animals with zero views.

### 2.5 Periodic Checkpointing
Every 200 fetched articles and at the completion of every batch, `save_cache(cache)` writes directly to disk. If the script is interrupted (Ctrl+C, power loss), zero progress is lost—restarting picks up exactly where it left off.

---

## 3. End-to-End Pipeline Walkthrough

### Step 1: High-Speed Wikidata SPARQL Harvesting
- **Objective:** Map each scientific name to its Wikidata entity (`qid`), count cross-wiki sitelinks (`swiki`), and find the English Wikipedia article (`en_title`).
- **Optimization:** Instead of querying 26,000 species one by one, species are chunked into **batches of 120 names** and sent via HTTP `POST` to the Wikidata SPARQL endpoint (`https://query.wikidata.org/sparql`):
  ```sparql
  SELECT ?scientificName ?item ?sitelinks ?enTitle WHERE {
    VALUES ?scientificName { "Panthera leo" "Homo sapiens" "Tyto alba" ... }
    ?item wdt:P225 ?scientificName .
    ?item wikibase:sitelinks ?sitelinks .
    OPTIONAL {
      ?article schema:about ?item ;
               schema:isPartOf <https://en.wikipedia.org/> ;
               schema:name ?enTitle .
    }
  }
  ```
- **Sitelink Tie-Breaking:** If multiple Wikidata entities exist for the same scientific name (e.g., historical duplicates or synonym entries), the script keeps the entity with the highest sitelink count.

---

### Step 2: English Wikipedia Fallback & Redirect Resolution
- **Objective:** Resolve organisms where Wikidata has no direct English article linked, or where the scientific name redirects to a common English article (e.g., *Canis lupus* $\rightarrow$ *Wolf*).
- **Batching & Chunking:** Sends up to 35 candidates per batch to the MediaWiki API (`en.wikipedia.org/w/api.php?action=query&prop=pageprops&redirects=1`) to strictly honor Wikimedia's 50-title request limit.
- **Linguistic Variations Tested:**
  1. Primary English common name (e.g., `"Sand dollar"`)
  2. Sentence-cased variants (e.g., `"Sand Dollar"` vs `"Sand dollar"`)
  3. Hyphenated vs unhyphenated variations
  4. Scientific name and Latin declension variants (e.g., endings in `-us`, `-a`, `-ii`, `-i`)
- **Canonical Multi-Hop Following:** MediaWiki returns `normalized` and `redirects` arrays. The code walks the redirect chain up to 5 hops to discover the true final canonical article title and its `wikibase_item` QID.
- **Wikidata Sitelink Enrichment:** For any newly resolved QIDs, it calls `wbgetentities` to update their sitelink count.

---

### Step 2B: Option B — Cultivar, Subspecies & Domestic Form Rollup
- **The Biological Dilemma:** In everyday language, people read about *"Domestic dog"* (subspecies *Canis lupus familiaris*), *"Broccoli"* (cultivar of *Brassica oleracea*), or *"Bengal tiger"* (subspecies *Panthera tigris tigris*). If we strictly counted the species-level article alone, these world-famous organisms would appear artificially deflated in popularity.
- **The Solution:** Discover standalone articles for subspecies and domestic forms and add their traffic into the species' total score (`extra_articles`).
- **Strict Guardrails to Prevent Parasitic Traffic Hijacking:**
  1. **Umbrella Word Filtering:** Over 70 broad category names (e.g., *bird*, *fish*, *shark*, *frog*, *owl*, *beetle*, *flower*) are blacklisted.
  2. **Polytypic Genus/Family Filtering:** Any genus or family with more than 1 species in the catalog is barred from being claimed by any single species.
  3. **Wikidata Rank Verification:** The candidate article must have Wikidata claims:
     - Must be an instance of (`P31`) a biological taxon, domestic breed, or cultivar (`Q16521`, `Q23038290`, `Q767728`, `Q4886`, etc.).
     - Must **NOT** have a taxon rank (`P105`) of genus, family, order, or class (`Q35409`, `Q36732`, `Q38348`, etc.).
- **Result:** High-traffic subspecies are credited to their parent species without corrupting higher-order taxonomy.

---

### Step 3: High-Throughput Asynchronous Pageview Harvesting
- **Endpoint:** `https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/en.wikipedia.org/all-access/all-agents/{title}/monthly/{start_date}/{end_date}`
- **Title Inversion & Deduplication:** Multiple species or aliases might reference the same Wikipedia article. The script groups species by unique Wikipedia title so each Wikipedia URL is queried **exactly once**.
- **Concurrency & Rate-Limiting:**
  - Uses `ThreadPoolExecutor(max_workers=10)` (conservative pool to respect Wikimedia's REST API limits).
  - Exponential backoff on HTTP 429 (Too Many Requests), 502, and 503.
- **Live Terminal Telemetry:** Displays a real-time progress bar with request rate (req/s) and calculated dynamic ETA:
  ```text
  Fetching Views (2025–2026): [██████████████████░░░░░░░░░░░░] 14,200/22,810 ( 62.3%) | 9.8 req/s | ETA: 14m 38s
  ```

---

### Step 4: Biological Deduplication & Ranking Compilation
- **Deduplication by Scientific Name:** The taxonomic catalog contains alternate common names that point to the exact same biological species. The script aggregates all catalog entries by `scientific`:
  - Chooses the cleanest/shortest common name as the primary display label.
  - Collates all alternate names from both the catalog and [`data/species_aliases.json`](file:///Users/amitjoshi2724/Desktop/phylogenle/data/species_aliases.json) into a clean, semicolon-separated `aliases` string.
- **Metric Aggregation:**
  $$\text{Total } V_{\text{wiki}} = V_{\text{base}} + \sum V_{\text{extra\_articles}}$$
- **Filtering Quality Bar:**
  - Requires $S_{\text{wiki}} > 1$ (present in at least 2 global languages).
  - Requires $V_{\text{wiki}} > 1$ (verified human readership).
  - Non-blank Wikipedia article title.
- **Generates Three Independent CSV Review Documents:**
  1. [`docs/species_ranking_by_swiki.csv`](file:///Users/amitjoshi2724/Desktop/phylogenle/docs/species_ranking_by_swiki.csv): Ranked #1 to #N purely by global language sitelinks.
  2. [`docs/species_ranking_by_vwiki.csv`](file:///Users/amitjoshi2724/Desktop/phylogenle/docs/species_ranking_by_vwiki.csv): Ranked #1 to #N purely by English Wikipedia pageviews.
  3. [`docs/species_popularity_rankings.csv`](file:///Users/amitjoshi2724/Desktop/phylogenle/docs/species_popularity_rankings.csv): Combined master dataset featuring both ranks side-by-side for calibration.

---

## 4. Key Configuration Parameters

At the top of [`rank_species_popularity.py`](file:///Users/amitjoshi2724/Desktop/phylogenle/rank_species_popularity.py#L31-L41):

```python
START_DATE = "20250101"   # Format YYYYMMDD: Start date for Wikipedia traffic
END_DATE   = "20261231"   # Format YYYYMMDD: End date for Wikipedia traffic
DATE_LABEL = "2025–2026"  # Human-readable label for logs, CSV headers, & reports
CACHE_PERIOD_KEY = f"vwiki_{START_DATE}_{END_DATE}"  # Unique cache invalidation key

MAX_WORKERS = 10          # Thread pool size (stay <= 15 to avoid 429 rate limits)
SAVE_INTERVAL = 200       # Cache disk flush frequency (every N queries)
```

> [!TIP]
> **Advancing the Year:** When you want to roll forward to a new time window (e.g., `20260101` to `20271231`), simply change `START_DATE`, `END_DATE`, and `DATE_LABEL`. Because `CACHE_PERIOD_KEY` changes, the script will automatically recognize that the cached pageviews are outdated and re-harvest fresh traffic without losing any of the resolved QIDs, sitelinks, or canonical titles!

---

## 5. Frequently Asked Questions & Scenarios

### Q1: "I added 5 new species to `data/species_taxonomy_catalog.json`. Do I have to re-harvest all 26,000 species?"
**No.** When you run `python3 rank_species_popularity.py`:
- Step 1 checks the cache and sees that 26,320 species are already resolved. It only queries the 5 new species.
- Step 2 only checks canonical fallbacks for the 5 new species.
- Step 3 only queries the Wikimedia REST API for the 5 new articles.
- The entire run finishes in **under 3 seconds**.

### Q2: "I added an umbrella taxon like `Fiddler Crab (Ocypodidae)` or `Barn Owl (Tyto)`. How do I keep SPARQL from overwriting it with a scientific stub?"
When adding umbrella taxa, set `"canonical_verified": true` and supply the verified `qid` directly in the cache (or via [`apply_collapsed_taxa_audit.py`](file:///Users/amitjoshi2724/Desktop/phylogenle/apply_collapsed_taxa_audit.py)). Step 1 and Step 2 will see that `qid` and `canonical_verified` are already present, completely bypassing automated SPARQL overwrites.

### Q3: "What downstream files depend on `rank_species_popularity.py`?"
1. [`docs/species_ranking_by_vwiki.csv`](file:///Users/amitjoshi2724/Desktop/phylogenle/docs/species_ranking_by_vwiki.csv): Used directly by [`check_original_344_in_top1k.py`](file:///Users/amitjoshi2724/Desktop/phylogenle/check_original_344_in_top1k.py) to generate tier analysis reports.
2. [`data/species_list.json`](file:///Users/amitjoshi2724/Desktop/phylogenle/data/species_list.json): The full interactive autocomplete list used by [`script.js`](file:///Users/amitjoshi2724/Desktop/phylogenle/script.js) during live gameplay.
3. Daily Puzzle Generators: Easy, Normal, and Hard mode target selectors read the ranks generated by this pipeline.
