# cb-linalg

A concept-book app for **Linear Algebra**, derived from the
[concept-book-base](https://github.com/digital-duck/concept-book-base) template.
The domain content — 8 chapter concept graphs plus one merged full-book graph —
was extracted from Robert Beezer's *A First Course in Linear Algebra* (FCLA,
v3.50, GNU Free Documentation License) by
[concept-book-press](../concept-book-press)'s ingest → extract → validate
pipeline. See `concept-book-press/docs/projects/linalg/README.md` for the full
extraction story (per-chapter diffs against a hand-built reference graph,
merge decisions, etc.).

This document covers everything needed to go from a fresh clone of
concept-book-base to actually generating book content for this domain — useful
background if this is your first time standing up a concept-book app from the
template, since a few one-time wiring steps aren't obvious from the base
repo alone.

---

## How the pieces fit together

Three repos are involved, each with a different job:

| Repo | Role |
|---|---|
| `concept-book-press` | Ingests the source textbook (PDF) and extracts concept graphs (`graph_ch01.yaml` … `graph_ch08.yaml`, `graph_full.yaml`) — the "content mining" step. Does not know about concept-book apps at all. |
| `SPL.py` | The content-generation *engine* — `spl3 run build_concept_book.spl` takes a concept graph + a target concept and writes the prose sections, calling an LLM per section. |
| `cb-linalg` (this repo) | The web app: displays the concept graph, and drives SPL.py to generate book HTML on demand or in batch. |

`cb-linalg` never talks to `concept-book-press` or `SPL.py` directly at
request time — it works off local copies:
- `public/domains/{id}/input/graph.yaml` — synced once from concept-book-press.
- `spl/` — a one-time copy of the SPL.py workflow files this app needs
  (`build_concept_book.spl`, `tools.py`, `graph_lib.py`, `style_profiles.py`).
  `scripts/batch_generate.py` and the FastAPI backend both shell out to `spl3`
  pointed at these local files, running with SPL.py's own repo as the process
  `cwd` (so `spl3`'s own Python package imports resolve).

---

## One-time setup

### 1. Prerequisites

```bash
# This app's own frontend deps
npm install

# The spl123 conda env (from SPL.py) provides spl3 and the Claude CLI backend
conda activate spl123
pip install -r requirements-api.txt   # fastapi, click, pyyaml, pydantic-settings, ...
which spl3                             # sanity check — should resolve inside spl123
```

You'll also need local clones of `SPL.py` and `concept-book-press` as siblings
of this repo (i.e. under `~/projects/digital-duck/`) — every script here
defaults to that layout and takes an override flag/env var if yours differs.

### 2. The `spl/` workflow directory

`scripts/batch_generate.py` runs:

```
spl3 run spl/build_concept_book.spl --tools spl/tools.py ...
```

`spl/` is **not** synced automatically — it's a one-time copy of recipe 74
("generic domain concept-book") from SPL.py's cookbook, the same pattern every
concept-book-base derivative uses (see `cb-zinets/spl/` for another example).
This repo's `spl/` has already been populated by copying, verbatim:

```bash
cp ~/projects/digital-duck/SPL.py/cookbook/74_concept_book/build_concept_book.spl \
   ~/projects/digital-duck/SPL.py/cookbook/74_concept_book/tools.py \
   ~/projects/digital-duck/SPL.py/cookbook/74_concept_book/graph_lib.py \
   ~/projects/digital-duck/SPL.py/cookbook/74_concept_book/style_profiles.py \
   spl/
```

Re-run this (from the repo root) only if you intentionally want to pick up
upstream changes to recipe 74 — there's no sync script for this step because
whether to pull in upstream workflow changes is a deliberate per-app decision,
not something to silently automate.

Note: unlike the hand-built domains recipe 74 was originally written for
(`linalg_graph.yaml`, `mechanics_graph.yaml`, etc., which live *inside*
SPL.py's own cookbook directory), the domains synced from concept-book-press
only exist in `public/domains/{id}/input/graph.yaml` here — they're never
copied into SPL.py. `batch_generate.py` was customized to pass that local
file's **absolute path** as the `domain_yaml` parameter (`graph_lib.load_domain()`
accepts absolute paths directly), rather than the bare `{domain_id}_graph.yaml`
filename the base template uses, which only resolves against files hand-copied
into SPL.py's cookbook dir. This generalization is backward compatible — it
works the same for both kinds of domains.

### 3. Sync the Beezer domains from concept-book-press

```bash
python scripts/sync_linalg_from_press.py
```

This copies `concept-book-press/output/linalg/graph_ch01.yaml` …
`graph_ch08.yaml` and `graph_full.yaml` into
`public/domains/linalg_ch01` … `linalg_ch08` and `linalg_full`, renders each
domain's `output/graph.html` navigator, and registers/refreshes catalog
entries in `public/domains/catalog.json` (with `has_book: false` — no prose
generated yet, source attribution set to Beezer/GNU FDL). Options:

```bash
python scripts/sync_linalg_from_press.py --chapters 1-2,4   # subset
python scripts/sync_linalg_from_press.py --no-full          # skip linalg_full
python scripts/sync_linalg_from_press.py --dry-run          # preview only
```

Re-run this any time concept-book-press's extraction is re-run (e.g. a
chapter is re-extracted, or the merge policy in `graph_full.yaml` changes) —
it's safe to re-run; existing `books`/`generated_concepts` catalog data is
preserved on refresh.

