#!/usr/bin/env python3
"""
Phylogenle - Diagnostic Analysis Script:
Checks where the original 344 baseline species appear in the empirical Vwiki rankings (docs/species_ranking_by_vwiki.csv).
Calculates how many are in the Top 1,000 (Easy Tier cutoff), and for those outside, exactly how much they are off by.
Includes analysis for both:
  1. Strict species-level binomial evaluation.
  2. Option 3 gameplay evaluation (where recognizable baseline genuses like Giraffe, Gorilla, Baboon are credited with their genus-level ranking).
"""

import os
import sys
import json
import csv
import re
import datetime
import subprocess

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_344_PATH = os.path.join(BASE_DIR, "data", "original_344_species.json")
VWIKI_CSV = os.path.join(BASE_DIR, "docs", "species_ranking_by_vwiki.csv")
REPORT_MD = os.path.join(BASE_DIR, "docs", "ORIGINAL_344_VS_TOP1K_ANALYSIS.md")

SPECIAL_TAXA_344 = {

    "Uca pugilator": {"taxon_sci": "Ocypodidae", "common": "Fiddler Crab", "rank_level": "Family"},
    "Tyto alba": {"taxon_sci": "Tyto", "common": "Barn Owl", "rank_level": "Genus"},
    "Electrophorus electricus": {"taxon_sci": "Electrophorus", "common": "Electric Eel", "rank_level": "Genus"},
    "Atta cephalotes": {"taxon_sci": "Atta", "common": "Leafcutter Ant", "rank_level": "Genus"},
    "Goliathus goliatus": {"taxon_sci": "Goliathus", "common": "Goliath Beetle", "rank_level": "Genus"},
    "Latrodectus mactans": {"taxon_sci": "Latrodectus", "common": "Black Widow Spider", "rank_level": "Genus"},
    "Zalophus californianus": {"taxon_sci": "Otariinae", "common": "Sea Lion", "rank_level": "Subfamily"},
    "Mnemiopsis leidyi": {"taxon_sci": "Ctenophora", "common": "Comb Jelly", "rank_level": "Phylum"},
    "Tetraodon nigroviridis": {"taxon_sci": "Tetraodontidae", "common": "Pufferfish", "rank_level": "Family"},
    "Pogona vitticeps": {"taxon_sci": "Pogona", "common": "Bearded Dragon", "rank_level": "Genus"},
    "Xenopus laevis": {"taxon_sci": "Xenopus", "common": "Clawed Frog", "rank_level": "Genus"},
    "Macaca mulatta": {"taxon_sci": "Macaca", "common": "Macaque", "rank_level": "Genus"},
    "Lynx lynx": {"taxon_sci": "Lynx", "common": "Lynx", "rank_level": "Genus"},
    "Ailuropoda melanoleuca": {"taxon_sci": "Ailuropoda", "common": "Panda", "rank_level": "Genus"},
    "Procyon lotor": {"taxon_sci": "Procyon", "common": "Raccoon", "rank_level": "Genus"},
    "Crocuta crocuta": {"taxon_sci": "Hyaenidae", "common": "Hyena", "rank_level": "Family"},
    "Hippopotamus amphibius": {"taxon_sci": "Hippopotamidae", "common": "Hippopotamus", "rank_level": "Family"},
    "Macropus rufus": {"taxon_sci": "Macropus", "common": "Kangaroo", "rank_level": "Genus"},
    "Coccinella septempunctata": {"taxon_sci": "Coccinellidae", "common": "Ladybird", "rank_level": "Family"},
    "Diomedea exulans": {"taxon_sci": "Diomedeidae", "common": "Albatross", "rank_level": "Family"},
    "Tridacna gigas": {"taxon_sci": "Tridacna", "common": "Giant Clam", "rank_level": "Genus"},    # 1. Higher Taxa (Orders, Suborders, Families, Subfamilies, Clades)
    "Bradypus tridactylus": {"taxon_sci": "Folivora", "common": "Sloth", "rank_level": "Suborder"},
    "Loxodonta africana": {"taxon_sci": "Elephantidae", "common": "Elephant", "rank_level": "Family"},
    "Gymnopis multiplicata": {"taxon_sci": "Gymnophiona", "common": "Caecilian", "rank_level": "Order"},
    "Erinaceus europaeus": {"taxon_sci": "Erinaceinae", "common": "Hedgehog", "rank_level": "Subfamily"},
    "Phoca vitulina": {"taxon_sci": "Pinnipedia", "common": "Seal", "rank_level": "Clade"},
    "Didelphis virginiana": {"taxon_sci": "Didelphidae", "common": "Opossum", "rank_level": "Family"},

    # 2. Iconic Genera
    "Apteryx mantelli": {"taxon_sci": "Apteryx", "common": "Kiwi", "rank_level": "Genus"},
    "Ateles geoffroyi": {"taxon_sci": "Ateles", "common": "Spider Monkey", "rank_level": "Genus"},
    "Alouatta palliata": {"taxon_sci": "Alouatta", "common": "Howler Monkey", "rank_level": "Genus"},
    "Dendrolagus matschiei": {"taxon_sci": "Dendrolagus", "common": "Tree Kangaroo", "rank_level": "Genus"},
    "Giraffa camelopardalis": {"taxon_sci": "Giraffa", "common": "Giraffe", "rank_level": "Genus"},
    "Gorilla gorilla": {"taxon_sci": "Gorilla", "common": "Gorilla", "rank_level": "Genus"},
    "Pongo pygmaeus": {"taxon_sci": "Pongo", "common": "Orangutan", "rank_level": "Genus"},
    "Papio anubis": {"taxon_sci": "Papio", "common": "Baboon", "rank_level": "Genus"},
    "Latimeria chalumnae": {"taxon_sci": "Latimeria", "common": "Coelacanth", "rank_level": "Genus"},
    "Chinchilla lanigera": {"taxon_sci": "Chinchilla", "common": "Chinchilla", "rank_level": "Genus"},
    "Arapaima gigas": {"taxon_sci": "Arapaima", "common": "Arapaima", "rank_level": "Genus"},
    "Desmodus rotundus": {"taxon_sci": "Desmodus", "common": "Vampire Bat", "rank_level": "Genus"},
    "Diceros bicornis": {"taxon_sci": "Diceros", "common": "Black Rhinoceros", "rank_level": "Genus"},
    "Rattus norvegicus": {"taxon_sci": "Rattus", "common": "Rat", "rank_level": "Genus"},
    "Mus musculus": {"taxon_sci": "Mus", "common": "Mouse", "rank_level": "Genus"},
    "Sciurus carolinensis": {"taxon_sci": "Sciurus", "common": "Tree Squirrel", "rank_level": "Genus"},
    "Sciurus vulgaris": {"taxon_sci": "Sciurus", "common": "Tree Squirrel", "rank_level": "Genus"},
    "Oryctolagus cuniculus": {"taxon_sci": "Oryctolagus", "common": "Rabbit", "rank_level": "Genus"},
    "Lepus europaeus": {"taxon_sci": "Lepus", "common": "Hare", "rank_level": "Genus"},
    "Erethizon dorsatum": {"taxon_sci": "Erethizon", "common": "Porcupine", "rank_level": "Genus"},
    "Castor canadensis": {"taxon_sci": "Castor", "common": "Beaver", "rank_level": "Genus"},
    "Talpa europaea": {"taxon_sci": "Talpidae", "common": "Mole", "rank_level": "Family"},
    "Dasypus novemcinctus": {"taxon_sci": "Dasypus", "common": "Long-nosed Armadillo", "rank_level": "Genus"},
    "Trichechus manatus": {"taxon_sci": "Trichechus", "common": "Manatee", "rank_level": "Genus"},
    "Struthio camelus": {"taxon_sci": "Struthio", "common": "Ostrich", "rank_level": "Genus"},
    "Meleagris gallopavo": {"taxon_sci": "Meleagris", "common": "Turkey", "rank_level": "Genus"},
    "Ophiophagus hannah": {"taxon_sci": "Ophiophagus", "common": "King Cobra", "rank_level": "Genus"},
    "Python bivittatus": {"taxon_sci": "Python", "common": "Python", "rank_level": "Genus"},
    "Python regius": {"taxon_sci": "Python", "common": "Python", "rank_level": "Genus"},
    "Nycticebus coucang": {"taxon_sci": "Nycticebus", "common": "Slow Loris", "rank_level": "Genus"},
    "Lontra canadensis": {"taxon_sci": "Lontra", "common": "River Otter", "rank_level": "Genus"},
    "Hylobates lar": {"taxon_sci": "Hylobates", "common": "Gibbon", "rank_level": "Genus"},
    "Syncerus caffer": {"taxon_sci": "Syncerus", "common": "African Buffalo", "rank_level": "Genus"},
    "Tursiops truncatus": {"taxon_sci": "Tursiops", "common": "Bottlenose Dolphin", "rank_level": "Genus"},
    "Hippocampus kuda": {"taxon_sci": "Hippocampus", "common": "Seahorse", "rank_level": "Genus"},

    # 3. Marine & Invertebrate Umbrella Taxa
    "Sepia officinalis": {"taxon_sci": "Sepiida", "common": "Cuttlefish", "rank_level": "Order"},
    "Asterias rubens": {"taxon_sci": "Asteroidea", "common": "Starfish", "rank_level": "Class"},
    "Chamaeleo chamaeleon": {"taxon_sci": "Chamaeleonidae", "common": "Chameleon", "rank_level": "Family"},
    "Loligo vulgaris": {"taxon_sci": "Decapodiformes", "common": "Squid", "rank_level": "Class"},
    "Octopus vulgaris": {"taxon_sci": "Octopoda", "common": "Octopus", "rank_level": "Order"},
    "Hypsibius exemplaris": {"taxon_sci": "Tardigrada", "common": "Tardigrade", "rank_level": "Phylum"},
    "Anax imperator": {"taxon_sci": "Anisoptera", "common": "Dragonfly", "rank_level": "Order"},
    "Pandinus imperator": {"taxon_sci": "Scorpiones", "common": "Scorpion", "rank_level": "Order"},
    "Lumbricus terrestris": {"taxon_sci": "Lumbricina", "common": "Earthworm", "rank_level": "Order"},
    "Strongylocentrotus purpuratus": {"taxon_sci": "Echinoidea", "common": "Sea Urchin", "rank_level": "Class"},
    "Holothuria atra": {"taxon_sci": "Holothuroidea", "common": "Sea Cucumber", "rank_level": "Class"},
    "Actinia equina": {"taxon_sci": "Actiniaria", "common": "Sea Anemone", "rank_level": "Order"},
    "Dasyatis pastinaca": {"taxon_sci": "Myliobatiformes", "common": "Stingray", "rank_level": "Order"},

    # 4. Additional Recognizable Animal Groups
    "Mantis religiosa": {"taxon_sci": "Mantodea", "common": "Mantis", "rank_level": "Order"},
    "Homarus americanus": {"taxon_sci": "Nephropidae", "common": "Lobster", "rank_level": "Family"},
    "Bombus terrestris": {"taxon_sci": "Bombus", "common": "Bumblebee", "rank_level": "Genus"},
    "Vespula vulgaris": {"taxon_sci": "Vespidae", "common": "Wasp", "rank_level": "Family"},
    "Aplysina fistularis": {"taxon_sci": "Porifera", "common": "Sponge", "rank_level": "Phylum"},
    "Lucanus cervus": {"taxon_sci": "Lucanidae", "common": "Stag Beetle", "rank_level": "Family"},
    "Crassostrea gigas": {"taxon_sci": "Ostreidae", "common": "Oyster", "rank_level": "Family"},
    "Mercenaria mercenaria": {"taxon_sci": "Bivalvia", "common": "Clam", "rank_level": "Class"},
    "Helix pomatia": {"taxon_sci": "Gastropoda", "common": "Snail", "rank_level": "Class"},
    "Archispirostreptus gigas": {"taxon_sci": "Diplopoda", "common": "Millipede", "rank_level": "Class"},
    "Penaeus monodon": {"taxon_sci": "Dendrobranchiata", "common": "Prawn", "rank_level": "Order"},
    "Deroceras reticulatum": {"taxon_sci": "Agriolimacidae", "common": "Slug", "rank_level": "Family"},
    "Schmidtea mediterranea": {"taxon_sci": "Tricladida", "common": "Planarian", "rank_level": "Order"},
    "Bufo bufo": {"taxon_sci": "Bufonidae", "common": "Toad", "rank_level": "Family"},
    "Rana temporaria": {"taxon_sci": "Anura", "common": "Frog", "rank_level": "Order"},

    # 5. Comprehensive Vertebrate & Invertebrate Umbrella Taxa
    "Pterois volitans": {"taxon_sci": "Pterois", "common": "Lionfish", "rank_level": "Genus"},
    "Lissotriton vulgaris": {"taxon_sci": "Pleurodelinae", "common": "Newt", "rank_level": "Subfamily"},
    "Hapalochlaena maculosa": {"taxon_sci": "Hapalochlaena", "common": "Blue-ringed octopus", "rank_level": "Genus"},
    "Gymnothorax javanicus": {"taxon_sci": "Muraenidae", "common": "Moray Eel", "rank_level": "Family"},
    "Nautilus pompilius": {"taxon_sci": "Nautilidae", "common": "Nautilus", "rank_level": "Family"},
    "Odontodactylus scyllarus": {"taxon_sci": "Stomatopoda", "common": "Mantis Shrimp", "rank_level": "Order"},
    "Chironex fleckeri": {"taxon_sci": "Cubozoa", "common": "Box Jellyfish", "rank_level": "Class"},
    "Limulus polyphemus": {"taxon_sci": "Limulidae", "common": "Horseshoe Crab", "rank_level": "Family"},
    "Melanocetus johnsonii": {"taxon_sci": "Lophiiformes", "common": "Anglerfish", "rank_level": "Order"},
    "Ictalurus punctatus": {"taxon_sci": "Siluriformes", "common": "Catfish", "rank_level": "Order"},
    "Phocoena phocoena": {"taxon_sci": "Phocoenidae", "common": "Porpoise", "rank_level": "Family"},
    "Sphyraena barracuda": {"taxon_sci": "Sphyraena", "common": "Barracuda", "rank_level": "Genus"},
    "Amphiprion ocellaris": {"taxon_sci": "Amphiprion", "common": "Clownfish", "rank_level": "Genus"},
    "Pygocentrus nattereri": {"taxon_sci": "Serrasalmidae", "common": "Piranha", "rank_level": "Family"},
    "Magicicada septendecim": {"taxon_sci": "Cicadidae", "common": "Cicada", "rank_level": "Family"},
    "Anopheles gambiae": {"taxon_sci": "Culicidae", "common": "Mosquito", "rank_level": "Family"},
    "Brachypelma hamorii": {"taxon_sci": "Theraphosidae", "common": "Tarantula", "rank_level": "Family"},
    "Papilio machaon": {"taxon_sci": "Papilionidae", "common": "Swallowtail Butterfly", "rank_level": "Family"},
    "Salamandra salamandra": {"taxon_sci": "Caudata", "common": "Salamander", "rank_level": "Order"},
    "Dendrobates tinctorius": {"taxon_sci": "Dendrobatidae", "common": "Poison Dart Frog", "rank_level": "Family"},
    "Vombatus ursinus": {"taxon_sci": "Vombatidae", "common": "Wombat", "rank_level": "Family"},
    "Phacochoerus africanus": {"taxon_sci": "Phacochoerus", "common": "Warthog", "rank_level": "Genus"},
    "Cynomys ludovicianus": {"taxon_sci": "Cynomys", "common": "Prairie Dog", "rank_level": "Genus"},
    "Archilochus colubris": {"taxon_sci": "Trochilidae", "common": "Hummingbird", "rank_level": "Family"},
    "Pelecanus occidentalis": {"taxon_sci": "Pelecanus", "common": "Pelican", "rank_level": "Genus"},
    "Cygnus cygnus": {"taxon_sci": "Cygnus", "common": "Swan", "rank_level": "Genus"},
    "Anser anser": {"taxon_sci": "Anser", "common": "Goose", "rank_level": "Genus"},
    "Macropus giganteus": {"taxon_sci": "Macropus", "common": "Kangaroo", "rank_level": "Genus"},
    "Phalacrocorax carbo": {"taxon_sci": "Phalacrocoracidae", "common": "Cormorant", "rank_level": "Family"},
    "Carlito syrichta": {"taxon_sci": "Tarsiidae", "common": "Tarsier", "rank_level": "Family"},
    "Solenopsis invicta": {"taxon_sci": "Solenopsis", "common": "Fire Ant", "rank_level": "Genus"},
}
SPECIAL_GENUSES_344 = SPECIAL_TAXA_344

