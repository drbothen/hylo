---
document_type: behavioral-contract
level: L3
version: "1.1.9"
status: draft
producer: product-owner
timestamp: 2026-11-18T08:00:00Z
phase: 1a
inputs: [behavioral-contracts/BC-ALLOCATION.md, domain-spec/L2-INDEX.md, semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts-r2.md, semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts-r8.md]
input-hash: "8e07087"
traces_to: domain-spec/L2-INDEX.md
origin: brownfield
extracted_from: "legacy/dgx_statusline.py:render_subagent_rows (SL:888-936)"
subsystem: "SS-01"
capability: "CAP-009"
legacy_id: BC-SL-097
parity_class: byte-exact
confidence: H
priority: P0
lifecycle_status: active
introduced: "0.1"
modified:
  - "1.1.1 2026-11-18T03:00:00Z: VP citation reconciliation: no-VP-yet row replaced with VP-010 golden leg (arbitrary-array differential remains open)"
  - "1.1.2 2026-11-18T07:00:00Z: adv-p3 remediation: every golden wire string re-derived from legacy and pasted ensure_ascii-escaped (ADV-P3-C01); id echo generalized to any JSON value (ADV-P3-C14); stray comma removed (ADV-P3-C22); joiner hex corrected to U+00B7"
  - "1.1.3 2026-11-18T08:00:00Z: pass-4 remediation: joiner sourced from statusline.subagent.joiner (ADV-P4-C04); parse/emit notes re-anchored to pyfmt.Decode + ordered pyfmt.Value, never encoding-json (ADV-P4-C03)"
  - "1.1.4 2026-11-18T23:00:00Z: pass-5 remediation (ADV-P5-C13) — killed row relabelled: explicit statusline.subagent.glyphs.killed map entry, not the glyph fallback (SL:845-846 vs SL:894)"
  - "1.1.5 2026-11-18T23:45:00Z: pass-6 remediation (ADV-P6-C04/C05) — PC4 rewrote the id echo as the decoded value re-serialized by pyfmt Dumps (raw tokens do not survive; float-id vector added; SL:924 dump runs under the measured per-site budget, see BC-5.02.006); PC3 corrected: ASCII controls, \" and \\ are escaped, the ESC inside an SGR sequence included"
  - "1.1.6 2026-11-18T23:45:00Z: pass-6 remediation (ADV-P6-C12) — frontmatter template conformance: priority P0 added (prd.md S1.07), introduced normalized to the sibling \"0.1\" format"
  - "1.1.7 2026-11-19T20:00:00Z: pass-7 remediation (ADV-P7-C02/C14, OD-190) — PC3 escape list completed with the CPython short escapes \\b and \\f (orchestrator-verified json.dumps emissions; ADV-P7-C02); vector-row prose pseudo-escape replaced with the em dash (ADV-P7-C14); PC5 states OD-190 LF-on-every-OS with the Windows oracle normalization declared beside PYTHONIOENCODING=utf-8"
  - "1.1.8 2026-11-20T12:30:00Z: pass-8 residual sweep (OD-192) — ASSUMP-107-1 capture deadline respelled: before Phase 2 writes the S1.07 stories, not before Phase 3"
  - "1.1.9 2026-11-20T18:00:00Z: pass-9 remediation (ADV-P9-C06) — the string-token vector's raw token restored to the \u0041 JSON escape so the input token and its output differ (the decoded input and output were identical, a vacuous pair); PC4 example respelled to match; oracle-checked"
deprecated: null
deprecated_by: null
replacement: null
retired: null
removed: null
removal_reason: null
---

# Behavioral Contract BC-1.07.004: One default-JSON line per eligible task; zero bytes for zero rows

## Description

