# 📋 Plan: Hierarchical Taxonomic Species Catalog

**Document:** `docs/TAXONOMIC_CATALOG_PLAN.md`  
**Target Output File:** `species_catalog_taxonomic.md`  
**Status:** Pending User Sign-Off  
**Target Pool:** Exactly 29,748 Species Across All Domains & Kingdoms of Life  

---

## 1. Executive Summary & Objective

In the current game, [`species_catalog.md`](../species_catalog.md) organizes organisms into broad informal categories (Mammals, Birds, Reptiles, Amphibians, Fishes, Invertebrates, Plants, Fungi, Bacteria, Protists, Viruses) with flat order listings. While functional, this layout is suboptimal for players deducing mystery organisms:
1. **No True Taxonomic Hierarchy**: For example, fish classes (`Actinopterygii`, `Chondrichthyes`, `Sarcopterygii`) or vertebrate phyla (`Chordata`) are flattened or grouped broadly rather than reflecting evolutionary taxonomy.
2. **Endless Scrolling**: Players who deduce that the mystery organism is a fish or plant currently have to scroll through thousands of mammals and birds.
3. **Player Deduction Tool**: Phylogenle gives taxonomic LCA feedback (Domain, Kingdom, Phylum, Class, Order, Family, Genus). A catalog reflecting this exact Linnaean structure allows players to drill down directly into the relevant clade.

### Core Commitments
- **Zero-Modification of Existing File**: [`species_catalog.md`](../species_catalog.md) remains **100% untouched**.
- **New Catalog File**: A brand new file named [`species_catalog_taxonomic.md`](../species_catalog_taxonomic.md) will be generated.
- **Zero-Drop Guarantee**: Every single one of the 29,748 species will be preserved.
- **Sum-Check Verification**: A strict automated sum check and set-equality check must pass before finalizing.
- **Collapsed by Default**: All sections will be wrapped in native collapsible `<details><summary>` HTML tags without `open`, starting collapsed so users can drill down without visual clutter.

---

## 2. Taxonomic Architecture & 8-Rank Game Alignment

The catalog directly mirrors the game's official 8-rank taxonomic divergence and emoji feedback system:

| Rank Icon | Taxonomic Rank | Role in Game / Deductive Progression |
| :---: | :--- | :--- |
| ⬛ | **Domain** | Outermost evolutionary divergence (Eukaryota, Bacteria, Viruses) |
| 🟫 | **Kingdom** | Primary clade branch (Animalia, Plantae, Fungi, Protista, Bacillati, Pseudomonadati) |
| 🟦 | **Phylum** | Major structural body plan (Chordata, Arthropoda, Mollusca, Streptophyta, etc.) |
| 🟪 | **Class** | Major taxonomic class (Mammalia, Aves, Reptilia, Amphibia, Actinopterygii, Insecta) |
| 🟥 | **Order** | Distinct lineage order (Carnivora, Primates, Passeriformes, Perciformes, etc.) |
| 🟧 | **Family** | Closely related biological family (Felidae, Canidae, Pomacentridae, etc.) |
| 🟨 | **Genus** | Taxonomic genus (*Panthera*, *Homo*, *Amphiprion*, etc.) |
| 🟩 | **Species** | Exact mystery organism match |

### Hierarchy Layers

```
Layer 1: ⬛ Domain (Eukaryota, Bacteria, Viruses)
  └── Layer 2: 🟫 Kingdom (Animalia, Plantae, Fungi, Protista, Pseudomonadati, Bacillati, Heunggongvirae)
        └── Layer 3: 🟦 Phylum (Chordata, Arthropoda, Mollusca, Streptophyta, etc.)
              └── Layer 4: 🟪 Class (Mammalia, Aves, Reptilia, Amphibia, Actinopterygii, Insecta, etc.)
                    └── Layer 5: 🟥 Order (Carnivora, Primates, Passeriformes, Perciformes, etc.)
                          └── Layer 6: 🟧 Family (Felidae, Hominidae, Pomacentridae, etc.)
                                └── Layer 7 & 8: 🟨 Genus & 🟩 Species Table
```

### Exact Domain & Kingdom Breakdown (Total: 29,748 Species)

| ⬛ Domain | 🟫 Kingdom | Primary Phyla Included | Total Species |
| :--- | :--- | :--- | :--- |
| **⬛ Eukaryota** | **🟫 Animalia (Metazoa)** | Chordata, Arthropoda, Mollusca, Echinodermata, Annelida, Cnidaria, Porifera, Nematoda, etc. | **27,792** |
| **⬛ Eukaryota** | **🟫 Plantae (Viridiplantae)** | Streptophyta (Angiosperms, Gymnosperms, Ferns, Mosses), Chlorophyta | **1,862** |
| **⬛ Eukaryota** | **🟫 Fungi** | Ascomycota, Basidiomycota, Mucoromycota, Chytridiomycota | **55** |
| **⬛ Eukaryota** | **🟫 Protista / Chromista** | Rhodophyta, Ochrophyta, Amoebozoa, Haptophyta | **17** |
| **⬛ Bacteria** | **🟫 Pseudomonadati** | Pseudomonadota (Gram-negative bacteria) | **16** |
| **⬛ Bacteria** | **🟫 Bacillati** | Bacillota, Mycoplasmatota, Actinomycetota | **4** |
| **⬛ Viruses** | **🟫 Heunggongvirae** | Herpesvirales | **2** |
| **Total Universal Pool** | | **All 8 Taxonomic Ranks Across All Life** | **29,748** |

