import json

import pathlib

pathlib.Path(__file__).parent.resolve()

ROOT_DIR_PATH = pathlib.Path(__file__).parent.parent.resolve()
DATA_DIR_PATH = f"{ROOT_DIR_PATH}/geo_data"

with open(f"{DATA_DIR_PATH}/all.json", "r") as fp:
    source_data = json.load(fp)

cc_to_region = {}

for entry in source_data:
    cc_to_region[entry["alpha-2"]] = entry["region"] or "(unknown)"

with open(f"{DATA_DIR_PATH}/cc_to_region.json", "w") as fp:
    json.dump(cc_to_region, fp, indent=2)
