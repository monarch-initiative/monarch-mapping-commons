# monarch-mapping-commons

A collection of all SSSOM-style mapping files used for the Monarch Initiative knowledge graph

## Repository Structure

* [config/](config/) - configuration files
    * [inverse_predicate_map.yml](config/inverse_predicate_map.yml)
    * [project-cruft.json](config/project-cruft.json) -- edit this if you need to change any of the project template values in [.cruft.json](.cruft.json)
* [mappings/](mappings/) - SSSOM mapping files (do not edit these)
* [src/](src/) - source files (edit these)


## Developer Documentation

To update the mapping registry from OLS:

```sh
sh odk.sh make update_registry -B
```

To update the mappings:

```sh
sh odk.sh make mappings
```

If the run requires a recently published SSSOM or OAK feature, first update ODK:

```sh
docker pull obolibrary/odkfull:dev
```

and then run the `dependencies` goal together with the mappings goal:


```sh
IMAGE=odkfull:dev sh odk.sh make mappings
```
For Windows, append `:dev` to `obolibrary/odkfull` in the `odk.bat` file.

*Note: If running on a Windows machine, replace `sh odk.sh` with `odk.bat` in the above commands.*

## Design decisions:

1. Only mappings of base entities are extracted. This ensures that we do not import the same UBERON mapping for every species specific anatomy ontology (XAO). This is realised as a filtering step that relies on the crude assumption that the ontology ID is somehow reflected in the subject_id.


## Credits

This project was made with the
[mapping-commons-cookiecutter](https://github.com/mapping-commons/mapping-commons-cookiecutter).