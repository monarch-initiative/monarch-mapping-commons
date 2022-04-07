import logging
from os.path import join, dirname, realpath
from pathlib import Path
from sssom.parsers import read_sssom_table
from sssom.writers import write_table
from sssom.util import MappingSetDataFrame, reconcile_prefix_and_data
import pandas as pd
import yaml
import click


@click.group()
def cli():
    pass

def _get_defaults_from_registry()-> dict:
    REGISTRY_YAML = dirname(dirname(realpath(__file__)))+"/registry.yaml"
    with open(REGISTRY_YAML, "r") as r:
        all_defaults = yaml.safe_load(r)
    return all_defaults["mapping_set_references"]

def _get_matching_dict(param:str, val:str)->dict:
    default_map_refs = _get_defaults_from_registry()
    map_ref = [
        item for item in default_map_refs if item[param] == val
    ]

    if len(map_ref )== 1:
        return map_ref[0]
    elif len(map_ref) > 1:
        logging.warning(f"registry.yaml file has multiple configurations for {param}: {val}.")
        return map_ref[0]
    else:
        logging.warning(f"No default value for {param} in the registry.yaml file.")


def _load_default_info(msdf:MappingSetDataFrame)-> MappingSetDataFrame:
    """
    Load MappingSetDataFrame object with default values from global config (registry.yaml).

    :param msdf: Input MappingSetDataFrame object.
    :return: Output MappingSetDataFrame with default values.
    """
    if msdf.metadata["mapping_set_id"]:
        relevant_map = _get_matching_dict("mapping_set_id", msdf.metadata["mapping_set_id"])
        if relevant_map:
            if "mirror_from" in relevant_map.keys():
                relevant_map.pop('mirror_from')
            msdf.df["confidence"] = relevant_map["registry_confidence"]
        else:
            map_id = msdf.metadata["mapping_set_id"]
            logging.warning(f"mapping_set_id :{map_id} \
                does not have default values")
    else:
        logging.warning(f"There seems to be no default values\
             for mapping_set_id provided.")
    return msdf


@cli.command()
@click.option("--config", "-c", type=click.Path(exists=True), help=f"Path to the config folder.")
@click.option("--source-location", "-s", type=click.Path() , help=f"Path to source of individual sssom.tsv files.")
@click.option("--target-location", "-t", type=click.Path(), help=f"Path to save the combined.sssom.tsv and prefix.yaml files.")
def run(config:Path, source_location:Path, target_location:Path):
    # Variables
    PREFIX_YAML_FILE = join(target_location, "prefix.yaml")
    COMBINED_SSSOM = join(target_location, "combined.sssom.tsv")

    with open(config, "rb") as c:
        config_yaml = yaml.safe_load(c)

    _, id = target_location.split('/')

    concerned_run_list = [
                        info for info in config_yaml["config"]["boomer_config"]["runs"]
                        if info["id"] == id
                    ]

    if len(concerned_run_list) == 1 :
        concerned_run = concerned_run_list[0]
    elif len(concerned_run_list) > 1:
        logging.warning(f"{config} file has multiple configurations for id = {id}")
    else:
        logging.warning(f"{config} file does not have configuration for id = {id}")

    mapping_files = concerned_run["mappings"]

    metadata = dict()
    prefix_map = dict()
    msdf_list = []
    df_list = []

    for fn in mapping_files:

        mapping_ref = [
            info for info in config_yaml["mapping_registry"]["mapping_set_references"]
            if info["local_name"] == fn
        ]
        if len(mapping_ref) == 1 :
            concerned_map = mapping_ref[0]
            confidence = concerned_map["registry_confidence"]
        elif len(mapping_ref) > 1:
            logging.warning(f"{config} file has multiple \
                    mapping_set_reference for local_name = {fn}")
            concerned_map = mapping_ref[0]
            confidence = concerned_map["registry_confidence"]
        else:
            logging.warning(f"{config} file does not have \
                mapping_set_reference for local_name = {fn}")

        fp = join(source_location, fn)
        print(f"Loading file:{fn} ")
        msdf = read_sssom_table(fp)
        # confidence, metadata and prefix_map from global config.
        msdf = _load_default_info(msdf)
        # confidence, metadata and prefix_map from local config.
        msdf.df['confidence'] = confidence
        metadata.update({k:v for k,v in msdf.metadata.items() if k not in metadata.keys()})
        prefix_map.update({k:v for k,v in msdf.prefix_map.items() if k not in prefix_map.keys()})
        msdf_list.append(msdf)
        df_list.append(msdf.df)

    combined_df = pd.concat(df_list, axis=0, ignore_index=True)
    combined_df = combined_df.drop_duplicates()
    combined_msdf = MappingSetDataFrame(df=combined_df, prefix_map=prefix_map, metadata=metadata)

    export_msdf = reconcile_prefix_and_data(combined_msdf,config_yaml["custom_prefix_map"])

    with open(PREFIX_YAML_FILE, "w+") as yml:
        yaml.dump(export_msdf.prefix_map,yml)
    with open(COMBINED_SSSOM, "w") as combo_file:
        write_table(export_msdf, combo_file)


if __name__ == "__main__":
    cli()
