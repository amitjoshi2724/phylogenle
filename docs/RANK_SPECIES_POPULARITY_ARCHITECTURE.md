# 🧬 Architecture & Operations: `rank_species_popularity.py`

> **Document Version:** 2.0 (Comprehensive API & Empirical Metric Deep Dive)  
> **Target Audience:** Core Contributors, Maintainers, & Researchers  
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

## 2. Deep Dive: The Two Empirical Popularity Metrics ($S_{\text{wiki}}$ vs. $V_{\text{wiki}}$)

The ranking engine relies on two distinct empirical metrics harvested from the Wikimedia Foundation's open knowledge graph. Each metric measures a fundamentally different dimension of organism prominence.

```
+-------------------------------------------------------------------------------------------------------+
|                                    WIKIMEDIA DATA SIGNALS COMPARISON                                  |
+-------------------------------------------------------------------------------------------------------+
|  Metric     | Source                     | What It Measures                    | Primary Advantage   |
|-------------+----------------------------+-------------------------------------+---------------------|
|  S_wiki     | Wikidata Knowledge Graph   | Cross-cultural, global consensus    | Immune to viral     |
|             | (?item wikibase:sitelinks) | across 300+ language editions       | news/media spikes   |
|-------------+----------------------------+-------------------------------------+---------------------|
|  V_wiki     | Wikimedia REST API         | Real human curiosity & readership   | Matches player      |
|             | (/metrics/pageviews/...)   | in English over 24-month window     | intuition & culture |
+-------------------------------------------------------------------------------------------------------+
```

### 2.1 Metric 1: $S_{\text{wiki}}$ (Wikidata Global Sitelinks)

#### What Is a Sitelink?
In Wikidata, every entity has a unique identifier (e.g., `Q140` for *Lion*, `Q144` for *Dog*). A **sitelink** is an explicit pointer linking that central Wikidata concept to an article about that concept in a specific Wikipedia language edition (such as English `en.wikipedia.org`, Spanish `es.wikipedia.org`, Japanese `ja.wikipedia.org`, Arabic `ar.wikipedia.org`, Swahili `sw.wikipedia.org`, etc.).

#### Why $S_{\text{wiki}}$ Matters
- **Global Cross-Cultural Consensus:** If an organism has an article in 180+ languages, it is recognized universally across civilization—not just in the English-speaking world.
- **Immunity to Short-Term Fads:** A viral meme on TikTok or a temporary news event might generate millions of English views for a few days, but it will **not** cause 150 separate international volunteer Wikipedia communities to translate and publish standalone encyclopedic entries.
- **Benchmark Champions:** Organisms with the highest $S_{\text{wiki}}$ globally:
  - *Homo sapiens* (Human): ~300 languages
  - *Panthera leo* (Lion): ~205 languages
  - *Canis lupus* (Wolf/Dog): ~195 languages
  - *Malus domestica* (Apple): ~190 languages
  - *Apis mellifera* (Western Honey Bee): ~185 languages

#### Limitations of $S_{\text{wiki}}$
- **Bot-Generated Taxonomic Stubs:** In some smaller language Wikipedias (e.g., Cebuano, Waray, Swedish), automated bots historically created millions of 1-sentence stubs for obscure beetles and snails based on GBIF or Catalogue of Life databases. This can artificially inflate the sitelink count of an obscure snail from 1 to 15.
- **Lagging Indicator:** Sitelink counts grow slowly over decades as encyclopedia contributors write translations.

---

### 2.2 Metric 2: $V_{\text{wiki}}$ (English Wikipedia Cumulative Pageviews)

#### What Is $V_{\text{wiki}}$?
$V_{\text{wiki}}$ represents the **exact count of human visits** to the organism's English Wikipedia article across all devices (desktop, mobile web, and official mobile apps), aggregated monthly over a multi-year period (default: `20250101` to `20261231`).

