import argparse
import json
from pathlib import Path
from typing import Any, Dict, Optional, Union


def _build_minimal_context(graph: Any) -> Dict[str, str]:
    """Build a compact @context containing only prefixes used by graph terms."""
    from rdflib.term import Literal, URIRef

    used_context: Dict[str, str] = {}

    def _record_uri(uri: URIRef) -> None:
        try:
            prefix, namespace, _ = graph.namespace_manager.compute_qname(uri)
        except Exception:
            return
        if prefix:
            used_context[prefix] = str(namespace)

    for subject, predicate, obj in graph:
        for term in (subject, predicate, obj):
            if isinstance(term, URIRef):
                _record_uri(term)
            elif isinstance(term, Literal) and term.datatype:
                _record_uri(term.datatype)

    return dict(sorted(used_context.items(), key=lambda item: item[0]))


def convert_rdf_to_jsonld(
    input_path: Union[str, Path],
    output_path: Optional[Union[str, Path]] = None,
    input_format: str = "turtle",
    context: Optional[Dict[str, Any]] = None,
    minimal_context: bool = True,
    auto_compact: bool = True,
    indent: int = 2,
) -> Path:
    """Convert an RDF ontology file (e.g., Turtle) to JSON-LD.

    Args:
        input_path: Source RDF file path.
        output_path: Destination JSON-LD path. Defaults to input path with .jsonld suffix.
        input_format: RDF input format accepted by rdflib (e.g., turtle, xml, nt).
        context: Optional JSON-LD context used for compaction.
        minimal_context: Keep only prefixes used in graph terms in @context.
        auto_compact: Enable rdflib JSON-LD compaction.
        indent: Output JSON indentation.

    Returns:
        The output JSON-LD file path.
    """
    try:
        from rdflib import Graph
    except ImportError as exc:
        raise ImportError(
            "rdflib is required. Install with: pip install rdflib rdflib-jsonld"
        ) from exc

    src = Path(input_path)
    if not src.exists():
        raise FileNotFoundError(f"Input ontology file not found: {src}")

    dst = Path(output_path) if output_path else src.with_suffix(".jsonld")
    dst.parent.mkdir(parents=True, exist_ok=True)

    graph = Graph()
    graph.parse(src.as_posix(), format=input_format)

    if minimal_context:
        auto_ctx = _build_minimal_context(graph)
        if context is None:
            context = auto_ctx
        else:
            merged_ctx = dict(auto_ctx)
            merged_ctx.update(context)
            context = merged_ctx

    serialize_kwargs: Dict[str, Any] = {"format": "json-ld"}
    if auto_compact:
        serialize_kwargs["auto_compact"] = True
    if context:
        serialize_kwargs["context"] = context

    serialized = graph.serialize(**serialize_kwargs)
    if isinstance(serialized, bytes):
        serialized = serialized.decode("utf-8")

    # Normalize output to a pretty JSON file.
    json_obj = json.loads(serialized)
    dst.write_text(
        json.dumps(json_obj, ensure_ascii=False, indent=indent),
        encoding="utf-8",
    )
    return dst


def _main() -> None:
    parser = argparse.ArgumentParser(description="Convert RDF/Turtle ontology to JSON-LD.")
    parser.add_argument("-i", "--input", required=True, help="Input RDF file path (.ttl, .rdf, ...).")
    parser.add_argument("-o", "--output", help="Output JSON-LD file path.")
    parser.add_argument(
        "--input_format",
        default="turtle",
        help="Input RDF format for rdflib (default: turtle).",
    )
    parser.add_argument(
        "--context_file",
        help="Optional JSON file containing a JSON-LD @context object.",
    )
    parser.add_argument(
        "--minimal_context",
        action="store_true",
        help="Auto-generate a minimal @context with only prefixes used in triples.",
    )
    parser.add_argument("--no_auto_compact", action="store_true", help="Disable auto compaction.")
    parser.add_argument("--indent", type=int, default=2, help="JSON indentation.")
    args = parser.parse_args()

    context = None
    if args.context_file:
        context = json.loads(Path(args.context_file).read_text(encoding="utf-8"))

    out = convert_rdf_to_jsonld(
        input_path=args.input,
        output_path=args.output,
        input_format=args.input_format,
        context=context,
        minimal_context=args.minimal_context,
        auto_compact=not args.no_auto_compact,
        indent=args.indent,
    )
    print(f"JSON-LD written to: {out}")


if __name__ == "__main__":
    _main()
