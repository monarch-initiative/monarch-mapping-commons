"""
This script reads the registry file and updates the custom Makefile 
to include the latest mapping sets.
"""

import yaml
from pathlib import Path

registry_file = Path(__file__).parent.parent / "registry.yml"
makefile = Path(__file__).parent.parent / "monarch_mapping_commons.Makefile"
makefile_template = """
## Customize Makefile settings for monarch_mapping_commons
## 
## If you need to customize your Makefile, make
## changes here rather than in the main Makefile

all: mappings
mappings: $(ALL_MAPPINGS)
"""


# Read registry
with open(registry_file, "r") as f:
    registry = yaml.safe_load(f)

mapping_sets = registry["mapping_set_references"]
mapping_targets = [f"$(MAPPING_DIR)/{m['local_name']}" for m in mapping_sets]
makefile_template += "\nALL_MAPPINGS = {}\n".format(" ".join(mapping_targets))

for mapping in mapping_sets:
    print("Adding target for mapping set: {}".format(mapping["mapping_set_id"]))
    try:
        url = mapping["mirror_from"]
    except KeyError:
        url = mapping["mapping_set_id"]
    makefile_template += f"""
$(MAPPINGS_DIR)/{mapping['local_name']}: | $(MAPPINGS_DIR)/
	wget {url} -O $@
"""

with open(makefile, "w") as f:
    f.write(makefile_template)
