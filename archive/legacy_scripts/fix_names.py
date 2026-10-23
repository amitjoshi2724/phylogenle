import re

better_names = {
    "Crab": "Blue Crab",
    "Lobster": "American Lobster",
    "Shrimp": "Giant Tiger Prawn",
    "Spider": "Black Widow Spider",
    "Scorpion": "Emperor Scorpion",
    "Centipede": "Amazonian Giant Centipede",
    "Millipede": "Giant African Millipede",
    "Ant": "Red Imported Fire Ant",
    "Bee": "Western Honey Bee",
    "Wasp": "Common Wasp",
    "Butterfly": "Monarch Butterfly",
    "Moth": "Domestic Silk Moth",
    "Beetle": "Seven-spot Ladybird",
    "Fly": "Housefly",
    "Mosquito": "African Malaria Mosquito",
    "Cockroach": "American Cockroach",
    "Earthworm": "Common Earthworm",
    "Jellyfish": "Moon Jelly",
    "Starfish": "Common Starfish",
    "Sea Urchin": "Purple Sea Urchin",
    "Frog": "Common Frog",
    "Toad": "Common Toad",
    "Salamander": "Fire Salamander",
    "Newt": "Smooth Newt",
    "Shark": "Great White Shark",
    "Tuna": "Atlantic Bluefin Tuna",
    "Salmon": "Atlantic Salmon",
    "Carp": "Common Carp",
    "Trout": "Rainbow Trout",
    "Bass": "Largemouth Bass",
    "Catfish": "Channel Catfish",
    "Pufferfish": "Green Spotted Puffer",
    "Eel": "European Eel",
    "Stingray": "Common Stingray",
    "Seahorse": "Estuary Seahorse",
    "Octopus": "Common Octopus",
    "Squid": "European Squid",
    "Cuttlefish": "Common Cuttlefish",
    "Snail": "Roman Snail",
    "Slug": "Grey Field Slug",
    "Oyster": "Pacific Oyster",
    "Clam": "Hard Clam",
    "Eagle": "Bald Eagle",
    "Hawk": "Red-tailed Hawk",
    "Falcon": "Peregrine Falcon",
    "Owl": "Great Horned Owl",
    "Penguin": "Emperor Penguin",
    "Chicken": "Domestic Chicken",
    "Duck": "Mallard Duck",
    "Goose": "Greylag Goose",
    "Swan": "Mute Swan",
    "Pigeon": "Rock Dove",
    "Crow": "American Crow",
    "Raven": "Common Raven",
    "Parrot": "Scarlet Macaw",
    "Hummingbird": "Ruby-throated Hummingbird",
    "Flamingo": "Greater Flamingo",
    "Peacock": "Indian Peafowl",
    "Snake": "Western Diamondback Rattlesnake",
    "Lizard": "Green Iguana",
    "Chameleon": "Common Chameleon",
    "Gecko": "Tokay Gecko",
    "Crocodile": "Nile Crocodile",
    "Alligator": "American Alligator",
    "Turtle": "Painted Turtle",
    "Tortoise": "Galapagos Tortoise",
    "Sea Turtle": "Green Sea Turtle",
    "Monkey": "Rhesus Macaque",
    "Lemur": "Ring-tailed Lemur",
    "Tarsier": "Philippine Tarsier",
    "Wolf": "Gray Wolf",
    "Bear": "Brown Bear",
    "Fox": "Red Fox",
    "Horse": "Domestic Horse",
    "Zebra": "Plains Zebra",
    "Cow": "Domestic Cow",
    "Pig": "Domestic Pig",
    "Sheep": "Domestic Sheep",
    "Goat": "Domestic Goat",
    "Deer": "White-tailed Deer",
    "Camel": "Dromedary Camel",
    "Dolphin": "Bottlenose Dolphin"
}

with open("generate_shards.py") as f:
    text = f.read()

# Extract the old SPECIES_MAP
match = re.search(r"SPECIES_MAP = \{(.*?)\}", text, re.DOTALL)
if match:
    dict_content = match.group(1)
    # Parse the dictionary
    # Find all "Key": "Value" pairs
    pairs = re.findall(r'"([^"]+)":\s*"([^"]+)"', dict_content)
    
    new_lines = ["SPECIES_MAP = {"]
    for common, sci in pairs:
        base_name = common
        if common in better_names:
            base_name = better_names[common]
        new_key = f"{base_name} ({sci})"
        new_lines.append(f'    "{new_key}": "{sci}",')
    new_lines.append("}")
    
    new_map_str = "\n".join(new_lines)
    
    text = text[:match.start()] + new_map_str + text[match.end():]
    
    with open("generate_shards.py", "w") as f:
        f.write(text)
    print("Done rewriting SPECIES_MAP.")

