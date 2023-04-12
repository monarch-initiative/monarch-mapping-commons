import pandas as pd
# import sys

# biomappings_file = sys.argv[1]
biomappings_file = "https://raw.githubusercontent.com/biopragmatics/biomappings/master/docs/_data/sssom/biomappings.sssom.tsv"
df = pd.read_csv(biomappings_file, sep='\t')

# Get only chebi to mesh rows
df = df[(df['subject_id'].str.contains('chebi')) & (df['object_id'].str.contains('mesh'))]

# Capitalize the mesh and chebi ids
df['subject_id'] = df['subject_id'].str.upper()
df['object_id'] = df['object_id'].str.upper()

# Swap values of subject id and object id
df['subject_id'], df['object_id'] = df['object_id'].values, df['subject_id'].values

# Write to file
df.to_csv("mappings/biomappings.sssom.tsv", sep='\t', index=False)
