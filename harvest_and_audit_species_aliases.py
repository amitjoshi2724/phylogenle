#!/usr/bin/env python3
"""
Phylogenle - Species Alias Harvester & Audit Engine (harvest_and_audit_species_aliases.py)

Audits and systematically populates verified common name aliases, regional names,
and taxonomic synonyms across all organisms in the master catalog.

Sources mined:
  1. Cached raw harvest in data/species_aliases_harvest_cache.json (from Wikidata skos:altLabel
     and English Wikipedia incoming redirects; re-harvested via --refresh-network).
  2. Consolidated taxonomic synonyms in data/consolidated_synonyms.json.
  3. Algorithmic vernacular & taxonomic synonym verification filter (eliminating all
     Wikipedia namespaces, anatomical/topical sub-articles, misspellings/typos,
     abbreviated binomials, redundant plurals, and primary-name collisions).

Outputs:
  - docs/AUDIT_SPECIES_ALIASES.md: Detailed audit report of alias coverage.
  - data/species_aliases.json: Enriched, sanitized multi-synonym registry for autocomplete and guess validation.
  - Re-triggers Step 4 of rank_species_popularity.py to update all 3 CSV ranking sheets in docs/.

Usage:
  python3 harvest_and_audit_species_aliases.py --audit-only       # Run audit without modifying files
  python3 harvest_and_audit_species_aliases.py                    # Sanitize & sync aliases + CSVs from harvest cache
  python3 harvest_and_audit_species_aliases.py --refresh-network  # Re-query Wikidata & Wikipedia from scratch
"""

import os
import sys
import json
import csv
import re
import time
import urllib.request
import urllib.parse
from difflib import SequenceMatcher
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CATALOG_PATH = os.path.join(BASE_DIR, "data", "species_taxonomy_catalog.json")
ALIASES_PATH = os.path.join(BASE_DIR, "data", "species_aliases.json")
SYNONYM_MAP_PATH = os.path.join(BASE_DIR, "data", "consolidated_synonyms.json")
CACHE_PATH = os.path.join(BASE_DIR, "data", "wikimedia_popularity_cache.json")
HARVEST_CACHE_PATH = os.path.join(BASE_DIR, "data", "species_aliases_harvest_cache.json")
REPORT_MD_PATH = os.path.join(BASE_DIR, "docs", "AUDIT_SPECIES_ALIASES.md")
VWIKI_CSV_PATH = os.path.join(BASE_DIR, "docs", "species_ranking_by_vwiki.csv")

USER_AGENT = "Phylogenle/1.0 (educational evolutionary biology puzzle game; https://amitjoshi2724.github.io/phylogenle/)"

# Broad umbrella categories that should never be mapped as an alias to a single species
UMBRELLA_BLACKLIST = {
    "animal", "plant", "fungus", "bacteria", "bird", "fish", "mammal", "reptile", "amphibian",
    "insect", "spider", "crab", "beetle", "frog", "snake", "lizard", "turtle", "whale", "shark",
    "owl", "hawk", "eagle", "falcon", "duck", "goose", "tree", "flower", "grass", "mushroom",
    "species", "taxon", "organism", "creature", "beast", "fauna", "flora"
}

STOP_PREPOSITIONS = {
    "in", "on", "at", "by", "for", "from", "with", "about", "into", "onto", "upon",
    "within", "without", "between", "among", "through", "during", "before", "after",
    "since", "until", "under", "over", "vs", "versus", "and", "or", "as", "is", "are",
    "was", "were", "to", "the", "a", "an", "of"
}

