# A script to process Biopragmatics' biomappings file
# into MESH-to-CHEBI mappings for use in the Monarch KG pipeline.

import argparse

import pandas as pd
import curies
import sssom

# Parse arguments
parser = argparse.ArgumentParser(prog='Monarch Mapping Commons')
parser.add_argument("--input", type=str, help="URL or path to biomappings file")
parser.add_argument("--output", type=str, help="Path to output file")
args = parser.parse_args()
biomappings_file = args.input
output_file = args.output

# Initialize curie converter
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

# Read biomappings file    
df = pd.read_csv(biomappings_file, sep='\t')

# Standardize curies
for row in df.itertuples():
    df.at[row.Index, 'subject_id'] = converter.standardize_curie(row.subject_id)
    df.at[row.Index, 'object_id'] = converter.standardize_curie(row.object_id)

# Get only chebi to mesh rows
df = df[(df['subject_id'].str.startswith('CHEBI')) & (df['object_id'].str.startswith('MESH'))]

# Assert that all subject IDs are CHEBI and all object IDs are MESH
assert all(row.object_id.__contains__("MESH") for row in df.itertuples()), \
    f"\n\tObject IDs are not all CHEBI: {df.subject_id.unique()}\n"
assert all(row.subject_id.__contains__("CHEBI") for row in df.itertuples()), \
    f"\n\tSubject IDs are not all MESH: {df.subject_id.unique()}\n"

# Write to file
df.to_csv(output_file, sep='\t', index=False)
