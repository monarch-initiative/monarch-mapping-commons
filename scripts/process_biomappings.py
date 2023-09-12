"""
A script to process Biopragmatics' biomappings file into CHEBI-to-MESH mappings for use in the Monarch KG pipeline.
"""

from datetime import datetime
from pathlib import Path

import requests
import pandas as pd
import curies
import click
import yaml


TSV_URL = "https://w3id.org/biopragmatics/biomappings/sssom/biomappings.sssom.tsv"
YAML_URL = "https://w3id.org/biopragmatics/biomappings/sssom/biomappings.sssom.yml"


@click.command(name="Monarch Mapping Commons")
@click.option(
    "--path",
    default=TSV_URL,
    help="URL or path to biomappings file",
)
@click.option("--output", type=click.Path(), help="Path to output file")
def main(path: str, output: Path):
    converter = curies.Converter(
        [
            curies.Record(
                prefix="CHEBI",
                prefix_synonyms=["chebi"],
                uri_prefix="http://purl.obolibrary.org/obo/CHEBI_",
            ),
            curies.Record(
                prefix="MESH",
                prefix_synonyms=["mesh"],
                uri_prefix="http://purl.obolibrary.org/obo/MESH_",
            ),
        ]
    )

    # Read biomappings file
    df = pd.read_csv(path, sep="\t")

    res = requests.get(YAML_URL)
    metadata = yaml.safe_load(res.text)

    converter.pd_standardize_curie(df, column="subject_id")
    converter.pd_standardize_curie(df, column="object_id")

    # Remove negative mappings
    df = df[df["predicate_modifier"] != "Not"]

    # Get only ChEBI to MeSH rows
    df = df[
        (df["subject_id"].str.startswith("MESH"))
        & (df["object_id"].str.startswith("CHEBI"))
    ]

    # Assert that all subject-IDs are MESH and all object-IDs are CHEBI
    assert all(
        row.subject_id.__contains__("MESH") for row in df.itertuples()
    ), f"\n\tSubject IDs are not all MESH: {df.subject_id.unique()}\n"

    assert all(
        row.object_id.__contains__("CHEBI") for row in df.itertuples()
    ), f"\n\tObject IDs are not all CHEBI: {df.subject_id.unique()}\n"

    # TODO @cthoyt make this version information available inside the YAML metadata
    df = df.assign(license=metadata["license"])
    df = df.assign(mapping_source=path)
    df = df.assign(
        mapping_source_version=f'biomappings_{datetime.now().strftime("%Y%m%d")}'
    )

    # Write to file
    df.to_csv(output, sep="\t", index=False)


if __name__ == "__main__":
    main()
