from os import sep
import typer
import pathlib

from kghub_downloader.download_utils import download_from_yaml
from sssom.context import get_converter
from curies import Converter, chain

from monarch_gene_mapping.cli_utils import generate_gene_mappings
from monarch_gene_mapping.uniprot_idmapping_preprocess import filter_uniprot_id_mapping_file

typer_app = typer.Typer()
sssom_converter = get_converter()
HERE = pathlib.Path(__file__).parent.absolute()
DOWNLOAD_YAML = f"{HERE}/download.yaml"

prefixes = {
    "HGNC": "https://www.genenames.org/data/gene-symbol-report/#!/hgnc_id/",
    "WB": "https://wormbase.org/",
}
gene_converter = Converter.from_prefix_map(prefixes)
converter = chain([sssom_converter, gene_converter])


@typer_app.command(name="download")
def _download():
    download_from_yaml(
        yaml_file=DOWNLOAD_YAML,
        output_dir=".",
    )


@typer_app.command(name="preprocess-uniprot")
def preprocess_uniprot_mappings(
    directory: str = typer.Option(f"..{sep}data{sep}uniprot", help="Data Directory"),
    source_filename: str = typer.Option("idmapping_selected.tab", help="Target File Name"),
    target_filename: str = typer.Option("idmapping_filtered.tsv", help="Target File Name"),
    number_of_lines: int = typer.Option(0, help="Number of Lines"),
):
    filter_uniprot_id_mapping_file(
        directory=directory,
        source_filename=source_filename,
        target_filename=target_filename,
        number_of_lines=number_of_lines,
    )


@typer_app.command()
def generate(
    output_dir=typer.Option("output", help="Output directory"),
    download: bool = typer.Option(False, help="Pass to first download required data"),
    preprocess_uniprot: bool = typer.Option(False, help="Filter out UniProt ID mapping data after download"),
):
    if download:
        _download()
        print("\nData download complete!\n")

    # prefilter 'target' taxa in Uniprot data
    if preprocess_uniprot:
        filter_uniprot_id_mapping_file(
            directory="data/uniprot",
            source_filename="idmapping_selected.tab",
            target_filename="idmapping_filtered.tsv",
            number_of_lines=0,
        )

    print("\nGenerating gene mapping...\n")
    pathlib.Path(output_dir).mkdir(parents=True, exist_ok=True)
    mappings = generate_gene_mappings()

    print("\nStandardizing CURIEs...\n")
    converter.pd_standardize_curie(mappings, column="subject_id", strict=True)
    converter.pd_standardize_curie(mappings, column="object_id", strict=True)

    mappings.to_csv(f"{output_dir}/gene_mappings.sssom.tsv", sep="\t", index=False)
    print(f"\nResults saved in {output_dir}/gene_mappings.sssom.tsv")


if __name__ == "__main__":
    typer_app()
