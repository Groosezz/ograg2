import argparse
import subprocess
import sys
from pathlib import Path
from typing import List


def run_command(cmd: List[str], workdir: Path) -> None:
    print(f"\n[run_mainline] Running: {' '.join(cmd)}")
    subprocess.run(cmd, cwd=workdir, check=True)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Reproduce the ontology-grounded RAG mainline: ontology mapping -> KG triples -> querying."
    )
    parser.add_argument(
        "--config_file",
        default="configs/mainline/config_soybean_mainline.yaml",
        help="Path to config yaml.",
    )
    parser.add_argument("--skip_build", action="store_true", help="Skip build_knowledge_graph stage.")
    parser.add_argument("--skip_query", action="store_true", help="Skip query_llm stage.")
    parser.add_argument("--force_map_ontology", action="store_true")
    parser.add_argument("--force_create_kg_triples", action="store_true")
    parser.add_argument("--only_map_ontology", action="store_true")
    parser.add_argument("--rewrite", action="store_true")
    args, passthrough = parser.parse_known_args()

    repo_root = Path(__file__).resolve().parent
    python_exe = sys.executable

    common_args = ["--config_file", args.config_file] + passthrough

    if not args.skip_build:
        build_cmd = [python_exe, "build_knowledge_graph.py"] + common_args
        if args.force_map_ontology:
            build_cmd.append("--force_map_ontology")
        if args.force_create_kg_triples:
            build_cmd.append("--force_create_kg_triples")
        if args.only_map_ontology:
            build_cmd.append("--only_map_ontology")
        if args.rewrite:
            build_cmd.append("--rewrite")
        run_command(build_cmd, repo_root)

    should_query = (not args.skip_query) and (not args.only_map_ontology)
    if should_query:
        query_cmd = [python_exe, "query_llm.py"] + common_args
        if args.rewrite:
            query_cmd.append("--rewrite")
        run_command(query_cmd, repo_root)


if __name__ == "__main__":
    main()
