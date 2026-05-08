import json, os, re
import subprocess

# Get old generate_shards.py
old_gen = subprocess.check_output(["git", "show", "HEAD:generate_shards.py"]).decode("utf-8")
match = re.search(r"SPECIES_MAP = (\{.*?\})", old_gen, re.DOTALL)
old_map = eval(match.group(1))

# We can invert old_map to go from common_name -> sci_name
# But wait, in the old JSON files, the filename is the target species (e.g. human.json).
# Inside human.json, keys are lowercase other species common names (e.g. "chimpanzee")
# We just need to reconstruct the cache keys.
time_cache = {}

for target_common, target_sci in old_map.items():
    filename = target_common.lower().replace(" ", "_") + ".json"
    filepath = os.path.join("data", filename)
    if os.path.exists(filepath):
        with open(filepath, "r") as f:
            data = json.load(f)
        for other_common_lower, info in data.items():
            # Find original case
            other_common = next((k for k in old_map.keys() if k.lower() == other_common_lower), None)
            if other_common:
                other_sci = old_map[other_common]
                pair_key = tuple(sorted([target_sci, other_sci]))
                cache_key = f"{pair_key[0]}||{pair_key[1]}"
                time_cache[cache_key] = info["time"]

with open("data/time_cache.json", "w") as f:
    json.dump(time_cache, f)

print(f"Rebuilt cache with {len(time_cache)} entries.")