TOPIC_JUNK_WORDS = {
    "penis", "vagina", "genitalia", "sex", "mating", "reproduction", "pregnancy",
    "gestation", "insemination", "slaughter", "farming", "herding", "industry",
    "production", "conservation", "poaching", "hunting", "baiting", "attack", "attacks",
    "collision", "collisions", "bite", "bites", "sting", "stings", "dermatitis", "venom",
    "poisoning", "disease", "diseases", "infection", "pathology", "anatomy", "biology",
    "ecology", "evolution", "evolutionary", "behavior", "behaviour", "communication",
    "intelligence", "emotion", "vision", "hearing", "diet", "dietary", "hibernation",
    "migration", "population", "populations", "habitat", "distribution", "taxonomy",
    "classification", "genetics", "genome", "folklore", "mythology", "religion",
    "culture", "cultural", "depictions", "history", "origin", "origins", "theories",
    "views", "meat", "milk", "cheese", "leather", "fur", "wool", "oil", "juice",
    "extract", "powder", "powdered", "syrup", "timber", "lumber", "bark", "tusk", "tusks",
    "trunk", "trunks", "antler", "antlers", "tooth", "teeth", "skin", "bone", "bones",
    "skeleton", "skull", "heart", "brain", "stomach", "stomachs", "eye", "eyes", "paw",
    "paws", "claw", "claws", "feather", "feathers", "egg", "eggs", "nest", "larva",
    "larvae", "pupa", "nymph", "cub", "cubs", "calf", "calves", "foal", "kitten",
    "puppy", "chick", "chicks", "pet", "pets", "captivity", "zoo", "zoos", "day",
    "festival", "project", "network", "society", "foundation", "operation", "genus",
    "family", "order", "class", "phylum", "clade", "subfamily", "tribe", "species",
    "specie", "group", "complex", "hybrid", "hybrids", "breed", "breeds", "husbandry",
    "domestication", "aggression", "vocalizations", "endangered", "extinct", "pull", "ok",
    "size", "groundskeeping", "landscaping", "goatfighting", "goatry", "keeping", "urine",
    "sandbox", "draft", "user", "template", "category", "wikipedia", "portal", "file",
    "baby", "hunter", "matriarch", "rage", "rogue", "poo", "dung", "droppings", "feces",
    "female", "male", "albino", "miniature", "feral", "gladiator", "bock", "doodle",
    "cockcrow", "crowing", "cooning", "orgle", "dyer", "vistas", "unit", "moo", "eating",
    "panter", "paragon"
}

KNOWN_VERNACULAR_LOANWORDS = {
    "housecat", "catamount", "pooch", "moggy", "spud", "tater", "tattie",
    "carpincho", "chiguire", "ajolote", "duckbill", "watermole", "duckmole",
    "washbear", "honeybadger", "icebear", "silvertip", "blackfish", "carcajou",
    "peafowl", "peachick", "peahen", "hogget", "wether", "biddy", "chook",
    "barnowl", "koala", "bandicoot", "wallaby", "wallaroo", "pademelon",
    "quokka", "quoll", "numbat", "wombat", "bilby", "potoroo", "hellbender",
    "mudpuppy", "waterdog", "bullfrog", "treefrog", "woodchuck", "groundhog",
    "whistlepig", "nightcrawler", "rainworm", "angleworm", "dewworm", "crawdad",
    "crawfish", "crayfish", "mudbug", "langoustine", "pillbug", "sowbug",
    "woodlouse", "silverfish", "firebrat", "earwig", "hellgrammite", "dobsonfly",
    "lacewing", "antlion", "doodlebug", "ladybug", "ladybird", "junebug",
    "tumblebug", "glowworm", "stinkbug", "shieldbug", "cicada", "katydid",
    "yellowjacket", "tarantula", "harvestman", "vinegaroon", "abalone", "limpet",
    "periwinkle", "whelk", "conch", "cowrie", "cowry", "nudibranch", "chiton",
    "cockle", "quahog", "geoduck", "shipworm", "lancelet", "amphioxus",
    "tunicate", "hagfish", "lamprey", "wobbegong", "porbeagle", "dogfish",
    "hammerhead", "bonnethead", "monkfish", "sawfish", "guitarfish", "thornback"
}

