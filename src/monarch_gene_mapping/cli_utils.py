from typing import List, Union

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


# Ensembl entrez xref files, mapped to a floor for the number of mappings each should
# yield. One file per species per genome assembly: NCBI's gene2ensembl carries only one
# Ensembl gene ID series per species, and our ingest sources are pinned to assorted
# assemblies, so a single series leaves the rest dangling. See download.yaml for why the
# releases are pinned and why older ones are kept alongside newer ones.
#
# Floors sit ~15% below observed counts: low enough to ride out release churn, high
# enough to catch a file that stopped parsing or a filter that matched nothing.
ENSEMBL_ENTREZ_FILES = {
    # Cow. gene2ensembl carries ENSBTAG00070; the files below carry ENSBTAG00000. Older
    # releases are kept because newer ones drop genes outright: ARS-UCD1.2 (rel 110) is
    # the only source for ~2,200 genes that 1.3 and 2.0 no longer carry at all.
    "Bos_taurus.ARS-UCD1.2.110.entrez.tsv.gz": 17000,
    "Bos_taurus.ARS-UCD1.3.113.entrez.tsv.gz": 15000,
    "Bos_taurus.ARS-UCD2.0.115.entrez.tsv.gz": 18000,
    # Chicken. gene2ensembl carries ENSGALG00010. GRCg6a is the only source of the
    # retired ENSGALG00000 series and GRCg7w the only source of ENSGALG00015; the two
    # GRCg7b releases fill gaps in ENSGALG00010.
    "Gallus_gallus.GRCg6a.106.entrez.tsv.gz": 13000,
    "Gallus_gallus_gca000002315v5.GRCg6a.115.entrez.tsv.gz": 17000,
    "Gallus_gallus.bGalGal1.mat.broiler.GRCg7b.110.entrez.tsv.gz": 17000,
    "Gallus_gallus.bGalGal1.mat.broiler.GRCg7b.115.entrez.tsv.gz": 17000,
    "Gallus_gallus_gca016700215v2.bGalGal1.pat.whiteleghornlayer.GRCg7w.115.entrez.tsv.gz": 17000,
    # Dog. gene2ensembl carries only CanFam3.1 (ENSCAFG00000). ROS_Cfam_1.0 is the
    # series PantherDB emits; the breed assemblies are each the sole source of their own.
    "Canis_lupus_familiaris.ROS_Cfam_1.0.115.entrez.tsv.gz": 19000,
    "Canis_lupus_familiarisboxer.Dog10K_Boxer_Tasha.115.entrez.tsv.gz": 17000,
    "Canis_lupus_familiarisbasenji.Basenji_breed-1.1.115.entrez.tsv.gz": 13000,
    "Canis_lupus_familiarisgsd.UU_Cfam_GSD_1.0.115.entrez.tsv.gz": 18000,
    "Canis_lupus_familiarisgreatdane.UMICH_Zoey_3.1.115.entrez.tsv.gz": 13000,
    # Pig. gene2ensembl carries ENSSSCG00000, spread over three Sscrofa11.1 releases
    # because each drops xrefs the others keep; the breed assemblies are sole sources.
    "Sus_scrofa.Sscrofa11.1.106.entrez.tsv.gz": 15000,
    "Sus_scrofa.Sscrofa11.1.115.entrez.tsv.gz": 14000,
    "Sus_scrofa.Sscrofa11.1.116.entrez.tsv.gz": 15000,
    "Sus_scrofa_wuzhishan.minipig_v1.0.115.entrez.tsv.gz": 6000,
    "Sus_scrofa_tibetan.Tibetan_Pig_v2.115.entrez.tsv.gz": 8000,
    "Sus_scrofa_largewhite.Large_White_v1.115.entrez.tsv.gz": 10000,
    # X. tropicalis. Same ID series as gene2ensembl, but better covered here.
    "Xenopus_tropicalis.UCB_Xtro_10.0.115.entrez.tsv.gz": 17000,
}


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
    filter_ids: List[Union[int, str]] = None,  # [9031]
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
        include_curie=["MGI:", "RGD:", "FB:", "WB:", "ZFIN:", "Xenbase:", "SGD:"],
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