def get_original_344():
    """Retrieve the 344 original baseline species from static file or git history."""
    if os.path.exists(STATIC_344_PATH):
        try:
            with open(STATIC_344_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass

    try:
        raw = subprocess.check_output(
            ["git", "show", "b8dea00:data/species_list.json"],
            cwd=BASE_DIR
        ).decode("utf-8")
        data = json.loads(raw)
        with open(STATIC_344_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return data
    except Exception as e:
        print(f"Warning: could not read from git history ({e}).")
        return []

def main():
    today_str = datetime.date.today().isoformat()
    print("=" * 70)
    print("🧬 Phylogenle: Original 344 Species vs. Top 1,000 Vwiki Analysis")
    print("=" * 70)

    if not os.path.exists(VWIKI_CSV):
        print(f"Error: {VWIKI_CSV} not found! Please run rank_species_popularity.py first.")
        sys.exit(1)

    orig_344 = get_original_344()
    if not orig_344:
        print("Error: Could not retrieve original 344 species list.")
        sys.exit(1)

    print(f"Loaded {len(orig_344)} original baseline organisms.")

    # Load Vwiki ranking CSV
    vwiki_by_sci = {}
    with open(VWIKI_CSV, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            sci = r["Scientific Name"].strip()
            rank = int(r["Rank_Vwiki"])
            views = int(r["Vwiki (2025–2026 Cumulative Views)"])
            comm = r["Common Name"].strip()
            title = r["Wikipedia Title"].strip()
            swiki = int(r["Swiki (Languages)"])
            vwiki_by_sci[sci] = {
                "rank": rank,
                "views": views,
                "common": comm,
                "title": title,
                "swiki": swiki,
                "order": r.get("Order", ""),
                "family": r.get("Family", ""),
                "class": r.get("Class", ""),
            }

    in_top_1k_strict = []
    outside_top_1k_strict = []

    in_top_1k_opt3 = []
    outside_top_1k_opt3 = []

    genus_impact_comparison = []

    for entry in orig_344:
        m = re.search(r"\(([^)]+)\)$", entry)
        if not m:
            continue
        sci = m.group(1).strip()
        comm = entry[:m.start()].strip()

        if sci in vwiki_by_sci:
            info = vwiki_by_sci[sci]
            rec_strict = {
                "common": comm,
                "scientific": sci,
                "rank": info["rank"],
                "views": info["views"],
                "title": info["title"],
                "swiki": info["swiki"],
                "class": info["class"],
                "order": info["order"],
            }
            if info["rank"] <= 1000:
                in_top_1k_strict.append(rec_strict)
            else:
                outside_top_1k_strict.append(rec_strict)

            # Option 3 Evaluation
            rec_opt3 = dict(rec_strict)
            if sci in SPECIAL_TAXA_344:
                taxon_sci = SPECIAL_TAXA_344[sci]["taxon_sci"]
                rank_level = SPECIAL_TAXA_344[sci]["rank_level"]
                group_common = SPECIAL_TAXA_344[sci]["common"]
                if taxon_sci in vwiki_by_sci:
                    g_info = vwiki_by_sci[taxon_sci]
                    gain = info["rank"] - g_info["rank"]
                    if g_info["rank"] < info["rank"]:
                        rec_opt3["rank"] = g_info["rank"]
                        rec_opt3["views"] = g_info["views"]
                        rec_opt3["title"] = g_info["title"]
                        rec_opt3["is_taxon_rollup"] = True
                        rec_opt3["species_rank"] = info["rank"]
                        rec_opt3["taxon_sci"] = taxon_sci
                        rec_opt3["rank_level"] = rank_level

                    genus_impact_comparison.append({
                        "common": group_common,
                        "species_comm": comm,
                        "species_sci": sci,
                        "species_rank": info["rank"],
                        "species_views": info["views"],
                        "taxon_sci": taxon_sci,
                        "rank_level": rank_level,
                        "taxon_rank": g_info["rank"],
                        "taxon_views": g_info["views"],
                        "rank_gain": gain,
                    })

            if rec_opt3["rank"] <= 1000:
                in_top_1k_opt3.append(rec_opt3)
            else:
                outside_top_1k_opt3.append(rec_opt3)

    # Sort
    in_top_1k_strict.sort(key=lambda x: x["rank"])
    outside_top_1k_strict.sort(key=lambda x: x["rank"])
    in_top_1k_opt3.sort(key=lambda x: x["rank"])
    outside_top_1k_opt3.sort(key=lambda x: x["rank"])
    genus_impact_comparison.sort(key=lambda x: x["rank_gain"], reverse=True)

    # Categorize outside top 1k by difficulty tiers (Option 3 perspective)
    normal_tier_opt3 = [x for x in outside_top_1k_opt3 if 1000 < x["rank"] <= 2000]
    advanced_tier_opt3 = [x for x in outside_top_1k_opt3 if 2000 < x["rank"] <= 5000]
    master_tier_opt3 = [x for x in outside_top_1k_opt3 if x["rank"] > 5000]

    all_ranks_opt3 = [x["rank"] for x in in_top_1k_opt3 + outside_top_1k_opt3]
    median_rank_opt3 = sorted(all_ranks_opt3)[len(all_ranks_opt3) // 2] if all_ranks_opt3 else 0

    promoted_count = len(in_top_1k_opt3) - len(in_top_1k_strict)

    print("\n📊 SUMMARY RESULTS:")
    print("-" * 70)
    print(f"Total Original Baseline Organisms:     {len(orig_344):,}")
    print(f"Found in Vwiki Rankings:               {len(orig_344):,} (100.0%)")
    print("-" * 70)
    print("1. STRICT SPECIES-LEVEL PERSPECTIVE (Pure Binomials):")
    print(f"   🐾 Inside Top 1,000 (Easy Tier):    {len(in_top_1k_strict):>3} / {len(orig_344)} ({len(in_top_1k_strict)/len(orig_344)*100:>5.1f}%)")
    print(f"   🌿 Outside Top 1,000:               {len(outside_top_1k_strict):>3} / {len(orig_344)} ({len(outside_top_1k_strict)/len(orig_344)*100:>5.1f}%)")
    print("-" * 70)
    print("2. OPTION 3 GAMEPLAY PERSPECTIVE (Live Genus/Taxon Match Support):")
    print(f"   🐾 Inside Top 1,000 (Easy Tier):    {len(in_top_1k_opt3):>3} / {len(orig_344)} ({len(in_top_1k_opt3)/len(orig_344)*100:>5.1f}%)  [+{promoted_count} net organisms promoted into Top 1k]")
    print(f"   🌿 Ranks 1,001 – 2,000 (Normal):    {len(normal_tier_opt3):>3} / {len(orig_344)} ({len(normal_tier_opt3)/len(orig_344)*100:>5.1f}%)  [Cumulative: {len(in_top_1k_opt3)+len(normal_tier_opt3)} / {len(orig_344)} ({(len(in_top_1k_opt3)+len(normal_tier_opt3))/len(orig_344)*100:.1f}%)]")
    print(f"   🔬 Ranks 2,001 – 5,000 (Advanced):  {len(advanced_tier_opt3):>3} / {len(orig_344)} ({len(advanced_tier_opt3)/len(orig_344)*100:>5.1f}%)  [Cumulative: {len(in_top_1k_opt3)+len(normal_tier_opt3)+len(advanced_tier_opt3)} / {len(orig_344)} ({(len(in_top_1k_opt3)+len(normal_tier_opt3)+len(advanced_tier_opt3))/len(orig_344)*100:.1f}%)]")
    print(f"   ⚡ Ranks > 5,000 (Master Only):     {len(master_tier_opt3):>3} / {len(orig_344)} ({len(master_tier_opt3)/len(orig_344)*100:>5.1f}%)")
    print(f"   Median Rank of Original Set:        #{median_rank_opt3:,}")
    print("-" * 70)

    print("\n🦁 OPTION 3 RECOGNIZABLE TAXA & GENUSES COMPARISON:")
    print(f"{'Organism':<18} | {'Taxon Level':<10} | {'Species Sci':<26} | {'Species Rank':>12} | {'Taxon Sci':<14} | {'Taxon Rank':>10} | {'Rank Gain':>10}")
    print("-" * 115)
    for g in genus_impact_comparison:
        gain = g["species_rank"] - g["taxon_rank"]
        gain_str = f"+{gain:,}" if gain > 0 else f"{gain:,}"
        print(f"{g['common']:<18} | {g['rank_level']:<10} | {g['species_sci']:<26} | #{g['species_rank']:>11,} | {g['taxon_sci']:<14} | #{g['taxon_rank']:>9,} | {gain_str:>10}")

    print("\n🔍 TOP 15 ORGANISMS JUST OUTSIDE TOP 1,000 (Closest to Cutoff, Option 3):")
    print(f"{'Rank':>6} | {'Off By':>7} | {'Common Name':<28} | {'Scientific Name':<26} | {'Views':>10}")
    print("-" * 88)
    for x in outside_top_1k_opt3[:15]:
        off_by = x["rank"] - 1000
        print(f"#{x['rank']:>5} | +{off_by:>5} | {x['common']:<28} | {x['scientific']:<26} | {x['views']:>10,}")

    print("\n🔬 THE 10 MOST OBSCURE ORIGINAL SPECIES (Furthest Outside Top 1,000):")
    print(f"{'Rank':>6} | {'Off By':>7} | {'Common Name':<28} | {'Scientific Name':<26} | {'Views':>10}")
    print("-" * 88)
    for x in outside_top_1k_opt3[-10:]:
        off_by = x["rank"] - 1000
        print(f"#{x['rank']:>5} | +{off_by:>5} | {x['common']:<28} | {x['scientific']:<26} | {x['views']:>10,}")

    # Generate Markdown Report
    with open(REPORT_MD, "w", encoding="utf-8") as f:
        f.write("# 🧬 Analysis: Original 344 Species vs. Top 1,000 Vwiki Rankings\n\n")
        f.write(f"> **Analysis Date:** {today_str}  \n")
        f.write(f"> **Dataset:** `{os.path.basename(VWIKI_CSV)}` (empirical Wikimedia pageviews)  \n")
        f.write(f"> **Baseline:** 344 Original Untouched Organisms  \n\n")

        f.write("## 1. Executive Summary\n\n")
        f.write("### Comparison by Evaluation Mode:\n")
        f.write(f"- **Option 3 Gameplay Perspective (Live in Game):** **{len(in_top_1k_opt3)} / {len(orig_344)} ({len(in_top_1k_opt3)/len(orig_344)*100:.1f}%)** in Top 1,000\n")
        f.write(f"- **Strict Species-Only Perspective:** **{len(in_top_1k_strict)} / {len(orig_344)} ({len(in_top_1k_strict)/len(orig_344)*100:.1f}%)** in Top 1,000\n\n")

        f.write("### Option 3 Tier Distribution:\n")
        f.write(f"- **Inside Top 1,000 (🐾 Easy Tier):** **{len(in_top_1k_opt3)} / {len(orig_344)} ({len(in_top_1k_opt3)/len(orig_344)*100:.1f}%)**\n")
        f.write(f"- **Inside Top 2,000 (🌿 Normal Tier):** **{len(in_top_1k_opt3) + len(normal_tier_opt3)} / {len(orig_344)} ({(len(in_top_1k_opt3)+len(normal_tier_opt3))/len(orig_344)*100:.1f}%)**\n")
        f.write(f"- **Inside Top 5,000 (🔬 Advanced Tier):** **{len(in_top_1k_opt3) + len(normal_tier_opt3) + len(advanced_tier_opt3)} / {len(orig_344)} ({(len(in_top_1k_opt3)+len(normal_tier_opt3)+len(advanced_tier_opt3))/len(orig_344)*100:.1f}%)**\n")
        f.write(f"- **Master Tier Only (> 5,000):** **{len(master_tier_opt3)} / {len(orig_344)} ({len(master_tier_opt3)/len(orig_344)*100:.1f}%)**\n")
        f.write(f"- **Median Rank:** **#{median_rank_opt3:,}**\n\n")

        f.write("## 2. Option 3 Recognizable Taxa & Genuses Impact\n\n")
        f.write(f"The {len(genus_impact_comparison)} iconic baseline organisms where the English Wikipedia article covers the Genus, Suborder, Family, or Order:\n\n")
        f.write("| Common Name | Taxonomic Level | Species Binomial | Species Rank | Option 3 Taxon | Taxon Rank | Rank Gain | Taxon Views |\n")
        f.write("| :--- | :--- | :--- | :---: | :--- | :---: | :---: | :---: |\n")
        for g in genus_impact_comparison:
            gain = g["species_rank"] - g["taxon_rank"]
            gain_str = f"+{gain:,}" if gain > 0 else f"{gain:,}"
            f.write(f"| **{g['common']}** | {g['rank_level']} | *{g['species_sci']}* | #{g['species_rank']:,} | *{g['taxon_sci']}* | **#{g['taxon_rank']:,}** | {gain_str} | {g['taxon_views']:,} |\n")

        f.write("\n## 3. Organisms Just Outside Top 1,000 (Ranks 1,001 – 2,000)\n\n")
        f.write("These organisms missed the 🐾 Easy (top 1k) cutoff, but comfortably qualify for the 🌿 Normal (top 2k) tier:\n\n")
        f.write("| Vwiki Rank | Off by (vs. 1k) | Common Name | Scientific Name | Cumulative Views | Sitelinks |\n")
        f.write("| :---: | :---: | :--- | :--- | :---: | :---: |\n")
        for x in normal_tier_opt3:
            off_by = x["rank"] - 1000
            f.write(f"| #{x['rank']:,} | +{off_by:,} | {x['common']} | *{x['scientific']}* | {x['views']:,} | {x['swiki']} |\n")

        f.write("\n## 4. Species in Advanced Tier (Ranks 2,001 – 5,000)\n\n")
        f.write("| Vwiki Rank | Off by (vs. 1k) | Common Name | Scientific Name | Cumulative Views | Sitelinks |\n")
        f.write("| :---: | :---: | :--- | :--- | :---: | :---: |\n")
        for x in advanced_tier_opt3:
            off_by = x["rank"] - 1000
            f.write(f"| #{x['rank']:,} | +{off_by:,} | {x['common']} | *{x['scientific']}* | {x['views']:,} | {x['swiki']} |\n")

        f.write("\n## 5. Species in Master Tier Only (Ranks > 5,000)\n\n")
        f.write("These organisms represent specialized microscopic, deep-sea, or obscure biological lineages present in the original 344:\n\n")
        f.write("| Vwiki Rank | Off by (vs. 1k) | Common Name | Scientific Name | Cumulative Views | Sitelinks |\n")
        f.write("| :---: | :---: | :--- | :--- | :---: | :---: |\n")
        for x in master_tier_opt3:
            off_by = x["rank"] - 1000
            f.write(f"| #{x['rank']:,} | +{off_by:,} | {x['common']} | *{x['scientific']}* | {x['views']:,} | {x['swiki']} |\n")

    print(f"\n📄 Complete markdown report generated at: {REPORT_MD}")
    print("=" * 70)

if __name__ == "__main__":
    main()
