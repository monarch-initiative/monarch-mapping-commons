# A script to standardize curies in biomappings and invert subject and object, 
# resulting in MESH to CHEBI mappings for use in the Monarch KG pipeline.
import sys

import pandas as pd
import curies
import sssom


converter = curies.Converter([
    curies.Record(
        prefix="CHEBI",
        prefix_synonyms=["chebi"],
        uri_prefix="http://purl.obolibrary.org/obo/CHEBI_",
    ),
    curies.Record(
        prefix="MESH",
        prefix_synonyms=["mesh"],
        uri_prefix="http://purl.obolibrary.org/obo/MESH_",
    )
])

try:
    biomappings_file = sys.argv[1]
except IndexError:
    biomappings_file = "https://raw.githubusercontent.com/biopragmatics/biomappings/master/docs/_data/sssom/biomappings.sssom.tsv"
    
df = pd.read_csv(biomappings_file, sep='\t')

# Get only chebi to mesh rows
df = df[(df['subject_id'].str.contains('chebi')) & (df['object_id'].str.contains('mesh'))]

# Standardize curies
for row in df.itertuples():
    df.at[row.Index, 'subject_id'] = converter.standardize_curie(row.subject_id)
    df.at[row.Index, 'object_id'] = converter.standardize_curie(row.object_id)

# Invert subject and object with sssom
df = sssom.util.invert_mappings(df=df, subject_prefix="MESH")

# Write to file
# df.to_csv("mappings/biomappings.sssom.tsv", sep='\t', index=False)
print(df.head(5))
