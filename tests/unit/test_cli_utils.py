"""
Unit tests for the mapping generation framework
"""
import pandas as pd
import pytest

from monarch_gene_mapping.cli_utils import df_mappings, explode_column, UNIPROT_ID_MAPPING_SELECTED_COLUMNS


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
