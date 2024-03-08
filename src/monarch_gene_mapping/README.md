# monarch-gene-mapping

Code for mapping source namespaces to preferred namespacing

## Strategy

This repository creates SSSOM mappings between gene identifiers for use in the Monarch Knowledge Graph. Gene naming authorities (HGNC, Model Organism Databases) are the preferred identifiers, with NCBIGene as a fallback. We prefer the naming sources as the first choice source for mappings. When the naming authority doesn't provide a mapping for an identifier we need to map from, we will use the source of that identifier as a fallback. Finally, a third party gene mapping may be used as a last resort.  

## Installation

```bash
poetry install
```

## Usage

```bash
poetry run gene-mapping --help
```

is a simple UI for processing the mapping data. 

## Special Data Considerations

The UniProtKB ID mappings file is huge: about an eleven (11) gigabyte _gzip_ compressed archive (as of November 2022). 
The Monarch Initiative only targets a subset of species in this file. The standard procedure is to 'pre-filter' the
data after downloading but before continued processing. This is the default 'generate' process, but the
monarch_gene_mapping.main script allows for discrete processing of this step.

