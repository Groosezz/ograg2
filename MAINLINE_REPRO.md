# OG-RAG Mainline Reproduction

This project has many experimental branches.  
The mainline reproduction path is:

1. Ontology mapping (`md/pdf` -> `ontology/*.jsonld`)
2. Triple generation (`ontology/*.jsonld` -> `*_triples.pkl`)
3. Ontology-hypergraph querying (`query.method = ontohypergraph-rag`)

## 1) Prerequisites

Set model credentials via either:

- `api_keys.yaml` in repo root, or
- environment variables (`OPENAI_API_KEY`, and optional Azure variables).

Install dependencies:

```bash
pip install -r requirements.txt
```

## 2) Use the dedicated mainline configs

- Soybean: `configs/mainline/config_soybean_mainline.yaml`
- Wheat: `configs/mainline/config_wheat_mainline.yaml`

## 3) One-command runner

Run full pipeline:

```bash
python run_mainline.py --config_file configs/mainline/config_soybean_mainline.yaml
```

Useful variants:

```bash
# rebuild ontology + triples, then query
python run_mainline.py --config_file configs/mainline/config_soybean_mainline.yaml --force_map_ontology --force_create_kg_triples

# build only ontology mapping
python run_mainline.py --config_file configs/mainline/config_soybean_mainline.yaml --only_map_ontology

# query only (reuse existing ontology/triples)
python run_mainline.py --config_file configs/mainline/config_soybean_mainline.yaml --skip_build
```

## 4) Manual equivalent commands

```bash
python build_knowledge_graph.py --config_file configs/mainline/config_soybean_mainline.yaml
python query_llm.py --config_file configs/mainline/config_soybean_mainline.yaml
```

