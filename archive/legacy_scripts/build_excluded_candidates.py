# Excluded and deferred animal candidates for manual user review
EXCLUDED_CANDIDATES = [
    # --- Category 1: Subspecies / Taxonomic Duplicate Taxa ---
    {
        "common": "Domestic Dog",
        "scientific": "Canis lupus familiaris",
        "clade": "Mammals",
        "group": "Carnivora / Canidae",
        "category": "Subspecies / Taxonomic Duplicate",
        "reason": "Subspecies of Gray Wolf (Canis lupus, TaxID 9612). Sharing identical LCA branch with wolf creates zero-distance time ambiguities and duplicate taxonomic keys.",
        "action": "Can be merged or treated as distinct domestic entry if custom subspecies resolution is implemented."
    },
    {
        "common": "Dingo",
        "scientific": "Canis lupus dingo",
        "clade": "Mammals",
        "group": "Carnivora / Canidae",
        "category": "Subspecies / Taxonomic Duplicate",
        "reason": "Taxonomic trinomial of Canis lupus. Excluded in favor of the full species Dhole (Cuon alpinus) and African Wild Dog (Lycaon pictus).",
        "action": "Available for manual activation if user wishes to treat dingo as a full standalone species."
    },
    {
        "common": "Barbary Lion",
        "scientific": "Panthera leo leo",
        "clade": "Mammals",
        "group": "Carnivora / Felidae",
        "category": "Subspecies / Taxonomic Duplicate",
        "reason": "Regional subspecies of Lion (Panthera leo). Duplicate branch in TimeTree.",
        "action": "Historical subspecies; user can review."
    },
    {
        "common": "Siberian Tiger / Amur Tiger",
        "scientific": "Panthera tigris altaica",
        "clade": "Mammals",
        "group": "Carnivora / Felidae",
        "category": "Subspecies / Taxonomic Duplicate",
        "reason": "Subspecies of Tiger (Panthera tigris). Tiger is already fully represented in the active catalog.",
        "action": "Subspecies entry; deferred to prevent duplicate Tiger guesses."
    },
    {
        "common": "Bengal Tiger",
        "scientific": "Panthera tigris tigris",
        "clade": "Mammals",
        "group": "Carnivora / Felidae",
        "category": "Subspecies / Taxonomic Duplicate",
        "reason": "Subspecies of Tiger (Panthera tigris). Already represented by species-level Tiger.",
        "action": "Subspecies entry; deferred."
    },
    {
        "common": "Domestic Ferret",
        "scientific": "Mustela putorius furo",
        "clade": "Mammals",
        "group": "Carnivora / Mustelidae",
        "category": "Subspecies / Taxonomic Duplicate",
        "reason": "Domestic form of European Polecat (Mustela putorius). Black-footed Ferret (Mustela nigripes) is included as a distinct wild species instead.",
        "action": "Can be swapped in place of European Polecat if domestic name is preferred."
    },
    {
        "common": "Blue Poison Dart Frog",
        "scientific": "Dendrobates tinctorius azureus",
        "clade": "Amphibians",
        "group": "Anura / Dendrobatidae",
        "category": "Subspecies / Taxonomic Duplicate",
        "reason": "Widely recognized morph/subspecies of Dyeing Dart Frog (Dendrobates tinctorius). Retaining both creates phylogenetic collision at 0 MYA.",
        "action": "Can be added as a synonym or separate entry if morphological morphs are split."
    },
    {
        "common": "Przewalski's Horse",
        "scientific": "Equus ferus przewalskii",
        "clade": "Mammals",
        "group": "Perissodactyla / Equidae",
        "category": "Subspecies / Taxonomic Duplicate",
        "reason": "Subspecies of Equus ferus. Horse lineage already covered by Domestic Horse (Equus caballus).",
        "action": "User can review whether to include wild Equus ferus."
    },

    # --- Category 2: Cryptic or Obscure Species (Lacking Popular Common Name) ---
    {
        "common": "Common Garden Centipede",
        "scientific": "Cryptops hortensis",
        "clade": "Invertebrates",
        "group": "Chilopoda / Scolopendromorpha",
        "category": "Cryptic or Obscure Species",
        "reason": "Small (15-30mm) cryptic soil centipede lacking broad public recognizability. Amazonian Giant Centipede (Scolopendra gigantea) and House Centipede (Scutigera coleoptrata) provide far better gameplay.",
        "action": "User review: keep giant/house centipedes or add garden centipede."
    },
    {
        "common": "California Sea Hare",
        "scientific": "Aplysia californica",
        "clade": "Invertebrates",
        "group": "Gastropoda / Aplysiida",
        "category": "Cryptic or Obscure Species",
        "reason": "Prominent neurobiology laboratory model organism, but relatively obscure as a general guessing puzzle organism compared to Blue Dragon Sea Slug and Spanish Dancer.",
        "action": "User review: valuable for science trivia, can be promoted if requested."
    },
    {
        "common": "Large White / Cabbage White",
        "scientific": "Pieris brassicae",
        "clade": "Invertebrates",
        "group": "Lepidoptera / Pieridae",
        "category": "Cryptic or Obscure Species",
        "reason": "Very plain white butterfly often conflated with Small White (Pieris rapae). Excluded to avoid ambiguous guess confusion.",
        "action": "User review: can be added if Pieridae butterfly diversity is desired."
    },
    {
        "common": "Common Carder Bee",
        "scientific": "Bombus pascuorum",
        "clade": "Invertebrates",
        "group": "Hymenoptera / Apidae",
        "category": "Cryptic or Obscure Species",
        "reason": "Visually subtle bumblebee. Buff-tailed Bumblebee (Bombus terrestris) and Red-tailed Bumblebee (Bombus lapidarius) provide cleaner identification.",
        "action": "Available for bumblebee cluster expansion."
    },
    {
        "common": "Moseley's Velvet Worm",
        "scientific": "Peripatopsis moseleyi",
        "clade": "Invertebrates",
        "group": "Onychophora / Peripatopsidae",
        "category": "Cryptic or Obscure Species",
        "reason": "Obscure South African velvet worm. Epiperipatus biolleyi was selected as the primary Onychophora exemplar.",
        "action": "User review: second onychophoran candidate if needed."
    },
    {
        "common": "Freshwater Planarian (Polychroa)",
        "scientific": "Schmidtea polychroa",
        "clade": "Invertebrates",
        "group": "Platyhelminthes / Tricladida",
        "category": "Cryptic or Obscure Species",
        "reason": "Sister species to Schmidtea mediterranea with virtually indistinguishable morphology to non-specialists.",
        "action": "Duplicate morphological twin deferred."
    },
    {
        "common": "Magna Water Flea",
        "scientific": "Daphnia magna",
        "clade": "Invertebrates",
        "group": "Crustacea / Branchiopoda",
        "category": "Cryptic or Obscure Species",
        "reason": "Sister species to Common Water Flea (Daphnia pulex). Including both 'Water Flea' species creates severe user ambiguity in search dropdown.",
        "action": "Daphnia pulex retained as primary water flea."
    },
    {
        "common": "European Green Toad (Sister)",
        "scientific": "Bufotes balearicus",
        "clade": "Amphibians",
        "group": "Anura / Bufonidae",
        "category": "Cryptic or Obscure Species",
        "reason": "Cryptic Italian/Balaeric sister species to European Green Toad (Bufotes viridis), recently split based solely on mitochondrial DNA.",
        "action": "Cryptic genetic split deferred."
    },

    # --- Category 3: Microscopic / Parasitic Organisms (Playability Deferral) ---
    {
        "common": "Trichina Worm / Pork Worm",
        "scientific": "Trichinella spiralis",
        "clade": "Invertebrates",
        "group": "Nematoda / Trichinellidae",
        "category": "Microscopic / Parasitic Organism",
        "reason": "Intracellular microscopic parasitic roundworm causing trichinosis. Excluded for gameplay tone and lack of macroscopic visual tree intuition.",
        "action": "User review: nematode parasite candidate."
    },
    {
        "common": "Human Pinworm",
        "scientific": "Enterobius vermicularis",
        "clade": "Invertebrates",
        "group": "Nematoda / Oxyuridae",
        "category": "Microscopic / Parasitic Organism",
        "reason": "Obligate human intestinal parasite. Excluded for family-friendly gameplay tone.",
        "action": "Deferred parasitic entry."
    },
    {
        "common": "Liver Fluke",
        "scientific": "Fasciola hepatica",
        "clade": "Invertebrates",
        "group": "Platyhelminthes / Trematoda",
        "category": "Microscopic / Parasitic Organism",
        "reason": "Parasitic flatworm of ruminants and humans. Freshwater planarian (Schmidtea) retained as free-living platyhelminth exemplar.",
        "action": "User review: can be added if parasitic flukes are wanted."
    },
    {
        "common": "Pork Tapeworm",
        "scientific": "Taenia solium",
        "clade": "Invertebrates",
        "group": "Platyhelminthes / Cestoda",
        "category": "Microscopic / Parasitic Organism",
        "reason": "Endoparasitic cestode. Deferring internal human parasites from the primary daily puzzle roster.",
        "action": "User review."
    },
    {
        "common": "Model Nematode (Briggsae)",
        "scientific": "Caenorhabditis briggsae",
        "clade": "Invertebrates",
        "group": "Nematoda / Rhabditidae",
        "category": "Microscopic / Parasitic Organism",
        "reason": "Microscopic soil nematode used as genomics twin to C. elegans. C. elegans already represents the genus.",
        "action": "Duplicate laboratory sister species deferred."
    },
    {
        "common": "Dust Mite",
        "scientific": "Dermatophagoides pteronyssinus",
        "clade": "Invertebrates",
        "group": "Arachnida / Pyroglyphidae",
        "category": "Microscopic / Parasitic Organism",
        "reason": "Microscopic synanthropic arachnid (0.2-0.3mm). Excluded in favor of macroscopic arachnids (spiders, scorpions, ticks).",
        "action": "Can be added if microscopic arachnids are desired."
    },

    # --- Category 4: Deferred Sister Species (Available for Future Expansion Packs) ---
    {
        "common": "American Black Duck",
        "scientific": "Anas rubripes",
        "clade": "Birds",
        "group": "Anseriformes / Anatidae",
        "category": "Deferred Sister Species",
        "reason": "Very close sister species to Mallard (Anas platyrhynchos) with frequent hybridization and <0.5 MYA divergence. Mallard, Pintail, Teal, and Wood Duck already provide rich Anseriformes representation.",
        "action": "High-quality candidate ready for immediate addition if user wants deeper duck clusters."
    },
    {
        "common": "Rough-legged Buzzard",
        "scientific": "Buteo lagopus",
        "clade": "Birds",
        "group": "Accipitriformes / Accipitridae",
        "category": "Deferred Sister Species",
        "reason": "Sister hawk to Red-tailed Hawk (Buteo jamaicensis) and Common Buzzard (Buteo buteo). Deferred to balance raptor diversity across other families (kites, harriers, falcons).",
        "action": "Ready for raptor cluster expansion."
    },
    {
        "common": "Merlin",
        "scientific": "Falco columbarius",
        "clade": "Birds",
        "group": "Falconiformes / Falconidae",
        "category": "Deferred Sister Species",
        "reason": "Small falcon. Falconidae already features Peregrine Falcon, Gyrfalcon, Common Kestrel, and American Kestrel.",
        "action": "Great candidate for a 5-species Falcon cluster."
    },
    {
        "common": "Eurasian Wigeon",
        "scientific": "Mareca penelope",
        "clade": "Birds",
        "group": "Anseriformes / Anatidae",
        "category": "Deferred Sister Species",
        "reason": "Dabbling duck. Deferred to preserve balanced proportions between waterfowl, wading birds, and passerines.",
        "action": "Waterfowl candidate available for manual addition."
    },
    {
        "common": "Sunda Pangolin (Sister)",
        "scientific": "Manis culionensis",
        "clade": "Mammals",
        "group": "Pholidota / Manidae",
        "category": "Deferred Sister Species",
        "reason": "Palawan Pangolin. Sunda Pangolin (Manis javanica) and Ground Pangolin (Smutsia temminckii) provide primary representation for Asian and African pangolins.",
        "action": "Rare island endemic pangolin candidate."
    },
    {
        "common": "Amur Leopard",
        "scientific": "Panthera pardus orientalis",
        "clade": "Mammals",
        "group": "Carnivora / Felidae",
        "category": "Deferred Sister Species",
        "reason": "Critically endangered Far Eastern subspecies of Leopard (Panthera pardus).",
        "action": "Subspecies of Panthera pardus; deferred to avoid duplicate leopard keys."
    },
    {
        "common": "Chilean Recluse Spider",
        "scientific": "Loxosceles laeta",
        "clade": "Invertebrates",
        "group": "Araneae / Sicariidae",
        "category": "Deferred Sister Species",
        "reason": "South American sister species to Brown Recluse (Loxosceles reclusa). Brown recluse is already included.",
        "action": "Sister recluse spider candidate."
    },
    {
        "common": "Spotted Hyena (Sister / Fossil)",
        "scientific": "Crocuta crocuta spelaea",
        "clade": "Mammals",
        "group": "Carnivora / Hyaenidae",
        "category": "Deferred Sister Species",
        "reason": "Extinct Cave Hyena subspecies. Roster focused on extant species with living phylogenetic observation data.",
        "action": "Prehistoric/extinct candidate."
    },
    {
        "common": "Drosophila simulans",
        "scientific": "Drosophila simulans",
        "clade": "Invertebrates",
        "group": "Diptera / Drosophilidae",
        "category": "Deferred Sister Species",
        "reason": "Cryptic sister fruit fly to Drosophila melanogaster. Diverged ~2.5 MYA but visually nearly identical.",
        "action": "Genetic twin fruit fly deferred."
    },
    {
        "common": "Lesser Flamingo",
        "scientific": "Phoeniconaias minor",
        "clade": "Birds",
        "group": "Phoenicopteriformes / Phoenicopteridae",
        "category": "Deferred Sister Species",
        "reason": "Sister flamingo. Greater Flamingo and American Flamingo already anchor the Phoenicopteridae family.",
        "action": "Available for 3-species flamingo cluster."
    },

    # --- Category 5: Non-Animal / Protist / Questionable Clade Candidates ---
    {
        "common": "Slime Mold (Dictyostelium)",
        "scientific": "Dictyostelium discoideum",
        "clade": "Non-Animal / Protist",
        "group": "Amoebozoa / Dictyosteliida",
        "category": "Non-Animal or Disputed Classification",
        "reason": "Amoebozoan slime mold, outside Kingdom Animalia (Metazoa). Phylogenle is strictly dedicated to Animalia.",
        "action": "Permanently excluded from Animalia game."
    },
    {
        "common": "Green Alga (Volvox)",
        "scientific": "Volvox carteri",
        "clade": "Non-Animal / Protist",
        "group": "Chlorophyta / Volvocales",
        "category": "Non-Animal or Disputed Classification",
        "reason": "Colonial chlorophyte green alga (Plantae/Viridiplantae). Outside Metazoa.",
        "action": "Permanently excluded."
    },
    {
        "common": "Giardia",
        "scientific": "Giardia duodenalis",
        "clade": "Non-Animal / Protist",
        "group": "Metamonada / Diplomonadida",
        "category": "Non-Animal or Disputed Classification",
        "reason": "Single-celled flagellated diplomonad parasite. Non-metazoan protist.",
        "action": "Permanently excluded."
    },
    {
        "common": "Yeast",
        "scientific": "Saccharomyces cerevisiae",
        "clade": "Non-Animal / Fungi",
        "group": "Ascomycota / Saccharomycetales",
        "category": "Non-Animal or Disputed Classification",
        "reason": "Fungal model organism. Excluded as game is strictly animal taxonomy.",
        "action": "Permanently excluded."
    }
]

