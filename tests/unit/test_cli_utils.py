"""
Unit tests for the mapping generation framework
"""
import ast
from pathlib import Path

import pandas as pd
import pytest
from sssom.io import parse_file

from monarch_gene_mapping.cli_utils import (
    alliance_mapping,
    df_mappings,
    dictybase_mapping,
    ensembl_entrez_mapping,
    explode_column,
    preprocess_alliance_df,
    ENSEMBL_ENTREZ_FILES,
    UNIPROT_ID_MAPPING_SELECTED_COLUMNS,
)


def test_null_mapping():
    hgnc_df = pd.read_csv("tests/resources/hgnc_test.txt", sep="\t", dtype="string")
    mapped = df_mappings(
        df=explode_column(hgnc_df, "omim_id", "|"),
        subject_column="hgnc_id",
        object_column="omim_id",
        object_curie_prefix="OMIM:",
        predicate_id="skos:exactMatch",
        mapping_justification="semapv:UnspecifiedMatching",
    )
    # assert len(mapped) == 4
    for row in mapped.itertuples():
        assert not ("NA" in row.subject_id)
        assert not ("NA" in row.object_id)
test_null_mapping()

def test_semicolon_in_id():
    uniprot_df = pd.read_csv("tests/resources/uniprot_test.tsv", names=UNIPROT_ID_MAPPING_SELECTED_COLUMNS, sep="\t")
    mapped = df_mappings(
        df=uniprot_df,
        subject_column="GeneID",
        subject_curie_prefix="NCBIGene:",
        predicate_id="skos:exactMatch",
        object_column="UniProtKB-AC",
        object_curie_prefix="UniProtKB:",
        mapping_justification="semapv:UnspecifiedMatching",
        filter_column="NCBI-taxon",
        # Chicken: 9031, Dog: 9615, Cow, 9913, Pig: 9823, Aspergillus ('Emericella') nidulans: 227321
        filter_ids=[9031, 9615, 9913, 9823, 227321],
    )
    assert len(mapped) == 4


def test_ensembl_entrez_trans_name_rows_are_not_mappings():
    """
    Ensembl entrez files interleave EntrezGene rows, whose xref is an NCBI gene ID, with
    EntrezGene_trans_name rows, whose xref is a transcript name like 'HTR2C-201'. Only
    the former are mappings; taking both mints nonexistent NCBIGene:<transcript> nodes.
    """
    mapped = ensembl_entrez_mapping("tests/resources/ensembl_entrez_test.tsv.gz")

    assert len(mapped) == 3
    assert set(mapped["subject_id"]) == {
        "NCBIGene:119868660",
        "NCBIGene:119868661",
        "NCBIGene:491802",
    }
    assert mapped["object_id"].str.startswith("ENSEMBL:ENSCAFG00845").all()


def test_ensembl_entrez_files_cover_both_dog_assemblies():
    """
    PantherDB emits ROS_Cfam_1.0 dog IDs while NCBI's gene2ensembl carries only
    CanFam3.1, so the ROS_Cfam_1.0 file is what keeps those ortholog edges resolvable.
    """
    assert any(
        name.startswith("Canis_lupus_familiaris.ROS_Cfam_1.0")
        for name in ENSEMBL_ENTREZ_FILES
    )


ALLIANCE_INCLUDE_CURIE = ["MGI:", "RGD:", "FB:", "WB:", "ZFIN:", "Xenbase:", "SGD:"]


def _alliance_fixture():
    return pd.read_csv("tests/resources/alliance_xref_test.tsv", sep="\t", dtype="string", comment="#")


def test_alliance_includes_sgd():
    """
    Yeast genes are SGD nodes in the KG and the Alliance file is our only source of
    cross-references to them, so SGD has to be in include_curie. Without it every
    BioGRID yeast interaction references an NCBIGene node that does not exist.
    """
    mapped = preprocess_alliance_df(
        df=_alliance_fixture(),
        exclude_taxon=["NCBITaxon:9606", "NCBITaxon:2697049"],
        include_curie=ALLIANCE_INCLUDE_CURIE,
        include_xref_curie=["ENSEMBL:", "NCBI_Gene:", "UniProtKB:"],
    )
    sgd = mapped[mapped["GeneID"].str.startswith("SGD:")]
    assert set(sgd["GlobalCrossReferenceID"]) == {"NCBIGene:851585", "NCBIGene:852238"}


def test_alliance_drops_self_xrefs_and_excluded_taxa():
    """SGD:x -> SGD:x carries no information, and human is excluded in favour of HGNC."""
    mapped = preprocess_alliance_df(
        df=_alliance_fixture(),
        exclude_taxon=["NCBITaxon:9606", "NCBITaxon:2697049"],
        include_curie=ALLIANCE_INCLUDE_CURIE,
        include_xref_curie=["ENSEMBL:", "NCBI_Gene:", "UniProtKB:"],
    )
    assert not (mapped["GeneID"] == mapped["GlobalCrossReferenceID"]).any()
    assert "NCBITaxon:9606" not in set(mapped["TaxonID"])