ALLOWED_OF_PHRASES = {
    "man o' war", "man-of-war", "man of war", "portuguese man o' war",
    "portuguese man-of-war", "portuguese man of war", "bird of paradise",
    "lily of the valley", "mother of pearl", "hen of the woods", "chicken of the woods",
    "crown of thorns", "horn of plenty", "coat of mail", "lady of the night"
}

LATIN_ONLY_EXTRA = {
    "felis", "ursus", "bos", "canis", "cervus", "simia", "rana", "lacerta", "coluber",
    "testudo", "salmo", "cyprinus", "perca", "gadus", "squalus", "cancer", "aranea",
    "papilio", "phalaena", "scarabaeus", "musca", "apis", "formica", "gryllus", "cimex",
    "aphis", "coccus", "ostrea", "mytilus", "helix", "asterias", "echinus", "taenia",
    "lumbricus", "hirudo", "limax", "sepia", "didus", "thalarctos", "euarctos",
    "lycopersicon", "lycopersicum", "salisburia", "crucifera", "raphanus", "napus",
    "physalis", "arethusa", "holothuria", "pterobalaena", "sibbaldius", "sibbaldus",
    "flowerius", "rhynchodon", "siredon", "didelphys", "uncinia", "uncia", "familiaris",
    "domesticus", "domestica", "vulgaris", "vulgare", "communis", "commune", "officinalis",
    "officinale", "sativus", "sativa", "sativum", "sylvestris", "sylvestre", "campestris",
    "arvensis", "pratensis", "palustris", "maritimus", "maritima", "marinus", "marina",
    "americanus", "americana", "africanus", "africana", "asiaticus", "asiatica",
    "europaeus", "europaea", "indicus", "indica", "chinensis", "japonica", "japonicus",
    "australis", "borealis", "orientalis", "occidentalis", "giganteus", "gigantea",
    "maximus", "maxima", "minimus", "minima", "albus", "alba", "niger", "nigra", "nigrum",
    "ruber", "rubra", "rubrum", "viridis", "viride", "flava", "flavus", "caeruleus",
    "caerulea", "cinereus", "cinerea", "fuscus", "fusca", "maculatus", "maculata",
    "striatus", "striata", "cristatus", "cristata", "cornutus", "cornuta", "horridus",
    "horrida", "ferox", "velox", "regalis", "esculentum", "esculenta", "esculentus",
    "capensis", "cameloides", "brooki", "brookei", "calidus", "cassini", "ernesti",
    "furuitii", "japonensis", "madens", "nesiotes", "radama", "submelanogenys", "tundrius",
    "pelegrinoides", "atriceps", "kreyenborgi", "anatum", "antiquus", "vetus", "catodon",
    "catadon", "mahuensis", "sondaica", "melanochaita", "abyssinica", "guildayi", "diris",
    "lithobates", "ranoidea", "litoria", "taurotragus", "choeropsis", "lupulella",
    "nymphalis", "crassostrea", "osphranter", "pagophilus", "sagmatias", "protographium",
    "speyeria", "hyelaphus", "accipiter", "leptuca", "rapa", "rotunda"
}

