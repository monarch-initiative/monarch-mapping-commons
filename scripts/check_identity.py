"""Check each OMOP -> source-code row against the OMOP CONCEPT record in the OHDSI WebAPI.

Usage: python3 check_identity.py FILE.sssom.tsv [FILE ...]   (reads stdin if FILE is "-")
"""
import csv, json, sys, urllib.request

API = "https://api.ohdsi.org/WebAPI/vocabulary/ATLASPROD/lookup/identifiers"
PREFIX_TO_VOCAB = {"LOINC": "LOINC", "SNOMEDCT": "SNOMED"}

for path in sys.argv[1:]:
    fh = sys.stdin if path == "-" else open(path, encoding="utf-8")
    rows = list(csv.DictReader((l for l in fh if not l.startswith("#")), delimiter="\t"))
    ids = [int(r["subject_id"].split(":")[1]) for r in rows]
    req = urllib.request.Request(API, data=json.dumps(ids).encode(), headers={"Content-Type": "application/json"})
    concepts = {c["CONCEPT_ID"]: c for c in json.load(urllib.request.urlopen(req, timeout=120))}

    problems = 0
    for r, cid in zip(rows, ids):
        prefix, code = r["object_id"].split(":", 1)
        c = concepts.get(cid)
        if c is None:
            msg = "not found in OMOP"
        elif c["VOCABULARY_ID"] != PREFIX_TO_VOCAB.get(prefix):
            msg = f"vocabulary {c['VOCABULARY_ID']} != {prefix}"
        elif c["CONCEPT_CODE"] != code:
            msg = f"concept_code {c['CONCEPT_CODE']} != {code}"
        elif r["subject_label"] and r["subject_label"] != c["CONCEPT_NAME"]:
            msg = f"label differs: {c['CONCEPT_NAME']!r}"
        else:
            continue
        problems += 1
        print(f"  MISMATCH {r['subject_id']} -> {r['object_id']}: {msg}")
    print(f"{path}: {len(rows)} rows checked, {problems} mismatches")
