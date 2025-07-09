"""
A script to process Biopragmatics' biomappings file into CHEBI-to-MESH mappings for use in the Monarch KG pipeline.
"""

from pathlib import Path
import yaml

import click
import requests
import pandas as pd
from prefixmaps import load_converter
from sssom.context import get_converter

HERE = Path(__file__).parent.resolve()
ROOT = HERE.parent.resolve()
DEFAULT_OUTPUT = ROOT.joinpath("mappings", "biomappings.sssom.tsv")

TSV_URL = "https://w3id.org/biopragmatics/biomappings/sssom/biomappings.sssom.tsv"
YAML_URL = "https://w3id.org/biopragmatics/biomappings/sssom/biomappings.sssom.yml"


@click.command(name="Monarch Mapping Commons")
@click.option(
    "--input",
    default=TSV_URL,
    help="URL or path to biomappings file",
)
@click.option("--output", type=click.Path(), default=DEFAULT_OUTPUT, help="Path to output file")
def main(input: str, output: Path):
    # Read biomappings file
    df = pd.read_csv(input, sep="\t", comment='#')

    res = requests.get(YAML_URL)
    metadata = yaml.safe_load(res.text)

    # Remove negative mappings
    df = df[df["predicate_modifier"] != "Not"]

    # Capture MESH to ChEBI rows
    df_to_flip = df[(df["subject_id"].str.startswith("mesh"))
                    & (df["object_id"].str.startswith("CHEBI"))
                    & (df["predicate_id"] == "skos:exactMatch")]

    # Get only ChEBI to MESH rows
    df = df[(df["subject_id"].str.startswith("CHEBI"))
            & (df["object_id"].str.startswith("mesh"))
            & (df["predicate_id"] == "skos:exactMatch")]

    # Flip the subject_id, subject_label and object_id, object_label columns on df_to_flip,
    df_to_flip = df_to_flip.rename(columns={
        "subject_id": "object_id",
        "subject_label": "object_label",
        "object_id": "subject_id",
        "object_label": "subject_label"
    })
    # put the columns back into the original order
    df_to_flip = df_to_flip[df.columns]
    df = pd.concat([df, df_to_flip])

    # Convert object_id (MESH) to upper case
    df["object_id"] = df["object_id"].str.upper()

    subset = {
        key: metadata[key]
        # these are all SSSOM keys, see https://mapping-commons.github.io/sssom/
        for key in [
            "license",
            "mapping_set_title",
            "mapping_set_version",
            "mapping_set_id",
        ]
    }
    df = df.assign(**subset)

    # Standardize CURIEs
    converter = load_converter("merged")
    converter.pd_standardize_curie(df, column="subject_id")
    converter.pd_standardize_curie(df, column="object_id")

    # Assert that all subject-IDs are CHEBI and all object-IDs are MESH
    assert all(
        row.subject_id.__contains__("CHEBI") for row in df.itertuples()
        # row.subject_id.__contains__("mesh") for row in df.itertuples()
    ), f"\n\tSubject IDs are not all CHEBI: {df.subject_id.unique()}\n"

    assert all(
        row.object_id.__contains__("MESH") for row in df.itertuples()
    ), f"\n\tObject IDs are not all MESH: {df.object_id.unique()}\n"


    # Write to file
    df.to_csv(output, sep="\t", index=False)


if __name__ == "__main__":
    main()