#### Why $V_{\text{wiki}}$ Matters
- **Real-Time Cultural Salience:** Players interact with the game in English. $V_{\text{wiki}}$ captures what English speakers actively think about, research, watch documentaries on, and learn about in school.
- **Resolving High-Interest Organisms:** Many organisms that have moderate sitelinks (~40–60 languages) have massive cultural popularity in English-speaking regions:
  - *Blue-ringed Octopus* (*Hapalochlaena*): ~1.27M views
  - *Axolotl* (*Ambystoma mexicanum*): ~3.8M views
  - *Capybara* (*Hydrochoerus hydrochaeris*): ~4.2M views
  - *Peregrine Falcon* (*Falco peregrinus*): ~2.1M views
  - *Venus Flytrap* (*Dionaea muscipula*): ~1.9M views
- **Automated Bot Filtering:** The Wikimedia Foundation's Pageview API runs proprietary bot/crawler detection algorithms. When querying `agent: all-agents`, the metric captures legitimate human pageviews while filtering out standard web scrapers and search engine indexers.

#### Limitations of $V_{\text{wiki}}$
- **Name Collisions & Ambiguity:** A common English word might refer to multiple concepts (e.g., *"Kiwi"* refers to the bird, the fruit, and people from New Zealand). This is why the pipeline uses MediaWiki canonical page properties (`wikibase_item`) to map specifically to the biological taxon entity.
- **Temporary Media Spikes:** A Hollywood movie (e.g., *Cocaine Bear*) or a viral meme can temporarily boost an article's traffic. Aggregating across a full 24-month window smoothes out short-term anomalies.

---

## 3. Comprehensive Breakdown of the 4 API Calls

