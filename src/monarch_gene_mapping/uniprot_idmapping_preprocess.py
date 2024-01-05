#!/usr/bin/env python
"""
Utility methods for pre-filtering of **huge** UniProdKB ID
mapping input file (i.e. data/uniprot/idmapping_selected.tab.gz)
The script takes about 9 minutes to filter the input dataset containing
~60 million original entries, down to ~1.2 million (of taxon-specific) entries.
"""
from os import sep

from sys import stderr
import argparse

from gzip import open as gzip_open, BadGzipFile

from datetime import datetime

from typing import Optional, List, Set

# Hard-coded list of target species (TODO: externalize this list in a configuration file?)
target_species: Set = {
    "9606",  # Homo sapiens
    "10090",  # Mus musculus (mouse)
    "9615",  # Canis lupus familiaris - domestic dog
    # "9685", # Felis catus - domestic cat
    "9913",  # Bos taurus - cow
    "9823",  # Sus scrofa - pig
    "10116",  # Rattus norvegicus (Norway rat)
    "9031",  # Gallus gallus
    "8364",  # Xenopus tropicalis - tropical clawed frog
    "7955",  # Danio rerio (Zebrafish)
    "7227",  # Drosophila melanogaster (fruit fly)
    "6239",  # Caenorhabditus elegans
    "44689",  # Dictylostelium
    "227321",  # Emericella nidulans (strain FGSC A4 etc.) (Aspergillus nidulans)
    "4896",  # Schizosaccharomyces pombe ("fission" yeast)
    "4932",  # Saccharomyces cerevisiae (baker's "budding" yeast)
}

# idmapping_selected.tab field 13 is column 12 in TSV array...
UNIPROT_ID_MAPPING_NCBI_TAXON_COLUMN = 12


def target_taxon(line: Optional[str]) -> bool:
    if not line:
        return False
    part: List[str] = line.split("\t")
    if part[UNIPROT_ID_MAPPING_NCBI_TAXON_COLUMN] in target_species:
        return True
    else:
        return False


PROGRESS_MONITOR_INCR: int = 1000


def filter_uniprot_id_mapping_file(
    directory: str, source_filename: str, target_filename: str, number_of_lines: int = 0  # root file name only?
) -> bool:
    """
    Filters contents of a UniProKB idmapping selected tab gzip'd archive against the target list of taxa.
    :param directory: str, location of source data file
    :param source_filename: str, root file name of input source data archive
    :param target_filename: str, root file name of output target data archive
    :param number_of_lines: int, positive number of lines parsed; 'all' lines parsed if omitted or set to zero
    :return: bool, True if filtering was successful; False if unsuccessful
    """
    if not directory:
        directory = "."
    directory_path: str = directory

    assert source_filename
    assert target_filename
    assert number_of_lines >= 0

    print(
        f"\nBegin file filtering '{number_of_lines if number_of_lines else 'all'}'"
        + f" lines in '{source_filename}' at {datetime.now().isoformat()}. "
        + f"\nPatience! This may take a little awhile!...\n"
    )

    # A standard gzip compressed TSV file
    source_gz_filename: str = f"{source_filename}.gz"
    source_gz_file_path: str = f"{directory_path}{sep}{source_gz_filename}"
    target_gz_filename: str = f"{target_filename}.gz"
    target_gz_file_path: str = f"{directory_path}{sep}{target_gz_filename}"
    n: int = 0
    p: int = 0  # visible progress monitor
    print("Processing... ")
    try:
        with gzip_open(source_gz_file_path, mode="rt", encoding="utf-8") as source_gz_file:
            with gzip_open(target_gz_file_path, mode="wt", encoding="utf-8") as target_file:
                for line in source_gz_file:
                    p += 1
                    if target_taxon(line):
                        print(line, file=target_file, end="")
                        n += 1
                    if number_of_lines and n > number_of_lines:
                        break
                    if not (p % PROGRESS_MONITOR_INCR):
                        print(f"{p} lines", end="\r")

    except FileNotFoundError as fnf:
        print(f"\nFile '{source_gz_file_path}' not found, at {datetime.now().isoformat()}", file=stderr)
        return False
    except BadGzipFile as bzf:
        print(
            f"\nFailed filtering '{source_filename}' at {datetime.now().isoformat()}: "
            + f"Gzip file access exception: {str(bzf)}",
            file=stderr,
        )
        return False

    print(f"\nFinished filtering file '{source_gz_file_path}' at {datetime.now().isoformat()}")
    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-d",
        "--directory",
        default=f"..{sep}data{sep}uniprot",
        help="Working directory containing the data (default: 'data/uniprot')",
    )
    parser.add_argument(
        "-s",
        "--source",
        default="idmapping_selected.tab",
        help="Source root data file name (default: 'idmapping_selected.tab')",
    )
    parser.add_argument(
        "-t", "--target", default="idmapping_filtered.tsv", help="Target root data file name (default: 'idmapping_filtered.tsv')"
    )
    parser.add_argument(
        "-n",
        "--number_of_lines",
        type=int,
        default=0,
        help="Maximum (positive) number of lines to process; n == 0 implies 'process all' (default: 0 == 'all')",
    )

    args = parser.parse_args()

    if filter_uniprot_id_mapping_file(
        directory=args.directory,
        source_filename=args.source,
        target_filename=args.target,
        number_of_lines=args.number_of_lines,
    ):
        quantity: str = args.number_of_lines > 0 if args.number_of_lines else "All"
        print(
            f"\n{quantity} lines of file '{args.source}' in directory '{args.directory}'"
            + f" successfully filtered into file '{args.target}'"
        )
    else:
        # fail filtering
        print(f"\nERROR: file '{str(args.source)}' in directory '{args.directory}' could NOT be processed?")
