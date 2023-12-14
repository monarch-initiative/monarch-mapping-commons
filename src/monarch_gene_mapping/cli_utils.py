from typing import List

import numpy as np
import pandas as pd
from pandas.core.frame import DataFrame

# The UniProtKB mapping tsv file lacks a header line
UNIPROT_ID_MAPPING_SELECTED_COLUMNS = [
    "UniProtKB-AC",
    "UniProtKB-ID",
    "GeneID",
    "RefSeq",
    "GI",
    "PDB",
    "GO",
    "UniRef100",
    "UniRef90",
    "UniRef50",
    "UniParc",
    "PIR",
    "NCBI-taxon",
    "MIM",
    "UniGene",
    "PubMed",
    "EMBL",
    "EMBL-CDS",
    "Ensembl",
    "Ensembl_TRS",
    "Ensembl_PRO",
    "Additional PubMed",
]


def add_prefix(prefix: str, column: pd.Series) -> pd.Series:
    """
    Add a prefix to all values in a series
    :param prefix: Prefix for values in series
    :param column: Series of values for prefixing
    :return:
    """
    return prefix + column.astype("str")


def df_mappings(
    df: DataFrame,
    subject_column: str,  # "GeneID"
    object_column: str,  # "Ensembl_gene_identifier"
    predicate_id: str = "skos:exactMatch",
    entity_delimiter: str = ";",
    mapping_justification: str = "semapv:UnspecifiedMatching",
    filter_column: str = None,  # "#tax_id",
    subject_curie_prefix: str = None,  # "NCBIGene:"
    object_curie_prefix: str = None,  # "ENSEMBL:"
    filter_ids: List[int] = None,  # [9031]
) -> DataFrame:
    """
    Create specified mappings from DataFrame
    :param df: DataFrame source for mapping values
    :param subject_column: Column containing subject ID's
    :param object_column: Column containing object ID's
    :param predicate_id: String for predicate ID
    :param entity_delimiter: Delimiter for splitting IDs
    :param mapping_justification: String for mapping justification
    :param filter_column: Column to filter DataFrame on
    :param filter_ids:
    :param subject_curie_prefix: Optional curie for prefixing subject ID's
    :param object_curie_prefix: Optional curie for prefixing object ID's
    :return:
    """
    # Filtering could be extracted and done before passing df but I think there is value keeping it here.
    if (filter_column is not None) and isinstance(filter_ids, list):
        # Create a copy to guarantee we aren't working on a slice
        df_filtered = df.loc[df[filter_column].isin(filter_ids), :].copy()
    else:
        # Create copy so we don't modify the original DataFrame
        df_filtered = df.copy()

    df_filtered["predicate_id"] = predicate_id
    df_filtered["mapping_justification"] = mapping_justification

    columns = {subject_column: "subject_id", object_column: "object_id"}
    select_columns = ["subject_id", "predicate_id", "object_id", "mapping_justification"]
    df_select = df_filtered.rename(columns=columns).loc[:, select_columns].copy()

    # Create a copy of the DataFrame with unmapped values
    # df_unmapped = df_select[df_select['subject_id'].isna() | df_select['object_id'].isna()]

    # Drop rows with missing values
    df_select = df_select.dropna(subset=["subject_id", "object_id"], how="any")
    df_select = df_select.drop_duplicates()

    # Expand rows with semicolon in subject_id or object_id to multiple rows
    df_select = explode_column(df_select, "subject_id", entity_delimiter)
    df_select = explode_column(df_select, "object_id", entity_delimiter)

    if subject_curie_prefix is not None:
        df_select["subject_id"] = add_prefix(subject_curie_prefix, df_select["subject_id"])
    if object_curie_prefix is not None:
        df_select["object_id"] = add_prefix(object_curie_prefix, df_select["object_id"])

    df_map = df_select.drop_duplicates().dropna().copy()
    return df_map  # , df_unmapped


def explode_column(df: DataFrame, column: str, delimiter: str) -> DataFrame:
    """
    Expand columns with delimiter separated lists to multiple rows for each
    :param df: DataFrame for column expansion
    :param column: Column name for expansion
    :param delimiter: Delimiter for splitting column
    :return:
    """
    # cast non-null items in column to string
    df[column] = np.where(pd.isnull(df[column]),df[column],df[column].astype(str))

    assign_kwargs = {column: df[column].str.split(delimiter)}
    df_exploded = df.assign(**assign_kwargs).explode(column).copy()

    # remove whitespace
    df_exploded[column] = df_exploded[column].str.strip()
    return df_exploded


def preprocess_alliance_df(
    df: DataFrame, exclude_taxon: List, include_curie: List, include_xref_curie: List
) -> DataFrame:
    taxon_filter = ~df["TaxonID"].isin(exclude_taxon)
    curie_filter = df["GeneID"].str.contains("|".join(include_curie))
    self_filter = df["GeneID"] != df["GlobalCrossReferenceID"]
    xref_curie_filter = df["GlobalCrossReferenceID"].str.startswith(tuple(include_xref_curie))
    df.loc[:, "GlobalCrossReferenceID"] = df["GlobalCrossReferenceID"].str.replace("NCBI_Gene:", "NCBIGene:")
    df_filtered = df.loc[taxon_filter & curie_filter & self_filter & xref_curie_filter, :]
    return df_filtered.copy()


