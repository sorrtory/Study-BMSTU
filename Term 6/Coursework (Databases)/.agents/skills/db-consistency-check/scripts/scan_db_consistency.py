#!/usr/bin/env python3
"""Lightweight scanner for coursework database model consistency.

The script intentionally reports candidates and suspicions. A Codex agent using
the skill must still inspect the referenced files and make the final judgment.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path


ROOT = Path.cwd()
DOCS = ROOT / "src" / "docs"
REPORT = ROOT / "report"
CODE_DIRS = [ROOT / "src" / "apps", ROOT / "src" / "grafana"]

EXPECTED_DOCS = {
    "er": DOCS / "er.md",
    "pg_jsonb": DOCS / "rel_jsonb.md",
    "pg_norm": DOCS / "rel_norm.md",
    "mongo_nested": DOCS / "doc_nested.md",
    "mongo_norm": DOCS / "doc_norm.md",
}

REPORT_HINTS = {
    "pg_jsonb": REPORT / "Content" / "032_pg_jsonb.tex",
    "pg_norm": REPORT / "Content" / "032_pg_norm.tex",
    "mongo_nested": REPORT / "Content" / "033_mdb_nested.tex",
    "mongo_norm": REPORT / "Content" / "034_mdb_ref.tex",
}


@dataclass(frozen=True)
class MermaidEntity:
    name: str
    fields: tuple[str, ...]


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="utf-8", errors="replace")


def line_of(text: str, needle: str) -> int:
    idx = text.find(needle)
    if idx < 0:
        return 1
    return text.count("\n", 0, idx) + 1


def normalize_name(name: str) -> str:
    return name.strip().lower().replace("\\_", "_").replace("-", "_")


def parse_mermaid_entities(text: str) -> dict[str, MermaidEntity]:
    entities: dict[str, MermaidEntity] = {}
    pattern = re.compile(r"^\s*([A-Z][A-Z0-9_]*)\s*\{\s*$([\s\S]*?)^\s*\}\s*$", re.M)
    for match in pattern.finditer(text):
        name = normalize_name(match.group(1))
        fields: list[str] = []
        for raw in match.group(2).splitlines():
            raw = raw.strip()
            if not raw:
                continue
            parts = raw.split()
            if len(parts) >= 2 and parts[1] in {"ID", "PK", "FK", "UK", "AK", "ㅤ"}:
                fields.append(normalize_name(parts[0]))
            elif len(parts) >= 2:
                fields.append(normalize_name(parts[1]))
        entities[name] = MermaidEntity(name=name, fields=tuple(fields))
    return entities


def parse_mermaid_relationships(text: str) -> list[tuple[str, str, str]]:
    rels: list[tuple[str, str, str]] = []
    rel_re = re.compile(r"^\s*([A-Z][A-Z0-9_]*)\s+([}|o\-\{]+)\s+([A-Z][A-Z0-9_]*)\s*:", re.M)
    for left, card, right in rel_re.findall(text):
        rels.append((normalize_name(left), card, normalize_name(right)))
    return rels


def extract_jsonb_fields(entities: dict[str, MermaidEntity]) -> list[str]:
    out: list[str] = []
    for entity in entities.values():
        for field in entity.fields:
            # Type information is not retained here, so inspect original via field names
            # that this coursework uses for JSONB-bearing attributes.
            if field in {"settings", "event_payload", "bounding_box", "attributes", "parameters"}:
                out.append(f"{entity.name}.{field}")
    return sorted(out)


def grep_files(base: Path, suffixes: tuple[str, ...]) -> list[Path]:
    if not base.exists():
        return []
    ignored_parts = {"node_modules", "dist", "build", ".pnpm", ".vite", "coverage"}
    return sorted(
        p
        for p in base.rglob("*")
        if p.is_file()
        and p.suffix in suffixes
        and not ignored_parts.intersection(p.relative_to(ROOT).parts)
    )


def collect_mentions(paths: list[Path], terms: set[str]) -> dict[str, list[str]]:
    mentions: dict[str, list[str]] = {term: [] for term in sorted(terms)}
    term_patterns = {
        term: re.compile(rf"(?<![A-Za-z0-9_]){re.escape(term).replace('_', r'(?:_|\\\\_)')}(?![A-Za-z0-9_])", re.I)
        for term in terms
        if term
    }
    for path in paths:
        text = read_text(path)
        for line_no, line in enumerate(text.splitlines(), 1):
            for term, pattern in term_patterns.items():
                if pattern.search(line):
                    rel = path.relative_to(ROOT)
                    mentions[term].append(f"{rel}:{line_no}")
    return {k: v for k, v in mentions.items() if v}


def code_schema_signals() -> list[str]:
    signals: list[str] = []
    schema_patterns = [
        re.compile(r"\bCREATE\s+TABLE\b", re.I),
        re.compile(r"\bINSERT\s+INTO\b", re.I),
        re.compile(r"\bSELECT\b.+\bFROM\b", re.I),
        re.compile(r"\bDELETE\s+FROM\b", re.I),
        re.compile(r"\bCollection\s*\(", re.I),
        re.compile(r"\.Collection\s*\(", re.I),
        re.compile(r"\bdb\.[A-Za-z0-9_]+\b", re.I),
    ]
    sql_only_patterns = [
        re.compile(r"\bUPDATE\s+[A-Za-z_][A-Za-z0-9_]*\s+SET\b", re.I),
    ]
    for base in CODE_DIRS:
        for path in grep_files(base, (".go", ".ts", ".tsx", ".js", ".sql", ".yml", ".yaml", ".json")):
            text = read_text(path)
            for line_no, line in enumerate(text.splitlines(), 1):
                patterns = schema_patterns
                if path.suffix == ".sql":
                    patterns = schema_patterns + sql_only_patterns
                if any(pattern.search(line) for pattern in patterns):
                    rel = path.relative_to(ROOT)
                    signals.append(f"{rel}:{line_no}: {line.strip()[:160]}")
    return signals


def print_entities(label: str, path: Path, entities: dict[str, MermaidEntity]) -> None:
    print(f"\n## {label}: {path.relative_to(ROOT)}")
    if not path.exists():
        print("MISSING")
        return
    print(f"entities/tables: {len(entities)}")
    for name, entity in sorted(entities.items()):
        print(f"- {name}: {', '.join(entity.fields)}")


def main() -> int:
    print("# DB consistency scan")
    print(f"root: {ROOT}")

    missing = [path for path in EXPECTED_DOCS.values() if not path.exists()]
    if missing:
        print("\n## Missing expected source-of-truth docs")
        for path in missing:
            print(f"- {path.relative_to(ROOT)}")

    parsed: dict[str, dict[str, MermaidEntity]] = {}
    relationships: dict[str, list[tuple[str, str, str]]] = {}
    for label, path in EXPECTED_DOCS.items():
        if not path.exists():
            parsed[label] = {}
            relationships[label] = []
            continue
        text = read_text(path)
        parsed[label] = parse_mermaid_entities(text)
        relationships[label] = parse_mermaid_relationships(text)
        print_entities(label, path, parsed[label])
        if relationships[label]:
            print("relationships:")
            for left, card, right in relationships[label]:
                print(f"- {left} {card} {right}")

    print("\n## Cross-model quick checks")
    er_entities = set(parsed["er"])
    for label in ("pg_jsonb", "pg_norm"):
        model_entities = set(parsed[label])
        if model_entities:
            missing_concepts = sorted(
                concept for concept in er_entities
                if concept not in model_entities and concept not in {"camera_telemetry"}
            )
            if missing_concepts:
                print(f"- suspicion: {label} lacks direct entities: {', '.join(missing_concepts)}")
    if "camera_telemetry" in er_entities:
        for label in ("pg_jsonb", "pg_norm"):
            if "camera_log" in parsed[label] and "camera_telemetry" not in parsed[label]:
                print(f"- naming drift candidate: ER camera_telemetry maps to {label} camera_log; verify text explains it")

    jsonb_fields = extract_jsonb_fields(parsed["pg_jsonb"])
    if jsonb_fields:
        print(f"- pg_jsonb JSON-like fields by name: {', '.join(jsonb_fields)}")
    norm_jsonb_fields = extract_jsonb_fields(parsed["pg_norm"])
    if norm_jsonb_fields:
        print(f"- suspicion: pg_norm still has JSON-like field names: {', '.join(norm_jsonb_fields)}")

    report_files = grep_files(REPORT / "Content", (".tex",)) + [REPORT / "content.tex"]
    terms: set[str] = set()
    for model in parsed.values():
        terms.update(model.keys())
        for entity in model.values():
            terms.update(entity.fields)
    terms.update({"event_payload", "camera_log", "camera_telemetry", "settings", "parameters"})
    mentions = collect_mentions(report_files, terms)
    print("\n## Report mention coverage")
    for label, hint in REPORT_HINTS.items():
        status = "exists" if hint.exists() else "missing"
        print(f"- {label}: {hint.relative_to(ROOT)} ({status})")
    for term in sorted(k for k, v in mentions.items() if len(v) <= 3):
        print(f"- sparse mention: {term}: {', '.join(mentions[term])}")

    print("\n## Code schema signals")
    signals = code_schema_signals()
    if not signals:
        print("- no DDL/DML/collection schema signals found in src/apps or src/grafana")
        print("- residual risk: code may only contain connection plumbing or schema may live elsewhere")
    else:
        for signal in signals[:200]:
            print(f"- {signal}")
        if len(signals) > 200:
            print(f"- ... {len(signals) - 200} more signals")

    print("\n## Manual follow-up required")
    print("- Inspect each suspicion above before declaring a final verdict.")
    print("- Compare exact semantics, because LaTeX escaping and naming aliases can be legitimate.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