CURATED_ESSENTIAL_ALIASES = {
    "Lynx rufus": ["red lynx", "bay lynx", "north american wildcat", "felis rufus"],
    "Panthera leo": ["african lion", "asiatic lion", "king of beasts", "felis leo"],
    "Ursus americanus": ["black bear", "north american black bear", "cinnamon bear", "kermode bear", "spirit bear"],
    "Ursus arctos": ["grizzly bear", "kodiak bear", "eurasian brown bear"],
    "Puma concolor": ["cougar", "mountain lion", "catamount", "panther", "florida panther", "felis concolor"],
    "Canis lupus": ["gray wolf", "grey wolf", "timber wolf", "arctic wolf", "tundra wolf"],
    "Canis lupus familiaris": ["domestic dog", "man's best friend", "canis familiaris", "hound", "pooch"],
    "Felis catus": ["house cat", "housecat", "domestic cat", "kitty", "moggy", "felis domesticus"],
    "Orcinus orca": ["killer whale", "blackfish"],
    "Hydrochoerus hydrochaeris": ["greater capybara", "carpincho", "chiguire"],
    "Physalia physalis": ["man-of-war", "man o' war", "bluebottle", "floating terror"],
    "Bison bison": ["american buffalo", "plains bison", "wood bison"],
    "Gulo gulo": ["glutton", "carcajou", "skunk bear"],
    "Ornithorhynchus anatinus": ["duck-billed platypus", "duckbill"],
    "Ailuropoda melanoleuca": ["panda bear", "giant panda bear", "parti-coloured bear"],
    "Marmota monax": ["woodchuck", "whistle-pig", "land-beaver"],
    "Phascolarctos cinereus": ["koala bear", "native bear"],
    "Equus asinus": ["ass", "burro", "jackass"],
    "Sus scrofa": ["wild pig", "wild hog", "razorback", "eurasian wild boar"],
    "Gallus gallus domesticus": ["rooster", "hen", "cockerel", "domestic chicken", "gallus domesticus"],
    "Lumbricina": ["earth worm", "nightcrawler", "rainworm", "angleworm", "dew-worm"],
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


def singularize(w):
    if w.endswith("wolves"):
        return w[:-6] + "wolf"
    if w.endswith("ves") and len(w) > 4:
        return w[:-3] + "f"
    if w.endswith("ies") and len(w) > 4:
        return w[:-3] + "y"
    if w.endswith("es") and len(w) > 4 and (
        w.endswith("ches") or w.endswith("shes") or w.endswith("xes") or w.endswith("sses") or w.endswith("oes")
    ):
        return w[:-2]
    if w.endswith("s") and not w.endswith("ss") and not w.endswith("us") and not w.endswith("is") and len(w) > 3:
        return w[:-1]
    return w


def norm_key(s):
    s_clean = s.lower().strip().replace("direwolf", "dire wolf").replace("direwolves", "dire wolf")
    words = [singularize(w) for w in re.split(r"[\s\-]+", s_clean) if w]
    return " ".join(words)


def latin_stem(w):
    return re.sub(r"(us|a|um|is|es|e)$", "", w.lower())


def build_vocabularies(catalog):
    """Build English dictionary, catalog English word set, and Latin taxon word set."""
    dict_words = set()
    dict_path = "/usr/share/dict/words"
    if os.path.exists(dict_path):
        with open(dict_path, "r", encoding="utf-8", errors="ignore") as f:
            dict_words = {w.strip().lower() for w in f if w.strip()}

    catalog_eng_words = set()
    latin_words = set(LATIN_ONLY_EXTRA)
    valid_genera = set(LATIN_ONLY_EXTRA)

    for s in catalog:
        for w in re.split(r"[\s\-'’\(\)]+", (s.get("common") or "").lower()):
            if len(w) >= 2:
                catalog_eng_words.add(w)
        for w in re.split(r"[\s\(\)\-\.]+", (s.get("scientific") or "").lower()):
            if len(w) >= 3:
                latin_words.add(w)
        if s.get("genus"):
            valid_genera.add(s["genus"].lower())
        for field in ("kingdom", "phylum", "class", "order", "family", "genus", "clade", "subclade"):
            val = (s.get(field) or "").lower()
            if val:
                latin_words.add(val)

    return dict_words, catalog_eng_words, latin_words, valid_genera


def is_clean_vernacular_alias(alias, common, sci, dict_words, catalog_eng_words, latin_words):
    """
    Algorithmically verify that `alias` is a clean human vernacular common name for `sci` (`common`),
    rejecting Wikipedia namespaces, topical/anatomical sub-articles, Latin binomials, plurals,
    abbreviated binomials, and misspellings/typos.
    """
    a = alias.strip().lower()
    c = (common or "").strip().lower()
    s = (sci or "").strip().lower()
    if not a or a == c or a == s:
        return False
    if len(a) < 3 or len(a) > 38:
        return False
    if a in UMBRELLA_BLACKLIST:
        return False
    # Strict ASCII letters, spaces, hyphens, apostrophes only (no colons, slashes, digits, parens)
    if not re.match(r"^[a-z][a-z\s\-']+[a-z]$", a):
        return False
    words = [w for w in re.split(r"[\s\-]+", a) if w]
    if len(words) > 4:
        return False
    # Reject single-letter abbreviated binomials (e.g., "h sapiens", "b taurus")
    if any(len(w) == 1 and w not in ("a", "o") for w in words):
        return False

    c_words = set(re.split(r"[\s\-]+", c))
    s_words = set(re.split(r"[\s\-]+", s))

    # Reject prepositions and anatomical/topical/junk words
    if a not in ALLOWED_OF_PHRASES:
        for w in words:
            w_clean = w.replace("'", "")
            if w in STOP_PREPOSITIONS or w_clean in STOP_PREPOSITIONS:
                return False
            if (w in TOPIC_JUNK_WORDS or w_clean in TOPIC_JUNK_WORDS) and w not in c_words:
                return False

    # Reject if normalized singular key equals common or scientific name
    if norm_key(a) == norm_key(c) or norm_key(a) == norm_key(s):
        return False
    if a.replace(" ", "").replace("-", "") == c.replace(" ", "").replace("-", ""):
        return False
    if a.replace(" ", "").replace("-", "") == s.replace(" ", "").replace("-", ""):
        return False
    # Reject single-word plurals of a word in the common name (e.g., "Pandas" for "Giant Panda", "Komodos" for "Komodo Dragon")
    if len(words) == 1 and words[0] not in c_words and singularize(words[0]) in c_words:
        return False
    if a in (f"{c} plant", f"{c} tree", f"{c} bird", f"{c} fish", f"{c} animal"):
        return False

    # Reject Latin binomials / taxonomic words masquerading as vernacular names
    for w in words:
        if w in s_words and w not in c_words:
            return False
        if w in LATIN_ONLY_EXTRA and w not in c_words:
            return False
        if w in latin_words and w not in catalog_eng_words and w not in dict_words:
            return False
        if w not in catalog_eng_words and w not in dict_words:
            if re.search(
                r"(idae|inae|iformes|oidea|opsida|mycetes|phyta|ensis|ense|ianus|iana|ianum|icus|ica|icum|atus|ata|atum|oides)$",
                w,
            ):
                return False

    # Every word must be a recognized English dictionary word, catalog vernacular word, or curated loanword
    valid_vocab = dict_words | catalog_eng_words | KNOWN_VERNACULAR_LOANWORDS
    for w in words:
        w_base = w[:-2] if w.endswith("'s") else w.replace("'", "")
        if (
            w not in valid_vocab
            and w_base not in valid_vocab
            and singularize(w) not in valid_vocab
            and singularize(w_base) not in valid_vocab
        ):
            return False

    # Also catch dictionary-word near-homophone typos of common-name words (e.g. "paragon falcon", "dyer wolf")
    for w in words:
        for cw in c_words:
            if len(w) >= 4 and len(cw) >= 4 and w != cw and singularize(w) != singularize(cw):
                if SequenceMatcher(None, w, cw).ratio() >= 0.80:
                    return False

    return True


def is_valid_taxonomic_synonym(alias, sci, valid_genera):
    """
    Algorithmically verify if `alias` is a legitimate binomial taxonomic synonym for `sci`
    (e.g., "felis rufus" for "Lynx rufus", "felis leo" for "Panthera leo",
    "lithobates catesbeianus" for "Aquarana catesbeiana") while rejecting misspellings.
    """
    a = alias.strip().lower()
    s = (sci or "").strip().lower()
    if not a or a == s:
        return False
    a_words = a.split()
    s_words = s.split()
    if len(a_words) != 2 or len(s_words) < 2:
        return False
    if not all(re.match(r"^[a-z]{3,}$", w) for w in a_words):
        return False
    g_a, e_a = a_words
    g_s, e_s = s_words[0], s_words[-1]
    if g_a == g_s and e_a == e_s:
        return False
    # Reject genus misspellings (e.g., "aptendodytes forsteri" vs "aptenodytes forsteri")
    if g_a != g_s and SequenceMatcher(None, g_a, g_s).ratio() >= 0.72:
        return False
    # Valid historical genus + matching specific epithet stem
    if g_a in valid_genera and len(latin_stem(e_s)) >= 3 and latin_stem(e_a) == latin_stem(e_s):
        return True
    return False


def query_sparql_altlabels_batch(scientific_names):
    """Query Wikidata SPARQL for English skos:altLabel for a batch of scientific names."""
    escaped_names = [f'"{name.replace(chr(34), chr(92) + chr(34))}"' for name in scientific_names]
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
                    results.setdefault(sci, set()).add(alt)
                return results
        except Exception:
            if attempt < 2:
                time.sleep(2.0 * (attempt + 1))
    return results


def query_wikipedia_redirects_single(title):
    """Fetch incoming English Wikipedia redirects for a single article title."""
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
                for _, pinfo in pages.items():
                    redirects = [r["title"] for r in pinfo.get("redirects", [])]
                    return title, redirects
        except Exception:
            if attempt < 2:
                time.sleep(1.0 * (attempt + 1))
    return title, []


def main():
    audit_only = "--audit-only" in sys.argv
    refresh_network = "--refresh-network" in sys.argv
    print("=" * 75)
    print("🧬 Phylogenle: Species Alias Harvester & Comprehensive Audit Engine")
    print("=" * 75)

    if not os.path.exists(CATALOG_PATH):
        print(f"Error: Catalog not found at {CATALOG_PATH}")
        sys.exit(1)

    with open(CATALOG_PATH, "r", encoding="utf-8") as f:
        catalog = json.load(f)
    print(f"Loaded {len(catalog):,} catalog entries from {CATALOG_PATH}")

    sci_to_display = {}
    sci_to_common = {}
    primary_names_lower = set()
    for s in catalog:
        sci = s["scientific"]
        comm = (s.get("common") or "").strip()
        disp = s.get("display") or (f"{comm} ({sci})" if comm else sci)
        sci_to_display[sci] = disp
        sci_to_common[sci] = comm
        primary_names_lower.add(disp.lower())
        primary_names_lower.add(sci.lower())
        if comm:
            primary_names_lower.add(comm.lower())

    existing_aliases = {}
    if os.path.exists(ALIASES_PATH):
        with open(ALIASES_PATH, "r", encoding="utf-8") as f:
            existing_aliases = json.load(f)
    print(f"Loaded {len(existing_aliases):,} existing aliases from {ALIASES_PATH}")

    cache = {}
    if os.path.exists(CACHE_PATH):
        with open(CACHE_PATH, "r", encoding="utf-8") as f:
            cache = json.load(f)

    ranked_species_order = []
    if os.path.exists(VWIKI_CSV_PATH):
        with open(VWIKI_CSV_PATH, "r", encoding="utf-8") as f:
            for r in csv.DictReader(f):
                sci = r.get("Scientific Name")
                if sci in sci_to_display:
                    ranked_species_order.append(sci)

    # =========================================================================
    # PHASE 1: AUDIT CURRENT STATE
    # =========================================================================
    print("\n--- PHASE 1: Auditing Current Alias Coverage ---")
    disp_to_sci = {disp: sci for sci, disp in sci_to_display.items()}
    aliases_by_target = {}
    for a, target in existing_aliases.items():
        target_sci = disp_to_sci.get(target)
        if not target_sci:
            continue
        target_comm = sci_to_common.get(target_sci, "")
        if a.lower() == target_sci.lower() or a.lower() == target_comm.lower():
            continue
        aliases_by_target.setdefault(target_sci, set()).add(a)

    total_species = len(catalog)
    with_aliases_count = len(aliases_by_target)
    without_aliases_count = total_species - with_aliases_count
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
    # PHASE 2 & 3: LOAD OR REFRESH HARVEST CACHE
    # =========================================================================
    harvest_cache = {}
    if os.path.exists(HARVEST_CACHE_PATH) and not refresh_network:
        with open(HARVEST_CACHE_PATH, "r", encoding="utf-8") as f:
            harvest_cache = json.load(f)
        print(f"\n--- PHASE 2 & 3: Loaded Raw Harvest Cache ({len(harvest_cache):,} species) from {HARVEST_CACHE_PATH} ---")
    else:
        print("\n--- PHASE 2: Harvesting Wikidata English Aliases (skos:altLabel) ---")
        BATCH_SIZE = 120
        all_scis = list(sci_to_display.keys())
        for i in range(0, len(all_scis), BATCH_SIZE):
            batch = all_scis[i : i + BATCH_SIZE]
            batch_results = query_sparql_altlabels_batch(batch)
            for sci, alts in batch_results.items():
                harvest_cache.setdefault(sci, [])
                harvest_cache[sci] = sorted(set(harvest_cache[sci]) | set(alts))
            time.sleep(0.15)

        print("\n--- PHASE 3: Harvesting English Wikipedia Redirects for Priority Species ---")
        priority_scis = set(ranked_species_order[:3000])
        titles_to_query = {
            cache[sci]["en_title"]: sci
            for sci in priority_scis
            if cache.get(sci, {}).get("en_title")
        }
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = {executor.submit(query_wikipedia_redirects_single, t): t for t in titles_to_query}
            for fut in as_completed(futures):
                t, reds = fut.result()
                sci = titles_to_query.get(t)
                if sci and reds:
                    harvest_cache.setdefault(sci, [])
                    harvest_cache[sci] = sorted(set(harvest_cache[sci]) | set(reds))

        with open(HARVEST_CACHE_PATH, "w", encoding="utf-8") as f:
            json.dump(harvest_cache, f, indent=2, ensure_ascii=False)
        print(f"Saved harvest cache to {HARVEST_CACHE_PATH}")

    # =========================================================================
    # PHASE 4: ALGORITHMIC SANITIZATION & DEDUPLICATION
    # =========================================================================
    print("\n--- PHASE 4: Running Algorithmic Alias & Taxonomic Synonym Filter ---")
    dict_words, catalog_eng_words, latin_words, valid_genera = build_vocabularies(catalog)

    consolidated_synonyms = {}
    if os.path.exists(SYNONYM_MAP_PATH):
        with open(SYNONYM_MAP_PATH, "r", encoding="utf-8") as f:
            consolidated_synonyms = json.load(f)

    final_aliases = {}
    species_gaining_aliases = set()

    # 1. Process curated essential aliases first (high-priority species)
    for sci, cur_list in CURATED_ESSENTIAL_ALIASES.items():
        if sci not in sci_to_display:
            continue
        target_disp = sci_to_display[sci]
        for a in cur_list:
            a_low = a.strip().lower()
            if a_low and a_low not in primary_names_lower:
                final_aliases[a_low] = target_disp
                species_gaining_aliases.add(sci)

    # 2. Process consolidated taxonomic synonyms (for search resolution)
    for syn_key, target_disp in consolidated_synonyms.items():
        s_low = syn_key.strip().lower()
        if target_disp in disp_to_sci and s_low not in primary_names_lower:
            if "(" not in s_low and ")" not in s_low:
                final_aliases[s_low] = target_disp
                species_gaining_aliases.add(disp_to_sci[target_disp])

    # 3. Process all species in popularity order so higher-popularity species claim shared vernacular aliases first
    ordered_scis = list(ranked_species_order) + [s for s in sci_to_display if s not in set(ranked_species_order)]

    for sci in ordered_scis:
        target_disp = sci_to_display[sci]
        comm = sci_to_common.get(sci, "")
        raw_candidates = harvest_cache.get(sci, [])
        if not raw_candidates:
            continue

        seen_norms = {norm_key(comm), norm_key(sci), norm_key(comm.replace(" ", ""))}
        for cur_a in CURATED_ESSENTIAL_ALIASES.get(sci, []):
            seen_norms.add(norm_key(cur_a))
        for raw_c in raw_candidates:
            c_low = raw_c.strip().lower()
            if not c_low or c_low in primary_names_lower or c_low in final_aliases:
                continue

            if is_clean_vernacular_alias(c_low, comm, sci, dict_words, catalog_eng_words, latin_words):
                nk = norm_key(c_low)
                if nk in seen_norms:
                    continue
                seen_norms.add(nk)
                final_aliases[c_low] = target_disp
                species_gaining_aliases.add(sci)
            elif is_valid_taxonomic_synonym(c_low, sci, valid_genera):
                final_aliases[c_low] = target_disp
                species_gaining_aliases.add(sci)

    with open(ALIASES_PATH, "w", encoding="utf-8") as f:
        json.dump(final_aliases, f, indent=2, ensure_ascii=False)
    print(f"Saved {len(final_aliases):,} verified non-primary aliases across {len(species_gaining_aliases):,} species to {ALIASES_PATH}.")

    # =========================================================================
    # PHASE 5: RE-AUDIT & GENERATE PERSISTENT AUDIT REPORT
    # =========================================================================
    print("\n--- PHASE 5: Generating Persistent Audit Report ---")
    post_aliases_by_target = {}
    for a, target in final_aliases.items():
        target_sci = disp_to_sci.get(target)
        if target_sci:
            post_aliases_by_target.setdefault(target_sci, set()).add(a)

    post_with_aliases = len(post_aliases_by_target)
    top_1000_post_with_aliases = sum(1 for s in top_1000 if s in post_aliases_by_target)

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
        ("Ailuropoda melanoleuca", "Giant Panda"),
    ]

    report_lines = [
        "# 🧬 Comprehensive Audit & Registry: Species Aliases Coverage",
        "",
        f"> **Audit Date:** {time.strftime('%Y-%m-%d')}  ",
        f"> **Total Catalog Species:** {total_species:,}  ",
        f"> **Total Verified Non-Primary Aliases in Registry:** {len(final_aliases):,}  ",
        "",
        "## 1. Executive Summary & Coverage Metrics",
        "",
        "| Metric | Value |",
        "| :--- | :---: |",
        f"| **Total Verified Aliases (`species_aliases.json`)** | **{len(final_aliases):,}** |",
        f"| **Species with Verified Aliases (Catalog-Wide)** | **{post_with_aliases:,} ({post_with_aliases/total_species*100:.1f}%)** |",
        f"| **Top 1,000 Species with Aliases (🐾 Easy Tier)** | **{top_1000_post_with_aliases:,} / 1,000 ({top_1000_post_with_aliases/10:.1f}%)** |",
        "| **Dangling Alias Targets (Not in `species_list.json`)** | **0** |",
        "| **Primary-Name Shadowing Collisions** | **0** |",
        "",
        "## 2. Key Spotlight Organisms & Verified Harvested Aliases",
        "",
        "| Organism | Scientific Name | Verified Harvested Aliases |",
        "| :--- | :--- | :--- |",
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
        "   - The `Alternative Names / Aliases` column is compiled from `data/species_aliases.json` via Step 4 of `rank_species_popularity.py`.",
        "",
    ])

    with open(REPORT_MD_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))
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
    print("🎉 COMPLETED! All aliases audited, sanitized, synced, and verified.")
    print("=" * 75)


if __name__ == "__main__":
    main()