def alliance_mapping() -> DataFrame:
    alliance_file = "data/alliance/GENECROSSREFERENCE_COMBINED.tsv.gz"
    alliance_df = pd.read_csv(alliance_file, sep="\t", dtype="string", comment="#")
    alliance_df_filtered = preprocess_alliance_df(
        df=alliance_df,
        exclude_taxon=["NCBITaxon:9606", "NCBITaxon:2697049"],
        include_curie=["MGI:", "RGD:", "FB:", "WB:", "ZFIN:", "Xenbase:"],
        include_xref_curie=["ENSEMBL:", "NCBI_Gene:", "UniProtKB:"],
    )
    alliance_mappings = df_mappings(
        df=alliance_df_filtered,
        subject_column="GeneID",
        subject_curie_prefix="",
        object_column="GlobalCrossReferenceID",
        object_curie_prefix="",
        predicate_id="skos:exactMatch",
        mapping_justification="semapv:UnspecifiedMatching",
    )

    return alliance_mappings


def generate_gene_mappings() -> DataFrame:
    mapping_dataframes = []

    ### Alliance mappings
    print("Generating Alliance mappings...")
    alliance_mappings = alliance_mapping()
    print(f"Generated {len(alliance_mappings)} Alliance mappings")
    assert len(alliance_mappings) > 400000
    mapping_dataframes.append(alliance_mappings)

    ### HGNC mappings

    print("\nGenerating HGNC to NCBI Gene mappings...")
    hgnc_df = pd.read_csv("data/hgnc/hgnc_complete_set.txt", sep="\t", dtype="string")
    hgnc_to_ncbi = df_mappings(
        df=hgnc_df,
        subject_column="hgnc_id",
        object_column="entrez_id",
        object_curie_prefix="NCBIGene:",
        predicate_id="skos:exactMatch",
        mapping_justification="semapv:UnspecifiedMatching",
    )
    print(f"Generated {len(hgnc_to_ncbi)} HGNC-NCBI Gene mappings")
    assert len(hgnc_to_ncbi) > 40000
    mapping_dataframes.append(hgnc_to_ncbi)

    print("\nGenerating HGNC to OMIM mappings...")
    hgnc_to_omim = df_mappings(
        df=explode_column(hgnc_df, "omim_id", "|"),
        subject_column="hgnc_id",
        object_column="omim_id",
        object_curie_prefix="OMIM:",
        predicate_id="skos:exactMatch",
        mapping_justification="semapv:UnspecifiedMatching",
    )
    print(f"Generated {len(hgnc_to_omim)} HGNC-OMIM mappings")
    assert len(hgnc_to_omim) > 16000
    mapping_dataframes.append(hgnc_to_omim)

    print("\nGenerating HGNC to UniProtKB mappings...")
    hgnc_to_uniprot = df_mappings(
        df=explode_column(hgnc_df, "uniprot_ids", "|"),
        subject_column="hgnc_id",
        object_column="uniprot_ids",
        object_curie_prefix="UniProtKB:",
        predicate_id="skos:closeMatch",
        mapping_justification="semapv:UnspecifiedMatching",
    )
    print(f"Generated {len(hgnc_to_uniprot)} HGNC-UniProtKB mappings")
    assert len(hgnc_to_uniprot) > 20000
    mapping_dataframes.append(hgnc_to_uniprot)

    print("\nGenerating HGNC to ENSEMBL Gene mappings...")
    hgnc_to_ensemble = df_mappings(
        df=hgnc_df,
        subject_column="hgnc_id",
        object_column="ensembl_gene_id",
        object_curie_prefix="ENSEMBL:",
        predicate_id="skos:exactMatch",
        mapping_justification="semapv:UnspecifiedMatching",
    )
    print(f"Generated {len(hgnc_to_ensemble)} HGNC-ENSEMBL Gene mappings")
    assert len(hgnc_to_ensemble) > 40000
    mapping_dataframes.append(hgnc_to_ensemble)

    ### NCBI mappings

    print("\nGenerating NCBIGene to ENSEMBL Gene mappings...")
    ensembl_df = pd.read_csv("data/ncbi/gene2ensembl.gz", compression="gzip", sep="\t")
    ensembl_to_ncbi = df_mappings(
        df=ensembl_df,
        subject_column="GeneID",
        subject_curie_prefix="NCBIGene:",
        object_column="Ensembl_gene_identifier",
        object_curie_prefix="ENSEMBL:",
        predicate_id="skos:exactMatch",
        mapping_justification="semapv:UnspecifiedMatching",
        filter_column="#tax_id",
        # Chicken: 9031, Dog: 9615, Cow, 9913, Pig: 9823, Aspergillus ('Emericella') nidulans: 227321
        filter_ids=[9031, 9615, 9913, 9823, 227321],
    )
    print(f"Generated {len(ensembl_to_ncbi)} ENSEMBL-NCBIGene Gene mappings")
    assert len(ensembl_to_ncbi) > 70000
    mapping_dataframes.append(ensembl_to_ncbi)

    ### UniProtKB mappings

    print("\nGenerating UniProtKB to NCBI Gene mappings...")
    uniprot_df = pd.read_csv(
        "data/uniprot/idmapping_filtered.tsv.gz",  # filtered down to target species
        names=UNIPROT_ID_MAPPING_SELECTED_COLUMNS,
        compression="gzip",
        sep="\t",
        low_memory=False,
    )
    uniprot_to_ncbi = df_mappings(
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
        entity_delimiter=";",
    )
    print(f"Generated {len(uniprot_to_ncbi)} UniProtKB-NCBIGene Gene mappings")
    assert len(uniprot_to_ncbi) > 70000
    mapping_dataframes.append(uniprot_to_ncbi)

    mappings = pd.concat(mapping_dataframes)
    for row in mappings.itertuples():
        assert not ("<NA>" in row.subject_id)
        assert not ("<NA>" in row.object_id)
    return mappings