def test_dictybase_mapping_reads_the_xref_not_the_taxon():
    """
    Dicty has a naming authority but no Alliance rows, so gene_info's dbXrefs column is
    our only route to dictyBase IDs. Rows without a dictyBase xref, and rows for other
    species, must not produce mappings.
    """
    mapped = dictybase_mapping("tests/resources/gene_info_dicty_test.tsv.gz")

    assert len(mapped) == 3
    assert set(mapped["subject_id"]) == {
        "dictyBase:DDB_G0294382",
        "dictyBase:DDB_G0294384",
        "dictyBase:DDB_G0294386",
    }
    assert mapped["object_id"].str.match(r"^NCBIGene:\d+$").all()
    # the dicty-taxon row whose dbXrefs carry no dictyBase entry is dropped
    assert "NCBIGene:99999999" not in set(mapped["object_id"])
    # and the human row is excluded by taxon, despite having a HGNC: xref
    assert not mapped["subject_id"].str.contains("HGNC").any()


def test_ensembl_files_exclude_species_with_a_naming_authority():
    """
    These files map Ensembl gene IDs to NCBIGene, which only resolves for species whose
    KG nodes *are* NCBIGene nodes -- the ones with no naming authority. Human and
    zebrafish genes are HGNC and ZFIN nodes, so such a mapping resolves almost nothing.

    Zebrafish is the case to be careful about: ZFIN curates ENSDARG assignments
    specifically to correct automated errors made on the Ensembl side, so ENSDARG to
    ZFIN:ZDB-GENE must come from ZFIN via the Alliance file, never from these.
    """
    excluded = ("Homo_sapiens", "Danio_rerio", "Mus_musculus", "Rattus_norvegicus")
    offenders = [f for f in ENSEMBL_ENTREZ_FILES if f.startswith(excluded)]
    assert not offenders, f"Species with a naming authority must not be mapped here: {offenders}"


# HGNC is the one prefix not derivable from a *_curie_prefix literal: hgnc_complete_set
# already carries "HGNC:" inline in its hgnc_id column, so the code never adds it.
PREFIXES_NOT_SET_IN_CODE = {"HGNC"}


def emitted_curie_prefixes() -> set:
    """
    Derive, from cli_utils.py itself, every CURIE prefix generate_gene_mappings can emit.

    Read out of the source rather than restated here on purpose: a hand-maintained list
    passes green when someone adds a source and forgets to update it, which is the exact
    failure this guards against.
    """
    source = Path("src/monarch_gene_mapping/cli_utils.py").read_text()
    tree = ast.parse(source)
    prefixes = set(PREFIXES_NOT_SET_IN_CODE)
    for node in ast.walk(tree):
        if not isinstance(node, ast.keyword) or node.arg is None:
            continue
        # subject_curie_prefix="NCBIGene:" / object_curie_prefix="ENSEMBL:"
        if node.arg.endswith("curie_prefix") and isinstance(node.value, ast.Constant):
            if isinstance(node.value.value, str) and node.value.value.endswith(":"):
                prefixes.add(node.value.value.rstrip(":"))
        # include_curie=[...] / include_xref_curie=[...]
        elif node.arg in {"include_curie", "include_xref_curie"} and isinstance(node.value, ast.List):
            for element in node.value.elts:
                if isinstance(element, ast.Constant) and isinstance(element.value, str):
                    prefixes.add(element.value.rstrip(":"))
    # the Alliance file's NCBI_Gene: is rewritten to NCBIGene: before it is emitted
    prefixes.discard("NCBI_Gene")
    prefixes.add("NCBIGene")
    return prefixes


def test_emitted_prefixes_are_derivable_from_the_source():
    """Sanity-check the derivation itself, so a silent parse failure cannot empty it."""
    prefixes = emitted_curie_prefixes()
    assert prefixes == {
        "MGI", "RGD", "FB", "WB", "ZFIN", "Xenbase", "SGD",
        "ENSEMBL", "NCBIGene", "UniProtKB", "HGNC", "OMIM", "dictyBase", "PomBase",
    }


def test_every_emitted_prefix_is_in_the_gene_mappings_prefix_map(tmp_path):
    """
    `make mappings` pipes the generated TSV through `sssom parse -m
    metadata/gene_mappings.sssom.yml --prefix-map-mode merged`, which hard-fails on any
    prefix missing from the merged prefix map:

        ValueError: {'SGD', 'dictyBase'} are used in the SSSOM mapping set
        but it does not exist in the prefix map

    That target is skipped under GH_ACTION, so CI cannot catch it and the failure only
    shows up on Jenkins after merge. The prefixes come from cli_utils.py, so adding a
    source without a declared expansion fails here rather than there.
    """
    prefixes = sorted(emitted_curie_prefixes())
    rows = "\n".join(
        f"{prefix}:X{i}\tskos:exactMatch\tNCBIGene:{i}\tsemapv:UnspecifiedMatching"
        for i, prefix in enumerate(prefixes, start=1)
    )
    source = tmp_path / "probe.sssom.tsv"
    source.write_text("subject_id\tpredicate_id\tobject_id\tmapping_justification\n" + rows + "\n")

    destination = tmp_path / "out.sssom.tsv"
    with destination.open("w") as out:
        parse_file(
            input_path=str(source),
            output=out,
            metadata_path="metadata/gene_mappings.sssom.yml",
            prefix_map_mode="merged",
        )

    # parse_file drops offending rows rather than raising when strict checking is off, so
    # assert the rows survived instead of relying on "it did not throw".
    written = destination.read_text()
    data_rows = [line for line in written.splitlines() if line and not line.startswith("#")][1:]
    assert len(data_rows) == len(prefixes)
    curie_map = written[written.index("# curie_map:"):]
    for prefix in prefixes:
        assert f"#   {prefix}:" in curie_map, f"{prefix} missing from the output curie_map"