[`rank_species_popularity.py`](file:///Users/amitjoshi2724/Desktop/phylogenle/rank_species_popularity.py) interfaces with **four distinct endpoints** across the Wikimedia ecosystem. Here are the exact request structures, headers, payloads, and response formats.

```mermaid
sequenceDiagram
    autonumber
    participant Script as rank_species_popularity.py
    participant SPARQL as Wikidata SPARQL Endpoint
    participant EnWiki as MediaWiki Action API (enwiki)
    participant WB as Wikidata API (wbgetentities)
    participant REST as Wikimedia REST Pageviews API

    Note over Script,SPARQL: Step 1: Bulk Sitelinks & Articles
    Script->>SPARQL: POST /sparql (Batch of 120 scientific names)
    SPARQL-->>Script: JSON bindings (QID, sitelinks count, en_title)

    Note over Script,EnWiki: Step 2: Canonical Redirect Resolution
    Script->>EnWiki: POST /w/api.php (Batch of 35 titles, redirects=1)
    EnWiki-->>Script: JSON pages (canonical title, wikibase_item QID)

    Note over Script,WB: Step 2 & 2B: Entity Claims & Sitelinks
    Script->>WB: GET /w/api.php?action=wbgetentities (QIDs chunked by 50)
    WB-->>Script: JSON entities (sitelinks count, P31 instance, P105 rank)

    Note over Script,REST: Step 3: High-Throughput Pageviews
    Script->>REST: GET /metrics/pageviews/.../monthly/20250101/20261231
    REST-->>Script: JSON monthly views array (Desktop + Mobile)
```

---

### 3.1 API Call #1: Wikidata SPARQL Query Service (Batch Sitelinks)

#### Endpoint & HTTP Specifications
- **URL:** `https://query.wikidata.org/sparql`
- **Method:** `POST`
- **Headers:**
  ```http
  User-Agent: Phylogenle/1.0 (educational evolutionary biology puzzle game; https://amitjoshi2724.github.io/phylogenle/; [EMAIL_ADDRESS])
  Content-Type: application/x-www-form-urlencoded
  Accept: application/sparql-results+json
  ```
- **Batch Size:** 120 scientific names per HTTP POST.

#### SPARQL Query Syntax
```sparql
SELECT ?scientificName ?item ?sitelinks ?enTitle WHERE {
  VALUES ?scientificName { "Panthera leo" "Homo sapiens" "Tyto alba" "Electrophorus electricus" ... }
  ?item wdt:P225 ?scientificName .
  ?item wikibase:sitelinks ?sitelinks .
  OPTIONAL {
    ?article schema:about ?item ;
             schema:isPartOf <https://en.wikipedia.org/> ;
             schema:name ?enTitle .
  }
}
```

#### Detailed Field Explanation
1. `VALUES ?scientificName { ... }`: Injects the 120 binomial names into a single query block, replacing 120 individual round-trip requests with 1.
2. `?item wdt:P225 ?scientificName`: `P225` is Wikidata’s official **Taxon Name** property. It anchors the query directly to the biological taxon record.
3. `?item wikibase:sitelinks ?sitelinks`: `wikibase:sitelinks` is a precomputed integer stored in Wikidata’s triplestore representing the total number of connected Wikipedia language articles.
4. `OPTIONAL { ... schema:isPartOf <https://en.wikipedia.org/> ... }`: Finds the exact title of the English Wikipedia article if one exists, without discarding species that lack an English article.

#### Raw JSON Response Format
```json
{
  "head": {
    "vars": [ "scientificName", "item", "sitelinks", "enTitle" ]
  },
  "results": {
    "bindings": [
      {
        "scientificName": { "type": "literal", "value": "Panthera leo" },
        "item": { "type": "uri", "value": "http://www.wikidata.org/entity/Q140" },
        "sitelinks": { "datatype": "http://www.w3.org/2001/XMLSchema#integer", "type": "literal", "value": "205" },
        "enTitle": { "type": "literal", "value": "Lion" }
      },
      {
        "scientificName": { "type": "literal", "value": "Tyto alba" },
        "item": { "type": "uri", "value": "http://www.wikidata.org/entity/Q25317" },
        "sitelinks": { "datatype": "http://www.w3.org/2001/XMLSchema#integer", "type": "literal", "value": "112" },
        "enTitle": { "type": "literal", "value": "Western barn owl" }
      }
    ]
  }
}
```

---

### 3.2 API Call #2: MediaWiki Action API (Redirect & Canonical Resolution)

#### Why This Call Is Essential
Wikidata often contains only the scientific binomial, but the English Wikipedia article might be located under a common name (e.g. *Canis lupus* $\rightarrow$ *Wolf*), or under a title that has since been moved or redirected. Furthermore, Latin spelling variations, hyphens, and gender declensions (*-us* vs *-a*) must be normalized.

#### Endpoint & HTTP Specifications
- **URL:** `https://en.wikipedia.org/w/api.php`
- **Method:** `POST`
- **Headers:**
  ```http
  User-Agent: Phylogenle/1.0 (educational evolutionary biology puzzle game; https://amitjoshi2724.github.io/phylogenle/; [EMAIL_ADDRESS])
  Content-Type: application/x-www-form-urlencoded
  ```
- **Payload Parameters:**
  ```python
  {
      "action": "query",
      "titles": "|".join(chunk),      # Up to 35 titles separated by pipes
      "prop": "pageprops",            # Requests page metadata
      "redirects": "1",               # Automatically resolves redirects!
      "format": "json"
  }
  ```

#### Raw JSON Response Format
When querying titles like `"sand dollar"`, `"Canis lupus familiaris"`, and `"Uca pugilator"`:
```json
{
  "query": {
    "normalized": [
      { "from": "sand dollar", "to": "Sand dollar" }
    ],
    "redirects": [
      { "from": "Canis lupus familiaris", "to": "Dog" },
      { "from": "Uca pugilator", "to": "Atlantic sand fiddler crab" }
    ],
    "pages": {
      "4269": {
        "pageid": 4269,
        "ns": 0,
        "title": "Dog",
        "pageprops": {
          "wikibase_item": "Q144"
        }
      },
      "129841": {
        "pageid": 129841,
        "ns": 0,
        "title": "Sand dollar",
        "pageprops": {
          "wikibase_item": "Q638541"
        }
      }
    }
  }
}
```

#### How the Script Resolves Multi-Hop Redirect Chains
MediaWiki provides two lookup tables in the response: `normalized` (spelling/case changes) and `redirects` (page pointer changes). 

The helper function [`query_enwiki_fallback_batch()`](file:///Users/amitjoshi2724/Desktop/phylogenle/rank_species_popularity.py#L114-L183) builds an in-memory graph (`alias_to_target` and `canonical_map`) and traverses up to 5 redirect hops for every candidate title until it lands on the terminal page and extracts both:
1. `canonical_title`: The true destination title on English Wikipedia.
2. `wikibase_item`: The Wikidata QID directly bound to that Wikipedia article.

---

### 3.3 API Call #3: Wikidata Entity API (`wbgetentities`)

#### Endpoint & HTTP Specifications
- **URL:** `https://www.wikidata.org/w/api.php`
- **Method:** `GET`
- **Headers:** `User-Agent: Phylogenle/1.0 ...`
- **Usage 1 (Sitelink Enrichment):**
  `?action=wbgetentities&ids=Q144|Q638541&props=sitelinks&format=json`
  - Fetches the total sitelink count for newly discovered canonical QIDs.
- **Usage 2 (Taxon Rank & Biological Verification in Step 2B):**
  `?action=wbgetentities&ids=Q144|Q12345&props=claims&format=json`
  - Inspects `claims.P31` (**instance of**) and `claims.P105` (**taxon rank**).

#### Step 2B Verification Logic
To prevent an article about a broad family or random concept from being stolen by a single species, the script validates:
- **Valid Instance Types (`P31`):** Must match taxon (`Q16521`), subspecies (`Q23038290`), breed (`Q38829`), cultivar (`Q4886`), or organism group.
- **Forbidden Higher Taxon Ranks (`P105`):** Must **NOT** be a Genus (`Q35409`), Family (`Q36732`), Order (`Q38348`), Class (`Q16428`), or Phylum (`Q34740`).

---

### 3.4 API Call #4: Wikimedia REST API Pageviews Metric Endpoint

#### Endpoint & HTTP Specifications
- **URL Template:**
  ```text
  https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/en.wikipedia.org/all-access/all-agents/{clean_title}/monthly/{start_date}/{end_date}
  ```
- **Method:** `GET`
- **Path Parameters:**
  - `project`: `en.wikipedia.org` (English Wikipedia)
  - `access`: `all-access` (aggregates Desktop, Mobile Web, and Mobile App)
  - `agent`: `all-agents` (filters out automated search engine crawlers and spiders)
  - `clean_title`: URL-encoded article title with spaces replaced by underscores (e.g. `Panthera_leo`, `Blue_whale`, `Western_barn_owl`)
  - `granularity`: `monthly`
  - `start_date`: `20250101`
  - `end_date`: `20261231`

#### Raw JSON Response Format
```json
{
  "items": [
    {
      "project": "en.wikipedia",
      "article": "Lion",
      "granularity": "monthly",
      "timestamp": "2025010100",
      "access": "all-access",
      "agent": "all-agents",
      "views": 412589
    },
    {
      "project": "en.wikipedia",
      "article": "Lion",
      "granularity": "monthly",
      "timestamp": "2025020100",
      "access": "all-access",
      "agent": "all-agents",
      "views": 389210
    },
    {
      "project": "en.wikipedia",
      "article": "Lion",
      "granularity": "monthly",
      "timestamp": "2025030100",
      "access": "all-access",
      "agent": "all-agents",
      "views": 421004
    }
  ]
}
```

#### Cumulative Summation
The script loops through every entry in `data["items"]` and computes:
$$V_{\text{cumulative}} = \sum_{m \in \text{items}} m[\text{"views"}]$$
For *Lion*, summing all monthly items across 2025–2026 yields **~8,842,000 views**.

#### HTTP Status Handling
- `200 OK`: Returns parsed integer total.
- `404 Not Found`: Article does not exist or has 0 pageviews in this period $\rightarrow$ returns `0`.
- `429 Too Many Requests`: Triggers exponential backoff (`time.sleep(2 ** attempt)`).
- `502 / 503 Bad Gateway / Service Unavailable`: Wikimedia server load $\rightarrow$ triggers exponential backoff.
- Transient Failure after 6 attempts: Returns `None` so the cache entry is **not corrupted**.

---

## 4. The "Only Do What Needs to Be Done" Philosophy

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

### 4.1 The Cache Data Schema
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

### 4.2 Delta Filtering Criteria per Step
| Step | What Triggers Work? | Filter Logic in Code |
| :--- | :--- | :--- |
| **Step 1 (Wikidata SPARQL)** | Species not in cache, or `qid is None`, or missing `swiki`. | `s["scientific"] not in cache or cache[s["scientific"]].get("qid") is None or "swiki" not in cache[s["scientific"]]` |
| **Step 2 (Wikipedia Canonical)** | Species has no `en_title` or has not been `canonical_verified`. | `not cache.get(s["scientific"], {}).get("en_title") or not cache.get(s["scientific"], {}).get("canonical_verified")` |
| **Step 3 (Wikimedia Pageviews)** | Article has `vwiki_period != CACHE_PERIOD_KEY` or `vwiki == 0` on an un-queried title. | `rec.get("vwiki_period") != CACHE_PERIOD_KEY` |

### 4.3 Automatic Invalidation Hooks
If Step 2 detects that an organism's article was renamed or redirected to a better canonical title (for example, from a scientific synonym to an English common name):
```python
if best_title != cache[sci].get("en_title"):
    cache[sci]["en_title"] = best_title
    cache[sci]["vwiki_period"] = None  # Immediately invalidates cached views!
```
By setting `vwiki_period = None`, Step 3 will automatically harvest pageviews for the new article title during the very next run.

### 4.4 Cache Poisoning Defense
If a network disconnect, socket timeout, or 503 service error occurs during traffic fetching:
- The script retries up to **6 times** with exponential backoff (`2^attempt` seconds).
- If all 6 attempts fail, the helper returns `(title, None)`.
- The harvester checks `if views is not None:`. If it is `None`, **it does NOT write `views = 0` to the cache** and does NOT set `vwiki_period`. This prevents transient network glitches from permanently poisoning high-popularity animals with zero views.

### 4.5 Periodic Checkpointing
Every 200 fetched articles and at the completion of every batch, `save_cache(cache)` writes directly to disk. If the script is interrupted (Ctrl+C, power loss), zero progress is lost—restarting picks up exactly where it left off.

---

## 5. End-to-End Pipeline Walkthrough

### Step 1: High-Speed Wikidata SPARQL Harvesting
- **Objective:** Map each scientific name to its Wikidata entity (`qid`), count cross-wiki sitelinks (`swiki`), and find the English Wikipedia article (`en_title`).
- **Optimization:** Instead of querying 26,000 species one by one, species are chunked into **batches of 120 names** and sent via HTTP `POST` to the Wikidata SPARQL endpoint (`https://query.wikidata.org/sparql`).
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

## 6. How the Final Rankings and Tiers Are Computed

In Step 4, after aggregating all biological data, the script sorts the dataset using a deterministic tuple key:

### 6.1 Ranking by $V_{\text{wiki}}$ (English Wikipedia Pageviews)
```python
by_vwiki = sorted(
    [item for item in all_ranked if item.get("vwiki", 0) > 1 and item.get("swiki", 0) > 1 and bool((item.get("en_title") or "").strip())],
    key=lambda x: (x["vwiki"], x["swiki"], x["common"]),
    reverse=True
)
```
- **Primary Sort Key:** $V_{\text{wiki}}$ (descending). The organism with the most total pageviews across 2025–2026 takes Rank #1.
- **Secondary Sort Key (Tie-breaker 1):** $S_{\text{wiki}}$ (descending). If two organisms have identical pageviews, the one with more global language translations wins.
- **Tertiary Sort Key (Tie-breaker 2):** Common name alphabetical (ascending).

### 6.2 Ranking by $S_{\text{wiki}}$ (Global Wikidata Sitelinks)
```python
by_swiki = sorted(
    [item for item in all_ranked if item.get("swiki", 0) > 1 and item.get("vwiki", 0) > 1 and bool((item.get("en_title") or "").strip())],
    key=lambda x: (x["swiki"], x["vwiki"], x["common"]),
    reverse=True
)
```
- **Primary Sort Key:** $S_{\text{wiki}}$ (descending).
- **Secondary Sort Key:** $V_{\text{wiki}}$ (descending).

### 6.3 Difficulty Tier Boundaries
In downstream game systems, these ranks map into tiers:
$$\text{Tier} = \begin{cases} 
\text{Easy (🐾)} & \text{Rank } 1 \le r \le 1,000 \\ 
\text{Normal (🌿)} & \text{Rank } 1,001 \le r \le 2,000 \\ 
\text{Advanced (🔬)} & \text{Rank } 2,001 \le r \le 5,000 \\ 
\text{Master (⚡)} & \text{Rank } > 5,000 
\end{cases}$$

---

## 7. Key Configuration Parameters

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

## 8. Frequently Asked Questions & Scenarios

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