---

## 3. Collapsible Formatting Specification

To ensure fast rendering, effortless navigation, and minimal scrolling, every hierarchical layer will use native `<details>` and `<summary>` tags **collapsed by default**:

```html
<details>
<summary>⬛ <b>Domain: Eukaryota</b> — 29,726 Species</summary>

  <details>
  <summary>🟫 <b>Kingdom: Animalia (Metazoa)</b> — 27,792 Species</summary>

    <details>
    <summary>🟦 <b>Phylum: Chordata</b> — 22,800 Species</summary>

      <details>
      <summary>🟪 <b>Class: Actinopterygii (Ray-finned Fishes)</b> — 9,862 Species</summary>

        <details>
        <summary>🟥 <b>Order: Perciformes (Perch-like Fishes)</b> — 2,410 Species</summary>

          <details>
          <summary>🟧 <b>Family: Pomacentridae (Damselfishes & Clownfishes)</b> — 28 Species</summary>

| Common Name | Scientific Name | 🟨 Genus |
| :--- | :--- | :--- |
| Clown Anemonefish | *Amphiprion ocellaris* | *Amphiprion* |
| Orange Clownfish | *Amphiprion percula* | *Amphiprion* |
| Tomato Clownfish | *Amphiprion frenatus* | *Amphiprion* |

          </details>
        </details>
      </details>

      <details>
      <summary>🟪 <b>Class: Mammalia (Mammals)</b> — 4,343 Species</summary>
      ...
      </details>
    </details>

    <details>
    <summary>🟦 <b>Phylum: Arthropoda (Insects, Arachnids, Crustaceans)</b> — 4,120 Species</summary>
    ...
    </details>
  </details>

  <details>
  <summary>🟫 <b>Kingdom: Plantae (Viridiplantae)</b> — 1,862 Species</summary>
  ...
  </details>
</details>

<details>
<summary>⬛ <b>Domain: Bacteria</b> — 20 Species</summary>
...
</details>

<details>
<summary>⬛ <b>Domain: Viruses</b> — 2 Species</summary>
...
</details>
```

### Why this structure is superior:
1. **Instant Filtering**: If a player guesses a bird and the game says `LCA: Class Actinopterygii (TMRCA: 435 Mya)`, the player immediately knows the target is a ray-finned fish. They expand `Animalia` ➔ `Chordata` ➔ `Actinopterygii`, completely ignoring mammals, birds, reptiles, amphibians, and invertebrates.
2. **Zero Clutter**: When opened, only the top-level Kingdoms are visible. Expanding a section reveals its immediate sub-branches cleanly.
3. **Markdown & In-App Compatibility**: `<details><summary>` is 100% supported by GitHub Markdown, standard markdown previewers, and `marked.js` inside our web app.

---

## 4. Verification & Sum-Check Methodology

To guarantee that **not a single animal or organism is left out**, we will execute an automated Python verification script:

### Check 1: Exact Total Count Sum-Check
$$\sum \text{Species in } \texttt{species\_catalog\_taxonomic.md} \equiv 29,748$$

### Check 2: Strict Set Equality Check
$$\text{Set}(\text{Species in } \texttt{species\_catalog.md}) \setminus \text{Set}(\text{Species in } \texttt{species\_catalog\_taxonomic.md}) = \emptyset$$
- The set difference must be strictly empty.
- Every single Latin scientific name and common name present in the old catalog must exist in the new catalog.

### Check 3: Baseline Organisms Guarantee
- All 344 original Metazoa baseline species (Human, Blue Whale, Platypus, Wolf, Cheetah, etc.) are explicitly checked and verified present in their proper taxonomic families.

---

## 5. Web App Integration

Once `species_catalog_taxonomic.md` is generated and verified:
1. The in-app Catalog modal in `script.js` will read `species_catalog_taxonomic.md`.
2. The search input will remain active: searching for any common or scientific name (e.g. `Panthera` or `Clownfish`) will filter the tree and auto-expand matching `<details>` branches.
3. The original `species_catalog.md` remains completely intact in the repository root as an untouched reference.

---

## 6. Sign-Off Checklist for User

- [ ] Structure: ⬛ Domain ➔ 🟫 Kingdom ➔ 🟦 Phylum ➔ 🟪 Class ➔ 🟥 Order ➔ 🟧 Family ➔ 🟨 Genus ➔ 🟩 Species.
- [ ] Behavior: All branches collapsed by default using `<details><summary>`.
- [ ] File Safety: Existing `species_catalog.md` remains 100% untouched; new file is `species_catalog_taxonomic.md`.
- [ ] Verification: Sum check of 29,748 species with zero omissions verified by automated script.