`render_subagent_rows` filters the `tasks` array to dict tasks carrying an `id` and emits exactly one
`json.dumps` object per survivor: `{"id": "<task id>", "content": "<rendered row>"}` with CPython
default separators (`, ` and `: `) and `ensure_ascii=True` — one LF-terminated line per row in input
order. Bits inside `content` are joined with the three-character selector space + U+00B7 + space
(source-level UTF-8 `20 c2 b7 20`; on the wire json.dumps emits `\u00b7` — PC7; no SGR on the
separator). Zero survivors produce zero output (no newline). The whole render completes
before a single print, so a render fault never leaves partial rows on stdout.

## Preconditions

1. ASSUMPTION (ASSUMP-107-1): the Claude Code 2.1.326 `subagentStatusLine` stdin payload is assumed
   compatible with the 2.1.322 contract legacy parsed; to be verified by a capture before Phase 2 writes the S1.07 stories (OD-192).
2. stdin parsed per BC-1.07.003; tasks iterable (else BC-1.07.008).

## Postconditions

1. Every task that is a `dict` and has key `id` yields exactly one output line; order preserved.
2. Non-dict tasks and dict tasks without `id` yield no line (not even blank).
3. Each line is `json.dumps({"id": task["id"], "content": bits_joined})` with defaults: property
   order id-then-content, `, `/`: ` separators, `ensure_ascii=True` — every non-ASCII character goes
   on the wire as a `\uXXXX` escape (ESC→`\u001b`, U+00BB→`\u00bb`, U+00B7→`\u00b7`,
   U+25E8→`\u25e8`, U+2714→`\u2714`, U+2718→`\u2718`, U+00E9→`\u00e9`, lone surrogate→`\ud800`);
   ASCII **printable** characters pass through unescaped; ASCII **control** characters are escaped
   (ESC — including the ESC that opens an SGR sequence — as `\u001b`, plus short escapes `\b`, `\f`,
   `\n`, `\t`, `\r` and `\uXXXX` for the rest, e.g. BEL→`\u0007`; ADV-P7-C02: CPython's `ensure_ascii`
   encoder emits `\b` (0x08) and `\f` (0x0C) as short escapes, so a name holding a backspace or form
   feed goes on the wire as `\b`/`\f`, never `\u0008`/`\u000c`), as are `\"` and `\\`
   (ADV-P6-C05: an SGR sequence is NOT exempt — its ESC and any inner quotes/backslashes are escaped
   like any other character).
4. The `id` is the **decoded value re-serialized by `pyfmt` `Dumps`** (ADV-P6-C04; SL:924
   decodes stdin and re-dumps — not a byte-for-byte token copy): any JSON value (string, number, bool,
   null, array, object; the array case is verified in the vectors below) is dumped from its decoded
   form, so raw-token spellings do not survive — `1.50`→`1.5`, `1E2`→`100.0`, `"\u0041"`→`"A"`,
   duplicate object keys collapse (last-wins kept — oracle-verified 2026-11-18,
   `/opt/homebrew/anaconda3/bin/python3 -I` 3.11.7); it is not coerced to string before dumping. The
   dump runs under the per-site encoder recursion budget measured for the SL:924 site — measured
   budget, see BC-5.02.006.
5. Lines are LF-terminated on every OS (OD-190: UTF-8 + LF everywhere; the Windows parity oracle's
   CRLF-to-LF normalization is declared beside its `PYTHONIOENCODING=utf-8` variable, not hidden in
   the shim); the last line carries the terminating LF (print semantics).
6. Zero eligible tasks: zero bytes, exit 0.
7. Between content bits the joiner is the configured `statusline.subagent.joiner` (D15; Text key
   registered in the BC-2.01.004 registry, free text with no control bytes, BC-2.01.003 PC-3), whose
   default is, at source level, the three characters space + U+00B7 + space
   (UTF-8 `20 c2 b7 20`; U+00B7, NOT U+2027); on the json.dumps wire the default renders as the 8
   ASCII bytes `20 5c 75 30 30 62 37 20` (that is, `" \u00b7 "`). No SGR codes wrap it.

## Invariants

