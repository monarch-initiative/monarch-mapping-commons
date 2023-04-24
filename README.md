# Monarch Mapping Commons

This is the Mapping Commons of the Monarch Initiative.  
It contains all mappings used in and around the knowledge graph underlying https://monarchinitiative.org/. 

### Requirements

- [Make](https://www.gnu.org/software/make/) / [build-essential](https://packages.ubuntu.com/focal/build-essential)
- [Docker](https://docs.docker.com/engine/install/)
- [Python 3](https://www.python.org/downloads/) with:  
    - [J2CLI](https://github.com/kolypto/j2cli)
    - [Pandas](https://pandas.pydata.org/)
    - [Curies](https://github.com/cthoyt/curies)
    - [SSSOM-Py](https://mapping-commons.github.io/sssom-py/installation.html)

### Installation

Clone the repo:
```
git clone https://github.com/monarch-initiative/monarch-mapping-commons
cd monarch-mapping-commons
```

Install the [requirements](#requirements) above.

A suitable Python environment can be created with [Poetry](https://python-poetry.org/):
```
cd monarch-mapping-commons
poetry install

# Activate the environment (optional)
poetry shell
```

### Usage

These make commands are designed to be run in an ODK Docker container.

- To build the Docker iamge and run all workflows:
    ```bash
    sh run_build.sh

    # Optionally specify available memory, for example
    MEMORY=48G sh run_build.sh
    ```

- The run script can be used to run a single workflow within the container, for example:
    ```bash
    sh run.sh make symbiont-mondo-icd10cm
    ```

    This will generate a custom workflow for the project specified by `projects/mondo-icd10cm.symbiont.yaml`.

- You can manually update the commons workflows by running (part of `run_build.sh`):
    ```bash
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

