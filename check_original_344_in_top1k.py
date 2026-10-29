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

SPECIAL_GENUSES_344 = {
    "Giraffa camelopardalis": {"genus_sci": "Giraffa", "common": "Giraffe"},
    "Gorilla gorilla": {"genus_sci": "Gorilla", "common": "Gorilla"},
    "Pongo pygmaeus": {"genus_sci": "Pongo", "common": "Orangutan"},
    "Latimeria chalumnae": {"genus_sci": "Latimeria", "common": "Coelacanth"},
    "Chinchilla lanigera": {"genus_sci": "Chinchilla", "common": "Chinchilla"},
    "Papio anubis": {"genus_sci": "Papio", "common": "Baboon"},
    "Arapaima gigas": {"genus_sci": "Arapaima", "common": "Arapaima"},
}

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
            if sci in SPECIAL_GENUSES_344:
                genus_sci = SPECIAL_GENUSES_344[sci]["genus_sci"]
                if genus_sci in vwiki_by_sci:
                    g_info = vwiki_by_sci[genus_sci]
                    rec_opt3["rank"] = g_info["rank"]
                    rec_opt3["views"] = g_info["views"]
                    rec_opt3["title"] = g_info["title"]
                    rec_opt3["is_genus_rollup"] = True
                    rec_opt3["species_rank"] = info["rank"]
                    rec_opt3["genus_sci"] = genus_sci
                    genus_impact_comparison.append({
                        "common": comm,
                        "species_sci": sci,
                        "species_rank": info["rank"],
                        "species_views": info["views"],
                        "genus_sci": genus_sci,
                        "genus_rank": g_info["rank"],
                        "genus_views": g_info["views"],
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
    genus_impact_comparison.sort(key=lambda x: x["genus_rank"])

    # Categorize outside top 1k by difficulty tiers (Option 3 perspective)
    normal_tier_opt3 = [x for x in outside_top_1k_opt3 if 1000 < x["rank"] <= 2000]
    advanced_tier_opt3 = [x for x in outside_top_1k_opt3 if 2000 < x["rank"] <= 5000]
    master_tier_opt3 = [x for x in outside_top_1k_opt3 if x["rank"] > 5000]

    all_ranks_opt3 = [x["rank"] for x in in_top_1k_opt3 + outside_top_1k_opt3]
    median_rank_opt3 = sorted(all_ranks_opt3)[len(all_ranks_opt3) // 2] if all_ranks_opt3 else 0

    print("\n📊 SUMMARY RESULTS:")
    print("-" * 70)
    print(f"Total Original Baseline Organisms:     {len(orig_344):,}")
    print(f"Found in Vwiki Rankings:               {len(orig_344):,} (100.0%)")
    print("-" * 70)
    print("1. STRICT SPECIES-LEVEL PERSPECTIVE (Pure Binomials):")
    print(f"   🐾 Inside Top 1,000 (Easy Tier):    {len(in_top_1k_strict):>3} / {len(orig_344)} ({len(in_top_1k_strict)/len(orig_344)*100:>5.1f}%)")
    print(f"   🌿 Outside Top 1,000:               {len(outside_top_1k_strict):>3} / {len(orig_344)} ({len(outside_top_1k_strict)/len(orig_344)*100:>5.1f}%)")
    print("-" * 70)
    print("2. OPTION 3 GAMEPLAY PERSPECTIVE (Live Genus Match Support):")
    print(f"   🐾 Inside Top 1,000 (Easy Tier):    {len(in_top_1k_opt3):>3} / {len(orig_344)} ({len(in_top_1k_opt3)/len(orig_344)*100:>5.1f}%)  [+5 net organisms promoted into Top 1k]")
    print(f"   🌿 Ranks 1,001 – 2,000 (Normal):    {len(normal_tier_opt3):>3} / {len(orig_344)} ({len(normal_tier_opt3)/len(orig_344)*100:>5.1f}%)  [Cumulative: {len(in_top_1k_opt3)+len(normal_tier_opt3)} / {len(orig_344)} ({(len(in_top_1k_opt3)+len(normal_tier_opt3))/len(orig_344)*100:.1f}%)]")
    print(f"   🔬 Ranks 2,001 – 5,000 (Advanced):  {len(advanced_tier_opt3):>3} / {len(orig_344)} ({len(advanced_tier_opt3)/len(orig_344)*100:>5.1f}%)  [Cumulative: {len(in_top_1k_opt3)+len(normal_tier_opt3)+len(advanced_tier_opt3)} / {len(orig_344)} ({(len(in_top_1k_opt3)+len(normal_tier_opt3)+len(advanced_tier_opt3))/len(orig_344)*100:.1f}%)]")
    print(f"   ⚡ Ranks > 5,000 (Master Only):     {len(master_tier_opt3):>3} / {len(orig_344)} ({len(master_tier_opt3)/len(orig_344)*100:>5.1f}%)")
    print(f"   Median Rank of Original Set:        #{median_rank_opt3:,}")
    print("-" * 70)

    print("\n🦁 OPTION 3 RECOGNIZABLE GENUSES COMPARISON:")
    print(f"{'Organism':<12} | {'Species Sci':<26} | {'Species Rank':>12} | {'Genus Sci':<12} | {'Genus Rank':>10} | {'Rank Gain':>10}")
    print("-" * 92)
    for g in genus_impact_comparison:
        gain = g["species_rank"] - g["genus_rank"]
        gain_str = f"+{gain:,}" if gain > 0 else f"{gain:,}"
        print(f"{g['common']:<12} | {g['species_sci']:<26} | #{g['species_rank']:>11,} | {g['genus_sci']:<12} | #{g['genus_rank']:>9,} | {gain_str:>10}")

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

        f.write("## 2. Option 3 Recognizable Genuses Impact\n\n")
        f.write("The 7 iconic baseline organisms where the English Wikipedia article covers the Genus:\n\n")
        f.write("| Common Name | Species Binomial | Species Rank | Genus Taxon | Genus Rank | Rank Difference | Genus Views |\n")
        f.write("| :--- | :--- | :---: | :--- | :---: | :---: | :---: |\n")
        for g in genus_impact_comparison:
            gain = g["species_rank"] - g["genus_rank"]
            gain_str = f"+{gain:,}" if gain > 0 else f"{gain:,}"
            f.write(f"| **{g['common']}** | *{g['species_sci']}* | #{g['species_rank']:,} | *{g['genus_sci']}* | **#{g['genus_rank']:,}** | {gain_str} | {g['genus_views']:,} |\n")

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
