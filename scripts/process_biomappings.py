"""
A script to process Biopragmatics' biomappings file into CHEBI-to-MESH mappings for use in the Monarch KG pipeline.
"""

from pathlib import Path
import yaml

import click
import requests
import pandas as pd
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
    df = pd.read_csv(input, sep="\t")

    res = requests.get(YAML_URL)
    metadata = yaml.safe_load(res.text)

    # Remove negative mappings
    df = df[df["predicate_modifier"] != "Not"]

    # Get only ChEBI to MESH rows
    df = df[(df["subject_id"].str.startswith("mesh")) & (df["object_id"].str.startswith("CHEBI"))]

    # Convert subject_id to upper case
    # df["subject_id"] = df["subject_id"].str.upper()

    # Assert that all subject-IDs are MESH and all object-IDs are CHEBI
    assert all(
        # row.subject_id.__contains__("MESH") for row in df.itertuples()
        row.subject_id.__contains__("mesh") for row in df.itertuples()
    ), f"\n\tSubject IDs are not all MESH: {df.subject_id.unique()}\n"

    assert all(
        row.object_id.__contains__("CHEBI") for row in df.itertuples()
    ), f"\n\tObject IDs are not all CHEBI: {df.subject_id.unique()}\n"

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
    converter = get_converter()
    converter.pd_standardize_curie(df, column="subject_id")
    converter.pd_standardize_curie(df, column="object_id")

    # Write to file
    df.to_csv(output, sep="\t", index=False)


if __name__ == "__main__":
    main()