1. One print per process, after the full render: no partial-row output precedes a fault (feeds
   BC-1.07.008's no-partial pin).
2. Output is pure ASCII on the wire (ensure_ascii) — immune to locale/encoding on every OS.
3. Row count equals eligible-task count; input order is preserved.

## Edge Cases

| ID | Description | Expected Behavior |
|----|-------------|-------------------|
| EC-001 | `tasks` is a dict | Iterates keys; non-dict items → no rows (zero bytes) |
| EC-002 | `tasks` is a string | Iterates characters; non-dict items → no rows (zero bytes) |
| EC-003 | Mixed batch: `{"name":"noid"}, {"id":"ok","status":"killed"}, "str"` | One line for `ok` only, in position |
| EC-004 | `id` non-string (number) | Echoed as JSON number in the id field |
| EC-005 | Lone surrogate in a name | Escaped by json.dumps (`a\ud800b`); no UnicodeEncodeError — no CP-S17 analogue (P3r2 §A7) |
| EC-006 | Duplicate ids in two tasks | Two lines; CC's contract owns dedup, not the renderer |
| EC-007 | Stdin carries a `columns` field | Ignored: subagent rows are never trimmed to width (no `trim_to_fit` in this mode) |

## Canonical Test Vectors

| Input | Expected Output | Category |
|-------|----------------|----------|
| `{"tasks":[{"id":"a1","name":"explore","status":"running","model":"claude-sonnet-5-5","tokenCount":12345,"startTime":<now-125000>}]}`, `model_prefixes = [claude-sonnet]` | `{"id": "a1", "content": "\u001b[33m\u00bb explore\u001b[0m \u00b7 \u001b[36m\u25e8DGX\u001b[0m \u001b[90mclaude-sonnet-5-5\u001b[0m \u00b7 \u001b[36m12.3k tok\u001b[0m \u00b7 \u001b[90m02:05\u001b[0m"}` +LF, exit 0 | happy-path |
| `{"tasks":[{"name":"noid"},{"id":"ok","status":"killed"},"str"]}` | one line, id `ok`: `{"id": "ok", "content": "\u001b[90m\u25cd ?\u001b[0m \u00b7 \u001b[90mkilled\u001b[0m"}`, exit 0 (explicit killed glyph from `statusline.subagent.glyphs.killed` U+25CD grey, SL:845-846 — a map key, **not** the fallback; the fallback for unknown/missing statuses is the independent key `statusline.subagent.glyphs.unknown`, BC-1.07.005 PC1; settled suffix) | edge-case |
| `{"tasks":[]}` | zero bytes, exit 0 | happy-path |
| `{"tasks":[{"id":"a9","name":"a\ud800b","status":"completed"}]}` | one line: `{"id": "a9", "content": "\u001b[32m\u2714 a\ud800b\u001b[0m \u00b7 \u001b[90mcompleted\u001b[0m"}`, exit 0 | edge-case |
| `{"tasks":[{"id":["x"],"name":"n","status":"completed"}]}` | one line: `{"id": ["x"], "content": "\u001b[32m\u2714 n\u001b[0m \u00b7 \u001b[90mcompleted\u001b[0m"}` (id array echoed from its decoded value), exit 0 | edge-case |
| `{"tasks":[{"id": 1.50, "name":"n","status":"completed"}]}` and `{"tasks":[{"id": 1E2, "name":"n","status":"completed"}]}` and `{"tasks":[{"id": "\u0041", "name":"n","status":"completed"}]}` (ADV-P9-C06: the raw stdin token is the 7-byte JSON escape spelling, so the input token and its re-serialized output differ; oracle pass-9 2026-11-18) | one line each: `{"id": 1.5, ...}`, `{"id": 100.0, ...}`, `{"id": "A", ...}` — decoded value re-serialized, not the raw token (oracle-verified 2026-11-18; pass-9 re-run: stdin "\u0041" echoes as "A") | edge-case |

Verified 2026-11-18 against CPython 3.11.7 (`python3 -I`, legacy module imported and exercised; goldens
re-derived escaped after the adv-p3 C01 escape-decoding incident): rows 1, 2, 4, 5 byte-reproduced;
default `json.dumps` separators confirmed (`{"id": "a1", "content": ...}`); every non-ASCII wire
character pasted above as its literal `\uXXXX` escape.

## Verification Properties

| VP-NNN | Property | Proof Method |
|--------|----------|-------------|
| VP-010 | Python-written NDJSON goldens match byte-for-byte: one `{"id": ..., "content": ...}` line per eligible task, CPython default separators, ensure_ascii=True, U+00B7 selector (`\u00b7` on the wire), zero-survivors-produce-zero-bytes | Tier B golden comparison (Python oracle writes; Go matches) |

## Traceability

| Field | Value |
|-------|-------|
| L2 Capability | CAP-009 |
| L2 Domain Invariants | DI-008 (exit 0), DI-012 (ASCII wire format kept, no deviation) |
| Architecture Module | `internal/statusline` (row framing) — JSON encoder should reuse `internal/pyfmt` semantics (VP-024 family) |
| Stories | TBD (filled by story-writer) |
| Source | legacy/dgx_statusline.py:`render_subagent_rows` (SL:888-936; joiner SL:924; print-at-end SL:934-935) |
| Legacy contract | BC-SL-097 (P3r2 §A7; helper home r8) |
| Decisions | OD-155, D4 (byte parity) |

## Related BCs (Recommended)

- BC-1.07.003 — composes with (parses stdin)
- BC-1.07.005 — composes with (glyph/name bits)
- BC-1.07.006, BC-1.07.007 — composes with (remaining segments)
- BC-1.07.008 — related to (no-partial-output pin)

## Architecture Anchors (Recommended)

- `architecture/ARCH-03-statusline.md` — subagent output framing; buffer-then-single-write
  (design IM-15/IM-22 analogy)

## Story Anchor (Recommended)

TBD — filled by story-writer

## VP Anchors (Recommended)

- VP-010 (Python-written NDJSON goldens: framing, separators, ensure_ascii, zero-survivor case)

---

### Brownfield-Specific Sections

#### Source Evidence

| Property | Value |
|----------|-------|
| **Path** | `legacy/dgx_statusline.py` (SL:888-936) |
| **Confidence** | high (module exercised under CPython 3.11.7, 2026-11-18) |
| **Extraction Date** | 2026-11-18 |

#### Evidence Types Used

- **assertion**: pinned runs reproducing r2 §A7's pinned vector plus skip/surrogate/empty cases
- **guard clause**: `if not isinstance(task, dict) or "id" not in task: continue` (SL:890-891)

#### Purity Classification

| Property | Assessment |
|----------|-----------|
| **I/O operations** | none in the filter/dump path (stdout write in main_subagent) |
| **Global state access** | none in hylo — prefix list comes from internal/config; legacy read `os.environ` inside the model segment (BC-1.07.006) |
| **Deterministic** | yes (given config + wall clock for the running clock) |
| **Thread safety** | safe for concurrent use (no shared mutable state) |
| **Overall classification** | pure function of (parsed stdin, config, wall clock) |

#### Refactoring Notes

Go: parse with `pyfmt.Decode(b, ModeText)` (BC-1.01.002, BC-5.02.003) in the shell, then iterate the
ordered `pyfmt.Value` model (BC-5.02.004): eligibility and the `id` echo via `Value.Kind`/`Get`/`Dumps`
(objects stay insertion-ordered; ids survive verbatim, any JSON value). Emit via a bytes.Buffer
flushed once. The joiner comes from resolved config (`statusline.subagent.joiner`, default
`" · "`; ADV-P4-C04). JSON escaping must match CPython `ensure_ascii` byte-for-byte — route
through `internal/pyfmt`'s encoder (VP-024 family); never `encoding/json` (rejects NaN/Infinity; maps
reorder object-id keys; float64 big ints break PC4's verbatim echo; `\ud800` becomes U+FFFD
contradicting EC-005; no CPython depth budget).
