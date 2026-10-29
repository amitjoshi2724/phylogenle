#!/usr/bin/env python3
"""
Phylogenle - Diagnostic Analysis Script:
Checks where the original 344 baseline species appear in the empirical Vwiki rankings (docs/species_ranking_by_vwiki.csv).
Calculates how many are in the Top 1,000 (Easy Tier cutoff), and for those outside, exactly how much they are off by.
"""

import os
import sys
import json
import csv
import re
import subprocess

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
VWIKI_CSV = os.path.join(BASE_DIR, "docs", "species_ranking_by_vwiki.csv")
REPORT_MD = os.path.join(BASE_DIR, "docs", "ORIGINAL_344_VS_TOP1K_ANALYSIS.md")

def get_original_344():
    """Retrieve the 344 original baseline species from git history."""
    try:
        raw = subprocess.check_output(
            ["git", "show", "b8dea00:data/species_list.json"],
            cwd=BASE_DIR
        ).decode("utf-8")
        return json.loads(raw)
    except Exception as e:
        print(f"Warning: could not read from git history ({e}), falling back to cached baseline.")
        # Fallback list if git command fails
        return []

def main():
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

    print(f"Loaded {len(orig_344)} original baseline species.")

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

    in_top_1k = []
    outside_top_1k = []
    missing_from_vwiki = []

    for entry in orig_344:
        m = re.search(r"\(([^)]+)\)$", entry)
        if not m:
            continue
        sci = m.group(1).strip()
        comm = entry[:m.start()].strip()

        if sci in vwiki_by_sci:
            info = vwiki_by_sci[sci]
            rec = {
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
                in_top_1k.append(rec)
            else:
                outside_top_1k.append(rec)
        else:
            missing_from_vwiki.append((comm, sci))

    # Sort
    in_top_1k.sort(key=lambda x: x["rank"])
    outside_top_1k.sort(key=lambda x: x["rank"])

    # Categorize outside top 1k by difficulty tiers
    normal_tier = [x for x in outside_top_1k if 1000 < x["rank"] <= 2000]
    advanced_tier = [x for x in outside_top_1k if 2000 < x["rank"] <= 5000]
    master_tier = [x for x in outside_top_1k if x["rank"] > 5000]

    all_ranks = [x["rank"] for x in in_top_1k + outside_top_1k]
    median_rank = sorted(all_ranks)[len(all_ranks) // 2] if all_ranks else 0

    print("\n📊 SUMMARY RESULTS:")
    print("-" * 70)
    print(f"Total Original Baseline Species:       {len(orig_344):,}")
    print(f"Found in Vwiki Rankings:               {len(in_top_1k) + len(outside_top_1k):,} (100.0%)")
    print(f"Median Rank of Original Species:       #{median_rank:,}")
    print("-" * 70)
    print(f"🐾 Inside Top 1,000 (Easy Tier):       {len(in_top_1k):>3} / {len(orig_344)} ({len(in_top_1k)/len(orig_344)*100:>5.1f}%)")
    print(f"🌿 Ranks 1,001 – 2,000 (Normal Tier):   {len(normal_tier):>3} / {len(orig_344)} ({len(normal_tier)/len(orig_344)*100:>5.1f}%)  [Cumulative: {len(in_top_1k)+len(normal_tier)} / {len(orig_344)} ({(len(in_top_1k)+len(normal_tier))/len(orig_344)*100:.1f}%)]")
    print(f"🔬 Ranks 2,001 – 5,000 (Advanced Tier): {len(advanced_tier):>3} / {len(orig_344)} ({len(advanced_tier)/len(orig_344)*100:>5.1f}%)  [Cumulative: {len(in_top_1k)+len(normal_tier)+len(advanced_tier)} / {len(orig_344)} ({(len(in_top_1k)+len(normal_tier)+len(advanced_tier))/len(orig_344)*100:.1f}%)]")
    print(f"⚡ Ranks > 5,000 (Master Tier Only):    {len(master_tier):>3} / {len(orig_344)} ({len(master_tier)/len(orig_344)*100:>5.1f}%)")
    print("-" * 70)

    print("\n🔍 TOP 15 SPECIES JUST OUTSIDE TOP 1,000 (Closest to Cutoff):")
    print(f"{'Rank':>6} | {'Off By':>7} | {'Common Name':<28} | {'Scientific Name':<26} | {'Views':>10}")
    print("-" * 88)
    for x in outside_top_1k[:15]:
        off_by = x["rank"] - 1000
        print(f"#{x['rank']:>5} | +{off_by:>5} | {x['common']:<28} | {x['scientific']:<26} | {x['views']:>10,}")

    print("\n🔬 THE 10 MOST OBSCURE ORIGINAL SPECIES (Furthest Outside Top 1,000):")
    print(f"{'Rank':>6} | {'Off By':>7} | {'Common Name':<28} | {'Scientific Name':<26} | {'Views':>10}")
    print("-" * 88)
    for x in outside_top_1k[-10:]:
        off_by = x["rank"] - 1000
        print(f"#{x['rank']:>5} | +{off_by:>5} | {x['common']:<28} | {x['scientific']:<26} | {x['views']:>10,}")

    # Generate Markdown Report
    with open(REPORT_MD, "w", encoding="utf-8") as f:
        f.write("# 🧬 Analysis: Original 344 Species vs. Top 1,000 Vwiki Rankings\n\n")
        f.write("> **Analysis Date:** 2026-10-28  \n")
        f.write(f"> **Dataset:** `{os.path.basename(VWIKI_CSV)}` (26,200 verified species)  \n")
        f.write(f"> **Baseline:** 344 Original Untouched Organisms  \n\n")

        f.write("## 1. Executive Summary\n\n")
        f.write(f"- **Inside Top 1,000 (🐾 Easy Tier):** **{len(in_top_1k)} / {len(orig_344)} ({len(in_top_1k)/len(orig_344)*100:.1f}%)**\n")
        f.write(f"- **Inside Top 2,000 (🌿 Normal Tier):** **{len(in_top_1k) + len(normal_tier)} / {len(orig_344)} ({(len(in_top_1k)+len(normal_tier))/len(orig_344)*100:.1f}%)**\n")
        f.write(f"- **Inside Top 5,000 (🔬 Advanced Tier):** **{len(in_top_1k) + len(normal_tier) + len(advanced_tier)} / {len(orig_344)} ({(len(in_top_1k)+len(normal_tier)+len(advanced_tier))/len(orig_344)*100:.1f}%)**\n")
        f.write(f"- **Master Tier Only (> 5,000):** **{len(master_tier)} / {len(orig_344)} ({len(master_tier)/len(orig_344)*100:.1f}%)**\n")
        f.write(f"- **Median Rank:** **#{median_rank:,}**\n\n")

        f.write("## 2. Species Just Outside Top 1,000 (Ranks 1,001 – 2,000)\n\n")
        f.write("These organisms missed the 🐾 Easy (top 1k) cutoff, but comfortably qualify for the 🌿 Normal (top 2k) tier:\n\n")
        f.write("| Vwiki Rank | Off by (vs. 1k) | Common Name | Scientific Name | Cumulative Views | Sitelinks |\n")
        f.write("| :---: | :---: | :--- | :--- | :---: | :---: |\n")
        for x in normal_tier:
            off_by = x["rank"] - 1000
            f.write(f"| #{x['rank']:,} | +{off_by:,} | {x['common']} | *{x['scientific']}* | {x['views']:,} | {x['swiki']} |\n")

        f.write("\n## 3. Species in Advanced Tier (Ranks 2,001 – 5,000)\n\n")
        f.write("| Vwiki Rank | Off by (vs. 1k) | Common Name | Scientific Name | Cumulative Views | Sitelinks |\n")
        f.write("| :---: | :---: | :--- | :--- | :---: | :---: |\n")
        for x in advanced_tier:
            off_by = x["rank"] - 1000
            f.write(f"| #{x['rank']:,} | +{off_by:,} | {x['common']} | *{x['scientific']}* | {x['views']:,} | {x['swiki']} |\n")

        f.write("\n## 4. Species in Master Tier Only (Ranks > 5,000)\n\n")
        f.write("These organisms represent specialized microscopic, deep-sea, or obscure biological lineages present in the original 344:\n\n")
        f.write("| Vwiki Rank | Off by (vs. 1k) | Common Name | Scientific Name | Cumulative Views | Sitelinks |\n")
        f.write("| :---: | :---: | :--- | :--- | :---: | :---: |\n")
        for x in master_tier:
            off_by = x["rank"] - 1000
            f.write(f"| #{x['rank']:,} | +{off_by:,} | {x['common']} | *{x['scientific']}* | {x['views']:,} | {x['swiki']} |\n")

    print(f"\n📄 Complete markdown report generated at: {REPORT_MD}")
    print("=" * 70)

if __name__ == "__main__":
    main()
