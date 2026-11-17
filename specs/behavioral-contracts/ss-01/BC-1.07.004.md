---
document_type: behavioral-contract
level: L3
version: "1.1.1"
status: draft
producer: product-owner
timestamp: 2026-11-18T03:00:00Z
phase: 1a
inputs: [behavioral-contracts/BC-ALLOCATION.md, domain-spec/L2-INDEX.md, semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts-r2.md, semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts-r8.md]
input-hash: "9e0be15"
traces_to: domain-spec/L2-INDEX.md
origin: brownfield
extracted_from: "legacy/dgx_statusline.py:render_subagent_rows (SL:888-936)"
subsystem: "SS-01"
capability: "CAP-009"
legacy_id: BC-SL-097
parity_class: byte-exact
confidence: H
lifecycle_status: active
introduced: v0.2.2
modified: ["1.1.1 2026-11-18T03:00:00Z: VP citation reconciliation: no-VP-yet row replaced with VP-010 golden leg (arbitrary-array differential remains open)"]
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
`json.dumps` object per survivor — `{"id": "<task id>", "content": "<rendered row>"}` with CPython
default separators (`, ` and `: `) and `ensure_ascii=True` — one LF-terminated line per row in input
order. Bits inside `content` are joined with the raw three-byte selector ` · ` (space, U+00B7, space;
no SGR on the separator). Zero survivors produce zero output (no newline). The whole render completes
before a single print, so a render fault never leaves partial rows on stdout.

## Preconditions

1. ASSUMPTION (ASSUMP-107-1): the Claude Code 2.1.326 `subagentStatusLine` stdin payload is assumed
   compatible with the 2.1.322 contract legacy parsed; to be verified by a capture before Phase 3.
2. stdin parsed per BC-1.07.003; tasks iterable (else BC-1.07.008).

## Postconditions

1. Every task that is a `dict` and has key `id` yields exactly one output line; order preserved.
2. Non-dict tasks and dict tasks without `id` yield no line (not even blank).
3. Each line is `json.dumps({"id": task["id"], "content": bits_joined}, )` with defaults: property
   order id-then-content, `, `/`: ` separators, `ensure_ascii=True` escaping (ESC→`\u001b`, »→`»`,
   ·→`·`, ◨→`◨`, ✔→`✔`, é→`é`, lone surrogate→`\ud800`).
4. The `id` is echoed verbatim (any JSON scalar type); it is not coerced to string before dumping.
5. Lines are LF-terminated; the last line carries the terminating LF (print semantics).
6. Zero eligible tasks: zero bytes, exit 0.
7. The " · " joiner is the raw UTF-8 sequence `20 e2 80 a7 20`; no SGR codes wrap it.

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
| `{"tasks":[{"id":"a1","name":"explore","status":"running","model":"claude-sonnet-5-5","tokenCount":12345,"startTime":<now-125000>}]}`, `model_prefixes = [claude-sonnet]` | `{"id": "a1", "content": "\u001b[33m» explore\u001b[0m · \u001b[36m◨DGX\u001b[0m \u001b[90mclaude-sonnet-5-5\u001b[0m · \u001b[36m12.3k tok\u001b[0m · \u001b[90m02:05\u001b[0m"}` +LF, exit 0 | happy-path |
| `{"tasks":[{"name":"noid"},{"id":"ok","status":"killed"},"str"]}` | one line, id `ok`, glyph ◍ grey, trail `killed` | edge-case |
| `{"tasks":[]}` | zero bytes, exit 0 | happy-path |
| `{"tasks":[{"id":"a9","name":"a\ud800b","status":"completed"}]}` | id `a9` line with `a\ud800b` escaped in content, exit 0 | edge-case |

Verified 2026-11-18 against CPython 3.11.7 (`python3 -I`, legacy module imported and exercised): rows
1, 2, 4 byte-reproduced; default `json.dumps` separators confirmed (`{"id": "a1", "content": ...}`).

## Verification Properties

| VP-NNN | Property | Proof Method |
|--------|----------|-------------|
| VP-010 | Python-written NDJSON goldens match byte-for-byte: one `{"id": ..., "content": ...}` line per eligible task, CPython default separators, ensure_ascii=True, raw ` · ` selector, zero-survivors-produce-zero-bytes | Tier B golden comparison (Python oracle writes; Go matches) |

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

Go: `for _, task := range tasks { if m, ok := task.(map[string]any); ok { if id, has := m["id"]; has {
... } } }`; emit via a bytes.Buffer flushed once. JSON escaping must match CPython `ensure_ascii`
byte-for-byte — prefer routing through `internal/pyfmt`'s encoder so VP-024's equivalence carries.
