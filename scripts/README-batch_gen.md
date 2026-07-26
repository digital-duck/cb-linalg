# ConceptBook Generation Guide (cb-linalg)

This repo generates concept books for **one domain family**: Robert Beezer's
*A First Course in Linear Algebra*, split into 8 chapters plus a merged
full-book graph. Domain IDs in `public/domains/catalog.json`:

```
linalg_ch01   Systems of Linear Equations
linalg_ch02   Vectors
linalg_ch03   Matrices
linalg_ch04   Vector Spaces        (no application node yet -> no book target)
linalg_ch05   Determinants
linalg_ch06   Eigenvalues
linalg_ch07   Linear Transformations
linalg_ch08   Representations
linalg_full   Full Book (merged across all 8 chapters)
```

`linalg_full` is what most people mean by "the linalg concept book" — it's the
merged graph across all 8 chapters, currently generated in English with two
targets (`fibonacci_closed_form`, `determinant_by_row_reduction`).

## Prerequisites

```bash
conda activate spl123
cd ~/projects/digital-duck/cb-linalg/
```

The backend API must be running for the UI Generate/PDF buttons:
```bash
bash scripts/start-api.sh   # uvicorn on :8200
npm run dev                 # Vite on :5174 (separate terminal)
```

---

## Scripts

### `scripts/test_gen.sh` — interactive / per-domain runs

```bash
bash scripts/test_gen.sh                    # all domains
bash scripts/test_gen.sh linalg_full        # one domain
bash scripts/test_gen.sh linalg_ch01 linalg_ch02
```

Key flags inside the script (edit before running):
| Line | Flag | Effect |
|------|------|--------|
| `--skip-cache` | force fresh LLM calls | use when re-generating with new prompts or a new model |
| `--skip-existing` | skip targets already in catalog *for this (target, model, language)* | use for incremental runs |

Logs are written to `logs/batch_gen_YYYYMMDD_HHMMSS.log`.

### `scripts/batch_generate.py` — CLI with full options

```bash
python scripts/batch_generate.py [OPTIONS]
```

| Option | Default | Description |
|--------|---------|--------------|
| `--domain` | all | Domain ID (repeatable: `--domain linalg_ch01 --domain linalg_ch02`) |
| `--n-targets` | 2 | Number of application nodes per domain |
| `--level` | domain default (`college`) | Override level: `intro / core / college / research` |
| `--language` | `en` | Output language ISO code (`en`, `zh`, `fr`, …) — friendly names also accepted (`chinese`, `french`) |
| `--llm` | `claude_cli:claude-sonnet-4-6` | LLM backend (env: `CB_LLM`) |
| `--spl-dir` | `~/projects/digital-duck/SPL.py` | SPL.py root (env: `CB_SPL_DIR`) |
| `--skip-cache` | off | Bypass spl3 LLM cache — force fresh generation |
| `--skip-existing` / `--no-skip-existing` | **on** | Skip a target already in `catalog.json` for this exact `(target, model, language)` combination |
| `--dry-run` | off | Print planned jobs without running |
| `--stop-on-error` | off | Abort batch on first failure |

**`--skip-existing` is language-aware as of 2026-07-26.** Earlier versions of
this script keyed the "already generated" check on `(target, model)` only,
ignoring `language` — so requesting `--language zh` on a domain already
generated in English would silently report `[skip] ... already in catalog`
and generate nothing, even though no Chinese output existed anywhere. Fixed in
`_already_generated()` / `_mark_generated()` to include `language` in both the
skip check and the `books`/`generated_concepts` catalog entries. If you pull
an older `cb-linalg` clone or a copy of this script from the sibling
`concept-book` repo, check for this before trusting a `[skip]` message across
languages.

### `scripts/sync_linalg_from_press.py` — pull graphs from concept-book-press

