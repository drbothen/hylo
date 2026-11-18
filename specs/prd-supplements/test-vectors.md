---
document_type: test-vectors
level: L3
version: "1.5"
status: draft
producer: product-owner
timestamp: 2026-11-18T18:30:00Z
phase: 1a
stage: "3 of 3 (integration)"
inputs: [prd.md]
input-hash: "0149ffc"
traces_to: prd.md
---

# Test Vectors: hylo P1 canonical golden tables

> PRD supplement — extracted from PRD Section 5b.
> Referenced by: test-writer, holdout-evaluator.
> Each canonical table is specified in full inside its owning contract (verified against
> the CPython 3.11.7 oracle on 2026-11-15 by the stage-2 writers). This supplement indexes
> them; it does not duplicate the bytes.

| Canonical table | Size | Owning BC | Provenance |
|---|---|---|---|
| 29-byte degraded line (exact bytes + exit 0) | 1 vector | BC-1.01.001 | oracle run 2026-11-15 |
| COLUMNS grammar table (unset, 0, 71/72 boundary, negatives incl. -0, unicode digits, underscores, 4,300/4,301-digit) | ~20 rows | BC-1.01.005 (consumes BC-5.01.002) | oracle run (term_cols) |
| ROWS x COLUMNS trim-breakpoint matrix (rows 1-3 across unset/0/71/72/-5/-0/10) | matrix | BC-1.01.010, BC-1.01.003 | oracle run; widths re-derived per segment |
| 45-byte default line; stdin nesting budget (993/994) | vectors | BC-1.01.002 | oracle run |
| Turn-machine exhaustive table (20 rows incl. added T13) | 20 rows | BC-1.03.016 | pass-3 r2 §A4 (19 rows) + 1 pinned addition |
| D4-EX-2 wrong-shape table (exact expected caches) | 21 rows | BC-1.03.019 | pass-3 r3 §3.1 |
| json.dumps length oracle | 63 cases (row 53 script-generated, OD-142) | BC-5.02.002, BC-5.02.001 | design §8; P3r2 §A5; regenerated 2026-11-15 |
| json.loads(bytes) acceptance set (BOM/UTF-16/32, surrogates, depth, NaN, duplicates) | vector set | BC-5.02.003 | oracle run 2026-11-15 |
| get_sample pinned sequence + exact cache JSON | 11 steps | BC-1.04.020 | oracle run |
| Cost colouring goldens (seeded sessions) | 21 sessions (12 s + 8 g + sess-self), 12 outputs, 5 scenarios | BC-1.05.008 | oracle run 2026-11-15; recount per pass-4 A09/C2-04 |
| heat() HSV cell colours | cell table | BC-1.02.019 | oracle run |
| Freshness ladder thresholds + stale suffix | ladder table | BC-1.04.004 | oracle run |
| Row goldens A/B/C (committed Tier B strings, per-OS variants) | 3 goldens | BC-6.03.001 | P3r2 strings; totals recomputed |
| CPython-generated pyfmt expectation tables (Round/RoundN/F, ParseInt/ParseFloat, divmod/mod, Strip sets, FromISOFormat) | generated per helper | BC-5.01.001..003, BC-5.03.001..004, BC-5.04.001 | committed generator output (design §2.6) |
| `-0.0` spellings (cache-hit segment, thermometer) | 2 vectors | BC-1.02.023, BC-1.02.020 | oracle run (writer-added pins) |
| D4-EX-3 class vectors (one per key class + reason strings) | 1+ per class | BC-2.02.001..006, BC-2.01.003/.005 | spec-pinned (OD-114) |
| Number-range extremes: int64-overflow and Duration-ceiling rows (OD-164) | 1+ per keyed site | BC-2.02.002 | spec-pinned (OD-164) |
| Per-OS file-read encoding vectors — every file read as UTF-8 on all OSes; locale-decode differences ride exclusion id `OD-159` | vector set | transcript/cache BCs (BC-1.03.x, BC-1.06.x), BC-5.02.003 | spec-pinned (OD-159) |
| OD-156 numeric-overflow vectors (CP-O01..O05, CP-O10/O11 stdin/metrics/cache-borne at render → 29-byte line; CP-O06..O08 transcript-borne → skip line, CP-O09 → legacy no-write save; CP-A04/A05 subagent conversions → 29-byte line; CP-N03 metrics-borne, SL:717) | 1+ per trigger — including an overflow (≥ 2**1024 − 2**970) row in each owning BC's table: pass-4 B04 restores the missing rows in BC-1.02.006/.011/.012/.014/.017/.020/.025 and names the CP-O id in the corresponding EC registers | BC-1.02.006/.011/.012/.014/.017/.020/.025, BC-1.03.005/.006/.007/.010/.016/.018, BC-1.04.001/.004/.005 (CP-N03 owners), BC-1.05.007, BC-1.05.002 (CP-O11 co-owner), BC-1.06.001, BC-1.07.007 | spec-pinned (OD-156; register in error-taxonomy.md) |
| `--subagent` / custom agent-panel row vectors (config off switch; legacy BC-SL-097 surface) | vector set | BC-1.07.001..008, BC-4.01.002 | spec-pinned (OD-155) |

Escape convention: in vector cells, `\uXXXX` escapes (e.g. `\u200B`, `\u00A0`) denote that
code point visibly; `\xNN` denotes a byte; `\e` is 0x1B. No table contains a literal
invisible character (scanned at stage 3).
