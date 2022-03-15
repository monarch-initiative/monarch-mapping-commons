from os import listdir
from os.path import join
from posixpath import dirname
from sssom.parsers import read_sssom_table
from sssom.writers import write_table
from sssom.util import MappingSetDataFrame
import pandas as pd
import yaml

INPUT_DIR = join(dirname(dirname(__file__)), "data/input")
OUTPUT_DIR = join(dirname(dirname(__file__)), "data/output")
OUT_PREFIX = 'confident_'
TSVS = [x for x in listdir(INPUT_DIR) if x.endswith('.tsv') and not x.startswith(OUT_PREFIX)]
PREFIX_YAML_FILE = join(OUTPUT_DIR, "prefix.yaml")
PREFIX_RECON_YAML = join(dirname(dirname(__file__)), "prefix_reconciliation.yaml")

metadata = dict()
prefix_map = dict()
msdf_list = []
df_list = []
# Read recon file
with open(PREFIX_RECON_YAML, "r") as pref_rec:
    prefix_reconciliation = yaml.safe_load(pref_rec)

prefix_synonyms = prefix_reconciliation[0]['prefix_synonyms']
prefix_expansion = prefix_reconciliation[1]['prefix_expansion_reconciliation']

for fn in TSVS:
    fp = join(INPUT_DIR, fn)
    print(f"Loading file:{fn} ")
    msdf = read_sssom_table(fp)
    msdf.df['confidence'] = 0.8
    metadata.update({k:v for k,v in msdf.metadata.items() if k not in metadata.keys()})
    prefix_map.update({k:v for k,v in msdf.prefix_map.items() if k not in prefix_map.keys()})
    # UPDATE PREFIX_MAP based on PREFIX_RECON_YAML
    for k in prefix_map.keys():
        prefix_syn_key = [s for s in prefix_synonyms.keys() if k == s]
        if len(prefix_syn_key) > 0:
            for sk in prefix_syn_key:
                correct_key = prefix_synonyms[sk]
                correct_value = prefix_expansion[correct_key]
                prefix_map.pop(sk, None)
                # Check if key exists.
                # If not, then condition applies.
                # If we want to change value regardless,
                # remove 'if' condition
                if correct_key not in prefix_map.keys():
                    prefix_map[correct_key] = correct_value
    
    msdf_list.append(msdf)
    df_list.append(msdf.df)
    out_fn = OUT_PREFIX+fn
    with open(join(INPUT_DIR, out_fn), "w") as of:
        write_table(msdf, of)

combined_df = pd.concat(df_list, axis=0, ignore_index=True)
combined_df = combined_df.drop_duplicates()

with open(PREFIX_YAML_FILE, "w+") as yml:
    yaml.dump(prefix_map,yml)

combined_msdf = MappingSetDataFrame(df=combined_df, prefix_map=prefix_map, metadata=metadata)
with open(join(INPUT_DIR, "combined_sssom.tsv"), "w") as combo_file:
    write_table(combined_msdf, combo_file)