Regenerates `linalg_ch01`–`ch08` and `linalg_full`'s `input/graph.yaml` from
the upstream `concept-book-press` extraction pipeline (Beezer's FCLA source).
Run this before a full-book batch if the source graphs changed:
```bash
python scripts/sync_linalg_from_press.py                # all 8 chapters + merge
python scripts/sync_linalg_from_press.py --chapters 1-2,4
python scripts/sync_linalg_from_press.py --no-full       # skip the linalg_full merge
python scripts/sync_linalg_from_press.py --dry-run
```

---

## Generating in Chinese (zh)

`linalg_full` and all 8 chapters currently exist in English only. To add a
Chinese pass on top of the existing English books (does not touch or remove
the English output):

```bash
conda activate spl123
cd ~/projects/digital-duck/cb-linalg/

# Test first: one domain, first run for this language needs --skip-cache
python scripts/batch_generate.py --domain linalg_full --language zh --skip-cache --dry-run
python scripts/batch_generate.py --domain linalg_full --language zh --skip-cache

# Then the rest of the chapters
python scripts/batch_generate.py \
    --domain linalg_ch01 --domain linalg_ch02 --domain linalg_ch03 \
    --domain linalg_ch05 --domain linalg_ch06 --domain linalg_ch07 --domain linalg_ch08 \
    --language zh --skip-cache
```

(`linalg_ch04` has no application node in its graph yet, so it has no book
target in any language — `batch_generate.py` will print `[skip]
linalg_ch04: no application nodes in graph.yaml` and move on.)

Output lands in a separate directory per language, alongside the English:
```
public/domains/linalg_full/output/college.en/sonnet/html/
public/domains/linalg_full/output/college.zh/sonnet/html/
```

Re-running the same command later (e.g. to pick up a prompt change) should
omit `--skip-cache` so cached concepts are reused and only new/changed ones
regenerate — see **Cache behaviour** below.

---

## Cache behaviour

The spl3 content cache key is `(concept, language, llm)`.

- Same concept in **different languages** → separate cache entries (independent)
- Same concept with **different LLM** → separate cache entries (good for quality comparison)
- Re-running without `--skip-cache` reuses the cached version → fast (0 LLM calls)
- Re-running with `--skip-cache` regenerates everything fresh → slow but picks up prompt changes

**Rule of thumb:**
- First run for a new domain/language/model → always add `--skip-cache`
- Subsequent runs to fill missing concepts → omit `--skip-cache` (reuse hits, generate misses)

---

## Comparing LLM quality

```bash
# Generate with Sonnet (default)
python scripts/batch_generate.py --domain linalg_full --skip-cache

# Generate same domain with Haiku for comparison
python scripts/batch_generate.py --domain linalg_full --skip-cache \
    --llm claude_cli:claude-haiku-4-5-20251001
```

Both outputs are cached independently (keyed by `llm`, not overwritten). Compare the HTML files in:
```
public/domains/linalg_full/output/college.en/sonnet/html/
public/domains/linalg_full/output/college.en/haiku/html/
```

---

## Output locations

| Artifact | Path |
|----------|------|
| Concept book HTML (TOC index) | `public/domains/{id}/output/{level}.{lang}/{model}/html/book_{target}.html` |
| Individual concept HTML | `public/domains/{id}/output/{level}.{lang}/{model}/html/concept_{name}.html` |
| PDF | `public/domains/{id}/output/{level}.{lang}/{model}/pdf/book_{target}.pdf` |
| Concept graph | `public/domains/{id}/output/graph.html` |
| Generation logs | `logs/batch_gen_YYYYMMDD_HHMMSS.log` |
| SPL run logs | `~/.spl/logs/build_concept_book-*.md` |

---

## Regenerating graph.html (after color/structure changes)

```bash
bash scripts/sync_from_spl.sh
```

This copies `*_graph.yaml` from SPL.py and regenerates all `graph.html` files.
Then hard-refresh the browser (`Ctrl+Shift+R`).

---

## Completed runs

### linalg_ch01–ch08 + linalg_full, English (sonnet, college)
All chapters except `linalg_ch04` (no application node) have at least one
English book generated; `linalg_full` has two (`fibonacci_closed_form`,
`determinant_by_row_reduction`).

### linalg_ch01–ch08 (excl. ch04), Chinese (zh) — done (2026-07-25)
```bash
python scripts/batch_generate.py \
    --domain linalg_ch01 --domain linalg_ch02 --domain linalg_ch03 --domain linalg_ch04 \
    --domain linalg_ch05 --domain linalg_ch06 --domain linalg_ch07 --domain linalg_ch08 \
    --language zh --skip-cache
```
Batch complete: 9 succeeded, 0 failed (ch04 auto-skipped, no application node).
Deliberately excludes `linalg_full` — the merged full-book graph still needs
verification before generating a Chinese pass on top of it.

### linalg_full, Chinese (zh) — pending
Blocked on verifying the merged graph first (see above). Once verified, use
the `linalg_full` command in **Generating in Chinese (zh)** above.