if __name__ == "__main__":
    print(f"Loaded {len(EXCLUDED_CANDIDATES)} excluded/deferred candidates for manual review.")

# Additional screened & categorized candidates for manual review
EXCLUDED_CANDIDATES.extend([
    # Subspecies & Synonyms
    {
        "common": "Kodiak Bear",
        "scientific": "Ursus arctos middendorffi",
        "clade": "Mammals",
        "group": "Carnivora / Ursidae",
        "category": "Subspecies / Taxonomic Duplicate",
        "reason": "Subspecies of Brown Bear (Ursus arctos). Brown Bear is already included.",
        "action": "Subspecies of Ursus arctos; deferred to avoid duplicate bear keys."
    },
    {
        "common": "Northwestern Crow",
        "scientific": "Corvus caurinus",
        "clade": "Birds",
        "group": "Passeriformes / Corvidae",
        "category": "Subspecies / Taxonomic Duplicate",
        "reason": "Recently lumped into American Crow (Corvus brachyrhynchos) by the American Ornithological Society based on genomic data.",
        "action": "Lumped junior synonym; American Crow retained."
    },
    {
        "common": "Myrtle Warbler",
        "scientific": "Setophaga coronata coronata",
        "clade": "Birds",
        "group": "Passeriformes / Parulidae",
        "category": "Subspecies / Taxonomic Duplicate",
        "reason": "Subspecies of Yellow-rumped Warbler (Setophaga coronata). Full species Setophaga coronata is included.",
        "action": "Subspecies entry deferred."
    },
    {
        "common": "Africanized Honey Bee / Killer Bee",
        "scientific": "Apis mellifera scutellata x",
        "clade": "Invertebrates",
        "group": "Hymenoptera / Apidae",
        "category": "Subspecies / Taxonomic Duplicate",
        "reason": "Hybrid lineage of Apis mellifera. Western Honey Bee is already in the catalog.",
        "action": "Domestic/feral hybrid deferred."
    },
    {
        "common": "Indonesian Coelacanth",
        "scientific": "Latimeria menadoensis",
        "clade": "Fishes",
        "group": "Coelacanthiformes / Latimeriidae",
        "category": "Deferred Sister Species",
        "reason": "Cryptic sister species to West Indian Ocean Coelacanth (Latimeria chalumnae). Diverged ~20-30 MYA. Kept as prime candidate if 2-species coelacanth cluster is desired.",
        "action": "Ready for manual promotion if player requests coelacanth pair."
    },
    {
        "common": "Cuban Crocodile",
        "scientific": "Crocodylus rhombifer",
        "clade": "Reptiles",
        "group": "Crocodylia / Crocodylidae",
        "category": "Deferred Sister Species",
        "reason": "Critically endangered endemic Cuban crocodile. American, Nile, Saltwater, and Mugger crocodiles already represent Crocodylus.",
        "action": "Available for expanded crocodile pack."
    },
    {
        "common": "Irukandji Box Jellyfish",
        "scientific": "Malo kingi",
        "clade": "Invertebrates",
        "group": "Cubozoa / Carukiidae",
        "category": "Cryptic or Obscure Species",
        "reason": "Extremely tiny (1 cubic cm), nearly invisible box jellyfish. Sea Wasp Box Jellyfish (Chironex fleckeri) represents Cubozoa with macroscopic fame.",
        "action": "Available if hyper-venomous marine pack is desired."
    },
    {
        "common": "Sea Lamprey",
        "scientific": "Petromyzon marinus",
        "clade": "Fishes",
        "group": "Petromyzontiformes / Petromyzontidae",
        "category": "Deferred Sister Species",
        "reason": "Jawless cyclostome fish (Agnatha). Diverged before jawed vertebrates (~500 MYA). Excellent candidate for jawless vertebrate branch.",
        "action": "User review: can be added as the basal-most living fish."
    },
    {
        "common": "Atlantic Hagfish",
        "scientific": "Myxine glutinosa",
        "clade": "Fishes",
        "group": "Myxiniformes / Myxinidae",
        "category": "Deferred Sister Species",
        "reason": "Deep-sea slime-producing jawless hagfish. Kept aside for manual user confirmation of tone.",
        "action": "Basal cyclostome candidate; user review."
    },
    {
        "common": "Thylacine / Tasmanian Tiger",
        "scientific": "Thylacinus cynocephalus",
        "clade": "Mammals",
        "group": "Dasyuromorphia / Thylacinidae",
        "category": "Deferred Sister Species",
        "reason": "Extinct marsupial carnivore (declared extinct 1936). Game focuses on extant biodiversity, but highly requested historical animal.",
        "action": "User review: can be promoted if recent historical extinctions are permitted."
    },
    {
        "common": "Dodo",
        "scientific": "Raphus cucullatus",
        "clade": "Birds",
        "group": "Columbiformes / Columbidae",
        "category": "Deferred Sister Species",
        "reason": "Extinct flightless columbid bird (extinct late 17th century). Excluded to keep pool to living species.",
        "action": "User review: prime candidate if iconic extinct animals are allowed."
    },
    {
        "common": "Passenger Pigeon",
        "scientific": "Ectopistes migratorius",
        "clade": "Birds",
        "group": "Columbiformes / Columbidae",
        "category": "Deferred Sister Species",
        "reason": "Extinct North American columbid (extinct 1914).",
        "action": "User review: historic extinction."
    },
    {
        "common": "Giant Intestinal Roundworm",
        "scientific": "Ascaris lumbricoides",
        "clade": "Invertebrates",
        "group": "Nematoda / Ascarididae",
        "category": "Microscopic / Parasitic Organism",
        "reason": "Large human intestinal parasitic nematode. Excluded for game tone.",
        "action": "Parasitic roundworm candidate."
    },
    {
        "common": "Blood Fluke (Schistosoma)",
        "scientific": "Schistosoma mansoni",
        "clade": "Invertebrates",
        "group": "Platyhelminthes / Schistosomatidae",
        "category": "Microscopic / Parasitic Organism",
        "reason": "Human blood parasite causing schistosomiasis. Excluded from general wildlife puzzle.",
        "action": "Deferred medical parasite."
    }
])
