"""
Unit tests for the UniProt ID mapping preprocessing
"""
from typing import Tuple

import pytest

from monarch_gene_mapping.uniprot_idmapping_preprocess import target_taxon


@pytest.mark.parametrize(
    "query",
    [
        (
            # NCBITaxon:10090, Mus musculus - yes, of interest to us
            "Q9Z131	3BP5_MOUSE	24056	NP_001334514.1; NP_036024.2	124028537; 148692861		"
            "GO:0005737; GO:0061099	UniRef100_Q9Z131	UniRef90_O60239	UniRef50_O60239	UPI0000ED8F31		"
            "10090			16141072; 15489334	AK043375; AK161427; BC018237; BC053741; AB016835	"
            "BAC31530.1; BAE36389.1; AAH18237.2; AAH53741.2; BAA75641.1	ENSMUSG00000021892	"
            "ENSMUST00000091903; ENSMUST00000100730	ENSMUSP00000089517; ENSMUSP00000117152	"
            "21844199; 28661486",
            True,
        ),
        (  # NCBITaxon:654924, Frog virus 3 (isolate Goorha) - no, not of interest to us
            "Q6GZX4	001R_FRG3G	2947773	YP_031579.1	81941549; 49237298		GO:0046782	UniRef100_Q6GZX4	"
            "UniRef90_Q6GZX4	UniRef50_Q6GZX4	UPI00003B0FD4		654924			15165820	"
            "AY548484	AAT09660.1				",
            False,
        ),
    ],
)
def test_target_taxon(query: Tuple[str, bool]):
    assert target_taxon(query[0]) is query[1]
