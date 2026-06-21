#!/usr/bin/env -S uv run --script

# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "biomappings>=0.5.2",
#     "click>=8.3.3",
#     "prefixmaps>=0.2.6",
#     "sssom-pydantic>=0.5.4",
#     "curies>=0.13.7",
# ]
# ///

"""Subset Biomappings to ChEBI-MeSH terms.

This script defines inline metadata compliant with `PEP-723 <https://peps.python.org/pep-0723/>`_,
meaning that any modern Python tooling should be able to install and run it.

This is used in combination with a _shebang_ (i.e., the first line starting with ``#!``) so
it knows how it can be run when called as an executable script from the command line
like in:

.. code-block:: console

    $ ./process_biomappings.py

Currently, it uses a shebang that works with ``uv`` as documented in
https://docs.astral.sh/uv/guides/scripts/#using-a-shebang-to-create-an-executable-file,
but can be changed to use a different runner if desired. As such, this script
can also be run with ``uv run process_biomappings.py``.
"""

import importlib.util
from pathlib import Path

import click
import curies
import sssom_pydantic
from curies.mixins import standardize_many
from curies.triples import keep_predicates, keep_prefixes_both
from curies.vocabulary import exact_match
from prefixmaps import load_converter
from pystow.utils import read_pydantic_yaml
from sssom_pydantic.process import (
    exclude_negative,
    exclude_unsure,
    invert_by_prefix_pair,
)

URL = "https://w3id.org/biopragmatics/biomappings/sssom/biomappings.sssom.tsv"

HERE = Path(__file__).parent.resolve()
ROOT = HERE.parent.resolve()
METADATA_PATH = ROOT.joinpath("metadata", "mesh_chebi_biomappings.sssom.yml")
DEFAULT_OUTPUT = ROOT.joinpath("mappings", "mesh_chebi_biomappings.sssom.tsv")


@click.command()
@click.option("--input", help="URL or path to biomappings file")
@click.option("--output", type=Path, default=DEFAULT_OUTPUT)
@click.option(
    "--remote",
    is_flag=True,
    help="If true, read the remote Biomappings instead of the local version",
)
def main(input: str | None, output: Path, remote: bool) -> None:
    """Subset Biomappings to ChEBI-MeSH terms."""
    if input is not None:
        mappings, _converter, metadata = sssom_pydantic.read(input)
        version = metadata.version
    elif remote or not importlib.util.find_spec("biomappings"):
        click.echo(f"reading SSSOM from {URL}")
        mappings, _converter, metadata = sssom_pydantic.read(URL)
        version = metadata.version
    else:
        import biomappings
        import biomappings.version

        mappings = biomappings.read_mappings()
        version = biomappings.version.get_version()

    converter: curies.Converter = load_converter("merged")
    # prefixmaps converters would be much more useful if they had synonyms built in.
    # I want this to be streamlined.
    converter.add_prefix_synonym("CHEBI", "chebi")
    converter.add_prefix_synonym("MESH", "mesh")
    converter.add_prefix_synonym("SEMAPV", "semapv")
    converter.add_prefix_synonym("ORCID", "orcid")

    mappings = exclude_negative(mappings)
    mappings = exclude_unsure(mappings)
    mappings = keep_prefixes_both(mappings, {"chebi", "mesh"})
    mappings = keep_predicates(mappings, exact_match)
    mappings = invert_by_prefix_pair(mappings, "mesh", "chebi")
    mappings = standardize_many(mappings, converter)

    metadata = read_pydantic_yaml(METADATA_PATH, sssom_pydantic.MappingSetRecord)
    metadata = metadata.model_copy(update={"mapping_set_version": version})

    click.echo(f"Writing to {output}")
    sssom_pydantic.write(mappings, output, converter=converter, metadata=metadata)


if __name__ == "__main__":
    main()
