# Monarch Reconciliation

Building a fully executable workflow for reconciling ontologies using boomer.

## How to run the workflows

Clone the repo first:

```
git clone https://github.com/monarch-initiative/boomer-workflow
cd boomer-workflow
```

Now we can run all configured workflows:

```
make all
```

You can run a specific project like this:

```
make symbiont-mondo-icd10cm
```

This will _generate_ a custom workflow for the project specified by `projects/mondo-icd10cm.symbiont.yaml`.

