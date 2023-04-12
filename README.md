# Monarch Mapping Commons

This is the Mapping Commons of the Monarch Initiative.  
It contains all mappings used in and around the knowledge graph underlying https://monarchinitiative.org/. 

### Requirements

- [Make](https://www.gnu.org/software/make/)
- [Docker](https://www.docker.com/)
- [Jinja2](https://jinja.palletsprojects.com/en/2.11.x/)
- [Python 3](https://www.python.org/downloads/) with [Pandas](https://pandas.pydata.org/)

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

### How to add a new mapping

TBD