---

## Quick start

### Frontend only (browse the concept graphs, no book generation)

```bash
npm run dev          # http://localhost:5174/<base>/
```

You can browse all 9 synced domains' concept graphs immediately after step 3
above — no LLM calls needed for this.

### Full stack (frontend + on-demand book generation via the web UI)

**Terminal 1 — backend:**
```bash
conda activate spl123
bash scripts/start-api.sh
```

**Terminal 2 — frontend:**
```bash
npm run dev
```

Vite proxies `/api` to the backend in dev mode. Use the Settings page to pick
an LLM adapter/model if you don't want the `CB_LLM` default (see
`example.env` — copy to `.env` and edit).

### Batch-generate books from the command line

```bash
conda activate spl123

# Preview what would be generated, without calling any LLM
python scripts/batch_generate.py --dry-run

# Generate the capstone application for every linalg_ch* + linalg_full domain
python scripts/batch_generate.py --n-targets 1

# Just one chapter
python scripts/batch_generate.py --domain linalg_ch02 --n-targets 1

# Skip anything already generated (re-running after adding new chapters)
python scripts/batch_generate.py --skip-existing

# Different LLM / level
python scripts/batch_generate.py --llm claude_cli:claude-opus-4-8 --level college
```

Each domain's `input/graph.yaml`'s `applications` section supplies the
"targets" `batch_generate.py` picks from — see the per-chapter capstone table
below. Generated HTML lands under
`public/domains/{id}/output/{level}.{lang}/{model}/html/`, and
`catalog.json` is updated on success (through `scripts/catalog_lock.py`'s
locked read-modify-write, so this is safe to run alongside the live API
server).

---

## The 9 synced domains

| Domain ID | Chapter | Capstone application |
|---|---|---|
| `linalg_ch01` | Systems of Linear Equations | `linear_programming_application` |
| `linalg_ch02` | Vectors | `gram_schmidt_procedure` |
| `linalg_ch03` | Matrices | `money_best_cities_ranking` |
| `linalg_ch04` | Vector Spaces | *(no application node — theory only)* |
| `linalg_ch05` | Determinants | `determinant_by_row_reduction` |
| `linalg_ch06` | Eigenvalues | `matrix_power_via_diagonalization` |
| `linalg_ch07` | Linear Transformations | `linear_transformations_and_systems_of_equations` |
| `linalg_ch08` | Representations | `orthonormal_basis_normal_matrix` |
| `linalg_full` | Full book (merged) | `determinant_by_row_reduction` |

`linalg_ch04` has no application node, so `batch_generate.py` skips it
automatically (theory-only chapters just won't produce a capstone book;
individual concept pages can still be generated on demand from the UI).

---

## Adding more domains later

1. Extract/update the graph in `concept-book-press` (see its
   `docs/projects/linalg/README.md`).
2. Re-run `python scripts/sync_linalg_from_press.py`.
3. Run `python scripts/batch_generate.py --domain <id>` (or use the web UI).

For a domain from a *different* source entirely (not concept-book-press), see
the base template's generic instructions in `CLAUDE.md` § "Adding a new
domain".

---

## Deployment (GitHub Pages)

```bash
npm run deploy      # vite build && gh-pages -d dist --no-history --dotfiles
                     # then prints "Homepage: https://digital-duck.github.io/cb-linalg/"
```

`npm run deploy` builds the static site and pushes it to the `gh-pages`
branch — an orphan branch (`--no-history`) containing only the compiled
`dist/` output, with no shared commit history with `main`. Never open a PR
from `gh-pages` into `main`; there's no common ancestor, so the diff would
just show your entire source tree replaced by build artifacts.

### One-time repo setting

GitHub Pages must be told to actually serve `gh-pages`, not `main` — this
isn't set by `npm run deploy` itself:

1. Repo → **Settings → Pages**.
2. Under "Build and deployment" → **Source**: "Deploy from a branch".
3. **Branch**: `gh-pages`, folder `/ (root)`. Save.

If this is left on `main` (or never set), the published URL serves `main`'s
raw, unbuilt `index.html` — which references `/src/main.js` directly and
renders blank, since GitHub Pages only serves static files and can't resolve
an unbundled ES module entrypoint. Symptom: the page loads (HTTP 200) but is
blank, and the built JS/CSS bundle paths 404.

`vite.config.js`'s `base` must also match the repo name (`/cb-linalg/`) for
the built asset paths to resolve under `https://digital-duck.github.io/cb-linalg/`
— already set correctly here, but worth checking first if you ever fork this
app under a different repo name.

The backend API and `spl/` workflow are local-only tools, not deployed —
generated book/concept HTML files are committed into `public/domains/` and
baked into the static `dist/` build.

---

## Architecture reference

See `CLAUDE.md` for the full architecture (frontend/backend file map, data
shapes, iframe event protocol, extension points). This README covers only the
domain-specific setup; `CLAUDE.md` is the generic base-template reference.
