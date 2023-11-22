"""
Script to process the registry and transform the mapping sets into Turtle to
upload on OxO2
"""

import argparse
import uuid
from typing import List, Tuple

import yaml
from pyld.jsonld import expand
from rdflib import Graph
from sssom.parsers import parse_sssom_table
from sssom.writers import to_json
from sssom_schema import SSSOM, MappingRegistry, MappingSetReference


def registry_parser(config: str) -> MappingRegistry:
    """ Parse registry and return MappingRegistry """
    with open(file=config, mode="r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    map_set_refs = (
        MappingSetReference(
            mapping_set_id=mapping["mapping_set_id"],
            mapping_set_group=mapping["mapping_set_group"] if mapping.get(
                "mapping_set_group"
            ) else None,
            local_name=mapping["local_name"],
        )
        for mapping in data["mapping_set_references"]
    )

    return MappingRegistry(
        mapping_registry_id=data["mapping_registry_id"],
        mapping_registry_title=data["mapping_registry_title"],
        mapping_registry_description=data["mapping_registry_description"],
        homepage=data["homepage"],
        mapping_set_references=list(map_set_refs),
    )


def generate_uuid(entry: List) -> Tuple[str, str]:
    """ Generate uuid for mappings and mapping sets """
    input_concat = "".join(entry)
    uu_id = uuid.uuid5(uuid.NAMESPACE_DNS, input_concat)
    uu_id = str(uu_id).replace("-", "")

    return f"{SSSOM}{uu_id}", uu_id


def update_context(entry: dict) -> dict:
    """ Fix context adding type and add uuid to context """
    for _, value in entry["@context"].items():
        if not isinstance(value, dict):
            continue

        if not value.get("@type"):
            continue

        if value["@type"] != "rdfs:Resource":
            continue

        value["@type"] = "@id"

    entry["@context"]["uuid"] = {"@type": "xsd:string"}

    return entry


def add_uuid_n_expand_curie(entry: dict) -> dict:
    """ Add uuid and expand curie to mappings """
    entry["@id"], entry["uuid"] = generate_uuid([entry["mapping_set_id"]])

    if not entry.get("mappings"):
        return entry

    context = get_context(entry)

    for mapping in entry["mappings"]:
        mapping_key = [
            mapping["subject_id"],
            mapping["predicate_id"],
            mapping["object_id"],
            mapping["mapping_justification"],
        ]
        mapping["@id"], mapping["uuid"] = generate_uuid(mapping_key)
        mapping["@type"] = "Mapping"

        mapping["subject_id"] = expand_curie(mapping["subject_id"], context)
        mapping["object_id"] = expand_curie(mapping["object_id"], context)
        # Add default confidence 1 for each mapping
        mapping["confidence"] = 1.0
    return entry


def get_context(entry: dict) -> dict:
    """ Get context """
    return entry["@context"]


def expand_curie(curie, context):
    """ Expand curie """
    namespace = curie.split(":")[0]
    if "http" in namespace:
        return curie

    return curie.replace(f"{namespace}:", context[f"{namespace}"])


def read_mappings(config: str):
    """ Transform to ttl all mapping sets listed in the registry """
    registry = registry_parser(config)

    for _, mapping_set_ref in registry.mapping_set_references.items():
        print(f"Parsing mapping_set_id {mapping_set_ref.mapping_set_id}")

        mapping_json = update_context(
            add_uuid_n_expand_curie(
                to_json(
                    parse_sssom_table(
                        f"mappings/{mapping_set_ref.local_name}"
                    )
                )
            )
        )

        context = get_context(mapping_json)

        g = Graph()
        g.parse(data={"@graph": expand(mapping_json, None)}, format="json-ld")
        g.parse(data={"@context": context}, format="json-ld")

        g.serialize(
            f"mappings/ttl/{mapping_set_ref.local_name}.ttl", format="turtle"
        )


def main(entry: dict):
    """ Main """
    read_mappings(entry.registry)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("registry", help="registry file with mappings")

    args = parser.parse_args()
    main(args)
