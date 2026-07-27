#!/usr/bin/env python3
"""Sync Beezer FCLA chapter graphs from concept-book-press into public/domains/.

concept-book-press's Path-B pipeline (docs/projects/linalg/README.md) ingested
Robert Beezer's *A First Course in Linear Algebra* (FCLA, GNU FDL) chapter by
chapter and produced, per chapter, a `graph_ch{N}.yaml` (plus a
`chunks_ch{N}.yaml` carrying the chapter title and source attribution) under
concept-book-press/output/linalg/ -- a flat layout, one file per chapter,
unlike college-physics-2e's output/{book}/ch{N}/graph.yaml directory-per-
chapter layout that scripts/sync_from_press.py targets. It also produced one
merged full-book graph, graph_full.yaml (see docs/projects/linalg/merge_report.md).

This script copies those straight across (no reformatting -- the extracted
graph.yaml is already a ConceptBook `domain`/`primitives`/`concepts`/
`applications` document, byte-compatible with graph_lib.load_domain()),
renders each domain's output/graph.html navigator, and registers/refreshes
catalog.json entries with has_book=False -- book HTML generation itself is a
separate step, via scripts/batch_generate.py.

Usage:
    python scripts/sync_linalg_from_press.py                # chapters 1-8
    python scripts/sync_linalg_from_press.py --chapters 1-2,4
    python scripts/sync_linalg_from_press.py --no-full       # skip linalg_full
    python scripts/sync_linalg_from_press.py --dry-run
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
PRESS_ROOT = Path.home() / "projects" / "digital-duck" / "concept-book-press"
PRESS_LINALG_DIR = PRESS_ROOT / "output" / "linalg"
DOMAINS_ROOT = REPO_ROOT / "public" / "domains"
CATALOG_PATH = DOMAINS_ROOT / "catalog.json"
GRAPH_TOOL = REPO_ROOT / "scripts" / "concept_graph.py"

# concept-book-press's level_map.py is the single source of truth for which
# academic level a known source book targets (see that module's docstring).
sys.path.insert(0, str(PRESS_ROOT))
from pipeline.level_map import derive_level  # noqa: E402

SOURCE = {
    "title": "A First Course in Linear Algebra (FCLA), v3.50",
    "authors": "Robert A. Beezer",
    "license": "GNU Free Documentation License",
    "url": "http://linear.pugetsound.edu",
}


def _graph_stats(graph_yaml: dict) -> dict:
    primitives = graph_yaml.get("primitives", {}) or {}
    concepts = graph_yaml.get("concepts", {}) or {}
    applications = graph_yaml.get("applications", {}) or {}
    edges = sum(len(v.get("composed_of", []) or []) for v in concepts.values())
    edges += sum(len(v.get("needs", []) or []) for v in applications.values())
    return {
        "nodes": len(primitives) + len(concepts) + len(applications),
        "edges": edges,
        "primitives": len(primitives),
        "concepts": len(concepts),
        "applications": len(applications),
    }


def _pick_capstone(graph_yaml: dict) -> str | None:
    apps = graph_yaml.get("applications", {}) or {}
    if apps:
        return next(iter(apps))
    concepts = graph_yaml.get("concepts", {}) or {}
    if not concepts:
        return None
    return max(concepts, key=lambda k: concepts[k].get("tier", 0))


def _sync_one(
    domain_id: str,
    name: str,
    description: str,
    graph_src: Path,
    attribution: str | None,
    dry_run: bool,
) -> dict | None:
    if not graph_src.exists():
        print(f"  {domain_id}: SKIP (no graph.yaml at {graph_src})")
        return None

    graph_yaml = yaml.safe_load(graph_src.read_text(encoding="utf-8"))
    stats = _graph_stats(graph_yaml)
    capstone = _pick_capstone(graph_yaml)

    print(f"  {domain_id}: \"{name}\"  "
          f"(nodes={stats['nodes']} edges={stats['edges']} capstone={capstone})")

    if dry_run:
        return None

    dest_dir = DOMAINS_ROOT / domain_id
    input_dir = dest_dir / "input"
    input_dir.mkdir(parents=True, exist_ok=True)
    (input_dir / "graph.yaml").write_text(graph_src.read_text(encoding="utf-8"), encoding="utf-8")

    graph_html = dest_dir / "output" / "graph.html"
    graph_html.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [sys.executable, str(GRAPH_TOOL), "--domain", str(input_dir / "graph.yaml"),
         "visualize", "--format", "html", "--output", str(graph_html)],
        check=True, cwd=str(REPO_ROOT),
    )

    source = dict(SOURCE)
    if attribution:
        source["attribution"] = attribution

    return {
        "id": domain_id,
        "name": name,
        "description": description,
        "capstone": capstone or "",
        "default_level": derive_level("linalg"),
        **stats,
        "tags": ["math"],
        "has_navigator": True,
        "has_book": False,
        "books": [],
        "generated_concepts": [],
        "source": source,
    }


def sync_chapter(chapter: int, dry_run: bool) -> dict | None:
    graph_src = PRESS_LINALG_DIR / f"graph_ch{chapter:02d}.yaml"
    chunks_src = PRESS_LINALG_DIR / f"chunks_ch{chapter:02d}.yaml"

    title = f"Chapter {chapter}"
    attribution = None
    if chunks_src.exists():
        chunks = yaml.safe_load(chunks_src.read_text(encoding="utf-8"))
        title = chunks.get("chapter_title") or title
        attribution = chunks.get("source_attribution")

    domain_id = f"linalg_ch{chapter:02d}"
    return _sync_one(
        domain_id=domain_id,
        name=f"Linear Algebra Ch{chapter}: {title}",
        description=f"A First Course in Linear Algebra (Beezer), Chapter {chapter}: {title}.",
        graph_src=graph_src,
        attribution=attribution,
        dry_run=dry_run,
    )


def sync_full(dry_run: bool) -> dict | None:
    graph_src = PRESS_LINALG_DIR / "graph_full.yaml"
    ch1_chunks = PRESS_LINALG_DIR / "chunks_ch01.yaml"
    attribution = None
    if ch1_chunks.exists():
        attribution = yaml.safe_load(ch1_chunks.read_text(encoding="utf-8")).get("source_attribution")

    return _sync_one(
        domain_id="linalg_full",
        name="Linear Algebra: Full Book (Beezer FCLA)",
        description=(
            "A First Course in Linear Algebra (Beezer) -- merged full-book concept "
            "graph across all 8 chapters. See concept-book-press's "
            "docs/projects/linalg/merge_report.md for how cross-chapter node "
            "collisions were resolved."
        ),
        graph_src=graph_src,
        attribution=attribution,
        dry_run=dry_run,
    )


def _parse_chapters(spec: str) -> list[int]:
    out = []
    for part in spec.split(","):
        part = part.strip()
        if "-" in part:
            lo, hi = part.split("-")
            out.extend(range(int(lo), int(hi) + 1))
        elif part:
            out.append(int(part))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--chapters", default="1-8", help="e.g. '1-8' or '1,3,5' (default: 1-8)")
    ap.add_argument("--no-full", action="store_true", help="Skip syncing the merged linalg_full domain")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    chapters = _parse_chapters(args.chapters)

    print(f"Source : {PRESS_LINALG_DIR}")
    print(f"Dest   : {DOMAINS_ROOT}")
    print(f"Chapters: {chapters}{'' if args.no_full else ' + linalg_full'}")
    print()

    catalog = json.loads(CATALOG_PATH.read_text(encoding="utf-8")) if CATALOG_PATH.exists() else []
    by_id = {e["id"]: e for e in catalog}
    added, refreshed = 0, 0

    entries = [sync_chapter(ch, args.dry_run) for ch in chapters]
    if not args.no_full:
        entries.append(sync_full(args.dry_run))

    for entry in entries:
        if entry is None:
            continue
        if entry["id"] in by_id:
            existing = by_id[entry["id"]]
            # Preserve anything book-generation has already populated.
            entry["has_book"] = existing.get("has_book", False)
            entry["books"] = existing.get("books", [])
            entry["generated_concepts"] = existing.get("generated_concepts", [])
            existing.update(entry)
            refreshed += 1
        else:
            catalog.append(entry)
            by_id[entry["id"]] = entry
            added += 1

    if not args.dry_run:
        CATALOG_PATH.write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print()
    print(f"{'(dry run) ' if args.dry_run else ''}catalog: {added} added, {refreshed} refreshed")


if __name__ == "__main__":
    main()