def ensembl_entrez_mapping(filename: str) -> DataFrame:
    """
    Map an Ensembl gene ID series to NCBIGene from one Ensembl entrez xref TSV.

    Each file covers a single species and genome assembly, and the gene ID series is
    assembly-specific, so several files per species are needed to resolve the ID series
    our various ingest sources emit.

    The files carry two kinds of row, distinguished by db_name: 'EntrezGene' rows whose
    xref is the NCBI gene ID we want, and 'EntrezGene_trans_name' rows whose xref is a
    transcript name such as 'HMOX1-201'. Only the former are mappings.

    :param filename: Path to a gzipped Ensembl <species>.<assembly>.<release>.entrez.tsv.gz
    :return: DataFrame of NCBIGene-ENSEMBL mappings
    """
    df = pd.read_csv(filename, compression="gzip", sep="\t")
    return df_mappings(
        df=df,
        subject_column="xref",
        subject_curie_prefix="NCBIGene:",
        object_column="gene_stable_id",
        object_curie_prefix="ENSEMBL:",
        predicate_id="skos:exactMatch",
        mapping_justification="semapv:UnspecifiedMatching",
        filter_column="db_name",
        filter_ids=["EntrezGene"],
    )


# Dictyostelium discoideum AX4. NCBI files dicty genes under this strain taxon; the KG
# nodes carry the species taxon (44689), but we match on the dictyBase xref rather than
# taxon, so the difference does not matter here.
DICTY_TAXON = 352472


def dictybase_mapping(gene_info_path: str) -> DataFrame:
    """
    Map dictyBase gene IDs to NCBIGene, read out of NCBI's gene_info.

    Dicty has a naming authority but no Alliance cross-reference rows, so the usual
    route does not reach it. gene_info carries the dictyBase ID directly in its
    pipe-delimited dbXrefs column, e.g.
    ``dictyBase:DDB_G0294382|AmoebaDB:DDB_G0294382|VEuPathDB:DDB_G0294382``.

    (The LocusTag column happens to hold the same DDB_G identifier for every dicty gene,
    but that is a quirk of dicty's naming rather than a declared cross-reference, so the
    xref is what we read.)

    :param gene_info_path: Path to a gzipped NCBI gene_info file
    :return: DataFrame of dictyBase-NCBIGene mappings
    """
    df = pd.read_csv(
        gene_info_path, compression="gzip", sep="\t", usecols=["#tax_id", "GeneID", "dbXrefs"]
    ).rename(columns={"#tax_id": "tax_id"})
    df = df[df["tax_id"] == DICTY_TAXON].copy()
    df["dictybase_id"] = df["dbXrefs"].str.extract(r"dictyBase:([^|]+)")
    df = df.dropna(subset=["dictybase_id"])

    return df_mappings(
        df=df,
        subject_column="dictybase_id",
        object_column="GeneID",
        subject_curie_prefix="dictyBase:",
        object_curie_prefix="NCBIGene:",
        predicate_id="skos:exactMatch",
        mapping_justification="semapv:UnspecifiedMatching",
    )


def emitted_prefixes(mappings: DataFrame) -> List[str]:
    """
    The CURIE prefixes a generated mapping set actually uses on either side.

    Read off the data rather than restated anywhere, so a new source cannot be added
    without its prefix being accounted for.

    :param mappings: DataFrame with subject_id and object_id columns
    :return: Sorted list of distinct prefixes
    """
    ids = pd.concat([mappings["subject_id"], mappings["object_id"]])
    return sorted(set(ids.str.extract(r"^([^:]+):", expand=False).dropna()))


def prefixmaps_curie_map(prefixes: List[str], converter) -> dict:
    """
    Build a curie_map from the converter the CURIEs were standardized against.

    Taking the expansions from the converter rather than hand-maintaining them keeps the
    published curie_map honest: it says how these identifiers were actually produced, and
    a prefix added by a new source is covered without anyone editing a YAML file. It also
    keeps one convention throughout -- prefixmaps is uniformly identifiers.org for the
    prefixes we emit -- instead of mixing registry URIs with human-facing resolver URLs.

    :param prefixes: Prefixes to declare
    :param converter: curies.Converter the mapping set was standardized against
    :return: Mapping of prefix to canonical URI prefix
    :raises ValueError: If the converter has no expansion for a prefix
    """
    curie_map = {}
    missing = []
    for prefix in prefixes:
        uri_prefix = converter.bimap.get(prefix)
        if uri_prefix is None:
            missing.append(prefix)
        else:
            curie_map[prefix] = uri_prefix
    if missing:
        raise ValueError(
            f"No expansion in the prefix map for {sorted(missing)}. A source is emitting a "
            f"prefix the converter does not know; either the prefix is wrong or it needs "
            f"adding upstream in prefixmaps."
        )
    return curie_map


