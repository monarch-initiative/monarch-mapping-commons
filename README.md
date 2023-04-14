# Monarch Mapping Commons

This is the Mapping Commons of the Monarch Initiative.  
It contains all mappings used in and around the knowledge graph underlying https://monarchinitiative.org/. 

### Requirements

- [Make](https://www.gnu.org/software/make/)
- [Docker](https://www.docker.com/)
- [Python 3](https://www.python.org/downloads/) with:  
    - [J2CLI](https://github.com/kolypto/j2cli)
    - [Pandas](https://pandas.pydata.org/)
    - [Curies](https://github.com/cthoyt/curies)
    - [SSSOM-Py](https://mapping-commons.github.io/sssom-py/installation.html)

A suitable Python environment can be created with [Poetry](https://python-poetry.org/):
```
cd monarch-mapping-commons
poetry install

# Activate the environment
poetry shell
```

## How to run the workflows

Clone the repo:

```
git clone https://github.com/monarch-initiative/monarch-mapping-commons
cd monarch-mapping-commons
```

Now we can run all configured workflows:

```
MEMORY=48G sh run_build.sh
```

You can run a specific project like this:

```
make symbiont-mondo-icd10cm
```

This will _generate_ a custom workflow for the project specified by `projects/mondo-icd10cm.symbiont.yaml`.

You can update the commons workflows by running (part of `run_build.sh`):
```
sh update_registry.sh
```

# Contributing 

### Adding a New Mapping



- Add an entry in `registry.yaml` for the new mapping
- Run `sh update_registry.sh` to generate an updated Makefile
- Add the goals/processing directives to the `custom.Makefile`, which extends the generated Makefile

| **(Strongly) Recommended Tools** | |
| --- | --- |
| [curies](https://github.com/cthoyt/curies) | a Python library for idiomatic conversion between CURIEs and URIs |
| [sssom-py](https://mapping-commons.github.io/sssom-py/index.html) | a Python library for working with SSSOM files |

