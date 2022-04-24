import json

import pathlib

pathlib.Path(__file__).parent.resolve()

ROOT_DIR_PATH = pathlib.Path(__file__).parent.parent.resolve()
DATA_DIR_PATH = f"{ROOT_DIR_PATH}/geo_data"

with open(f"{DATA_DIR_PATH}/all.json", "r") as fp:
    source_data = json.load(fp)

alpha2_to_region = {}

for entry in source_data:
    alpha2_to_region[entry["alpha-2"]] = entry["region"] or "(unknown)"

with open(f"{DATA_DIR_PATH}/alpha2_to_region.json", "w") as fp:
    json.dump(alpha2_to_region, fp, indent=2)
