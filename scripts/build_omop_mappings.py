"""
Build OMOP concept_id -> source-vocabulary identity mappings for the BDC priority measurement terms.

An OMOP concept_id is a surrogate key OHDSI assigns to a term loaded verbatim from a source vocabulary.
The OMOP CONCEPT row records that term's native vocabulary_id and concept_code, so subject and object
denote the same concept (skos:exactMatch). This is not the OHDSI "Maps to" relation.

Input: the OMOP CURIEs in MeasurementObservationTypeEnum of the BDC harmonized model (bdchm.yaml).
Concepts are resolved in one batch call to an OHDSI WebAPI, whose vocabulary version is recorded
as subject_source_version.
"""

from __future__ import annotations

import csv
import sys
from datetime import date
from pathlib import Path

import click
import requests
import yaml

HERE = Path(__file__).parent.resolve()
ROOT = HERE.parent.resolve()

BDCHM_URL = "https://raw.githubusercontent.com/RTIInternational/NHLBI-BDC-DMC-HM/main/src/bdchm/schema/bdchm.yaml"
ENUM_NAME = "MeasurementObservationTypeEnum"
WEBAPI_URL = "https://api.ohdsi.org/WebAPI"
WEBAPI_SOURCE = "ATLASPROD"

# OMOP vocabulary_id -> (object prefix, whether labels may be published)
# SNOMED CT description text is UMLS-license-gated, and for a SNOMED-sourced concept the OMOP
# concept_name IS that text, so both label columns are left blank.
VOCABULARIES = {
    "LOINC": ("LOINC", True),
    "SNOMED": ("SNOMEDCT", False),
}

COLUMNS = [
    "subject_id",
    "subject_label",
    "predicate_id",
    "object_id",
    "object_label",
    "mapping_justification",
    "comment",
]


def load_text(location: str) -> str:
    """Read a local path or URL."""
    if location.startswith(("http://", "https://")):
        res = requests.get(location, timeout=60)
        res.raise_for_status()
        return res.text
    return Path(location).read_text(encoding="utf-8")


def omop_ids_from_enum(schema_text: str) -> list[int]:
    """Return the OMOP concept_ids used as `meaning` in the measurement enum."""
    schema = yaml.safe_load(schema_text)
    values = schema["enums"][ENUM_NAME]["permissible_values"]
    curies = {(v or {}).get("meaning") for v in values.values()}
    return sorted(int(c.split(":", 1)[1]) for c in curies if c and c.startswith("OMOP:"))


def fetch_concepts(concept_ids: list[int]) -> dict[int, dict]:
    """Resolve concept_ids in one WebAPI call."""
    res = requests.post(
        f"{WEBAPI_URL}/vocabulary/{WEBAPI_SOURCE}/lookup/identifiers",
        json=concept_ids,
        timeout=120,
    )
    res.raise_for_status()
    return {c["CONCEPT_ID"]: c for c in res.json()}


def fetch_vocabulary_version() -> str:
    res = requests.get(f"{WEBAPI_URL}/vocabulary/{WEBAPI_SOURCE}/info", timeout=60)
    res.raise_for_status()
    return res.json()["version"]


def comment_for(concept: dict) -> str:
    domain = concept["DOMAIN_ID"]
    concept_class = concept["CONCEPT_CLASS_ID"]
    if concept["VOCABULARY_ID"] == "LOINC":
        if concept["CONCEPT_CODE"].startswith("LP"):
            return (
                f"LOINC Part code (OMOP concept_class_id '{concept_class}', "
                f"standard_concept '{concept['STANDARD_CONCEPT']}'), not a LOINC term code; "
                f"OMOP domain_id {domain}"
            )
        return f"OMOP domain_id {domain}"
    return f"OMOP domain_id {domain}; concept_class_id {concept_class}"


def build_rows(concept_ids: list[int], concepts: dict[int, dict], vocabulary: str) -> list[dict]:
    prefix, publish_labels = VOCABULARIES[vocabulary]
    rows = []
    for concept_id in concept_ids:
        concept = concepts.get(concept_id)
        if concept is None or concept["VOCABULARY_ID"] != vocabulary:
            continue
        if concept["INVALID_REASON"] != "V":
            print(f"Skipping invalid concept OMOP:{concept_id} ({concept['INVALID_REASON_CAPTION']})", file=sys.stderr)
            continue
        label = concept["CONCEPT_NAME"] if publish_labels else ""
        rows.append({
            "subject_id": f"OMOP:{concept_id}",
            "subject_label": label,
            "predicate_id": "skos:exactMatch",
            "object_id": f"{prefix}:{concept['CONCEPT_CODE']}",
            "object_label": label,
            "mapping_justification": "semapv:UnspecifiedMatching",
            "comment": comment_for(concept),
        })
    return rows


def report_unmapped(concept_ids: list[int], concepts: dict[int, dict]) -> None:
    """List concepts that fall in no output file, so exclusions are visible in the build log."""
    for concept_id in concept_ids:
        concept = concepts.get(concept_id)
        if concept is None:
            print(f"Not found in OMOP vocabulary: OMOP:{concept_id}", file=sys.stderr)
        elif concept["VOCABULARY_ID"] not in VOCABULARIES:
            print(
                f"Not mapped (vocabulary {concept['VOCABULARY_ID']}): OMOP:{concept_id} {concept['CONCEPT_CODE']}",
                file=sys.stderr,
            )


def write_sssom(rows: list[dict], metadata: dict, output: Path) -> None:
    header = yaml.safe_dump(metadata, sort_keys=False, allow_unicode=True, width=1000)
    with open(output, "w", encoding="utf-8", newline="") as f:
        for line in header.splitlines():
            f.write(f"# {line}\n")
        writer = csv.DictWriter(f, fieldnames=COLUMNS, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


@click.command()
@click.option("--vocabulary", type=click.Choice(sorted(VOCABULARIES)), required=True, help="Source vocabulary to map to")
@click.option("--metadata", "metadata_path", type=click.Path(exists=True, path_type=Path), required=True, help="Mapping set metadata yml")
@click.option("--output", type=click.Path(path_type=Path), required=True, help="Path to output SSSOM TSV")
@click.option("--input", "input_location", default=BDCHM_URL, show_default=True, help="URL or path to bdchm.yaml")
def main(vocabulary: str, metadata_path: Path, output: Path, input_location: str):
    concept_ids = omop_ids_from_enum(load_text(input_location))
    concepts = fetch_concepts(concept_ids)
    report_unmapped(concept_ids, concepts)

    rows = build_rows(concept_ids, concepts, vocabulary)

    metadata = yaml.safe_load(metadata_path.read_text(encoding="utf-8"))
    metadata["mapping_date"] = date.today().isoformat()
    metadata["subject_source_version"] = f"OMOP vocabulary {fetch_vocabulary_version()} ({WEBAPI_URL}, source {WEBAPI_SOURCE})"

    write_sssom(rows, metadata, output)
    print(f"Wrote {len(rows)} {vocabulary} mappings from {len(concept_ids)} OMOP concepts to {output}", file=sys.stderr)


if __name__ == "__main__":
    main()