def generate_gene_mappings() -> DataFrame:
    mapping_dataframes = []

    ### Alliance mappings
    print("Generating Alliance mappings...")
    alliance_mappings = alliance_mapping()
    print(f"Generated {len(alliance_mappings)} Alliance mappings")
    assert len(alliance_mappings) > 400000

    # Guarded separately because the cost of losing these is invisible here: yeast genes
    # are SGD nodes in the KG and nothing else in this file maps to them, so dropping
    # SGD from include_curie silently strands every BioGRID yeast interaction.
    sgd_mappings = alliance_mappings[alliance_mappings["subject_id"].str.startswith("SGD:")]
    print(f"  ...of which {len(sgd_mappings)} are SGD mappings")
    assert len(sgd_mappings) > 10000, f"Expected > 10000 SGD mappings, got {len(sgd_mappings)}"

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

    print("\nGenerating NCBIGene to ENSEMBL Gene mappings from gene2ensembl.gz...")
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

    ensembl_frames = []
    for filename, minimum in ENSEMBL_ENTREZ_FILES.items():
        print(f"\nGenerating NCBIGene to ENSEMBL Gene mappings from {filename}...")
        ensembl_to_ncbi_by_assembly = ensembl_entrez_mapping(f"data/ensembl/{filename}")
        print(f"Generated {len(ensembl_to_ncbi_by_assembly)} ENSEMBL-NCBIGene Gene mappings from {filename}")
        assert len(ensembl_to_ncbi_by_assembly) > minimum, (
            f"Expected > {minimum} mappings from {filename}, got {len(ensembl_to_ncbi_by_assembly)}"
        )
        ensembl_frames.append(ensembl_to_ncbi_by_assembly)

    # A gene keeps its ID across the releases and assemblies it appears in, so the same
    # pair is emitted by several of these files. Deduplicate the group rather than
    # writing the repeats out: with 20 files they would be 28% of the Ensembl rows.
    ensembl_to_ncbi_all = pd.concat(ensembl_frames).drop_duplicates()
    print(f"\n{len(ensembl_to_ncbi_all)} distinct ENSEMBL-NCBIGene mappings across "
          f"{len(ENSEMBL_ENTREZ_FILES)} assembly files")
    mapping_dataframes.append(ensembl_to_ncbi_all)

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
    assert len(uniprot_to_ncbi) > 70000, f"Expected > 70000 mappings for uniprot_to_ncbi, got {len(uniprot_to_ncbi)}"
    mapping_dataframes.append(uniprot_to_ncbi)

    print("\nGenerating dictyBase to NCBI Gene mappings...")
    dictybase_to_ncbi = dictybase_mapping("data/ncbi/gene_info.gz")
    print(f"Generated {len(dictybase_to_ncbi)} dictyBase-NCBIGene mappings")
    assert len(dictybase_to_ncbi) > 11000, (
        f"Expected > 11000 dictyBase mappings, got {len(dictybase_to_ncbi)}"
    )
    mapping_dataframes.append(dictybase_to_ncbi)

    print("\nGenerating PomBase to NCBI Gene mappings...")
    ncbigene_df = pd.read_csv("data/ncbi/gene_info.gz", compression="gzip", sep="\t", usecols=["#tax_id", "GeneID", "LocusTag"])
    # rename #tax_id column to tax_id
    ncbigene_df.rename(columns={"#tax_id": "tax_id"}, inplace=True)
    # filter to just pombe
    ncbigene_df = ncbigene_df[ncbigene_df["tax_id"] == 4896]

    pombase_to_ncbi = df_mappings(df=ncbigene_df,
                subject_column="LocusTag",
                object_column="GeneID",
                subject_curie_prefix="PomBase:",
                object_curie_prefix="NCBIGene:",
                predicate_id="skos:exactMatch",
                mapping_justification="semapv:UnspecifiedMatching")
    pombase_to_ncbi['subject_id'] = pombase_to_ncbi['subject_id'].str.replace("SPOM_","") # remove SPOM_ prefix
    valid_pombase_genes = pd.read_csv("data/pombase/gene_IDs_names_products.tsv",
                                      sep="\t", usecols=["gene_systematic_id_with_prefix"])
    # only keep rows where the subject_id is in valid_pombase_genes
    pombase_to_ncbi = pombase_to_ncbi[pombase_to_ncbi["subject_id"].isin(valid_pombase_genes["gene_systematic_id_with_prefix"])]
    assert len(pombase_to_ncbi) > 6000
    mapping_dataframes.append(pombase_to_ncbi)

    mappings = pd.concat(mapping_dataframes)
    for row in mappings.itertuples():
        assert not ("<NA>" in row.subject_id)
        assert not ("<NA>" in row.object_id)
    return mappings
