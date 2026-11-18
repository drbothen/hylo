---
document_type: behavioral-contract
level: L3
version: "1.2.5"
status: draft
producer: product-owner
timestamp: 2026-11-19T00:20:00Z
phase: 1a
inputs:
  - behavioral-contracts/BC-ALLOCATION.md
  - semport/hylo-legacy/statusline-target-design.md
  - semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts-r4.md
input-hash: "d41d1a7"
traces_to: domain-spec/L2-INDEX.md
origin: greenfield
extracted_from: "n.a. (greenfield helper; reproduces json.dump cache-file bytes; ruling (b) P3r2 §0)"
subsystem: "SS-05"
capability: "CAP-009"
legacy_id: new
parity_class: "n.a."
confidence: "—"
lifecycle_status: active
introduced: "0.1"
modified:
  - "2026-11-18T01:42:00Z (1.2.1) ADV-P3 remediation D10+D12: Dumps scoped to include the subagent stdout json.dumps (SL:924, BC-1.07.004); encoder failure on 4300-digit ints = typed ErrValue and legacy no-write"
  - "2026-11-18T22:00:00Z (1.2.2) ADV-P4 remediation D17 — json.dump encoder depth boundary measured directly (python3 -I, temp dir): succeeds through depth 992, RecursionError from 993 at limit 1000 module scope; law limit−8, slope verified at 700/1000/1300; typed ErrDepth + legacy no-write pinned (PC-6, EC-007/008, CTV)"
  - "2026-11-18T23:30:00Z (1.2.3) ADV-P5 remediation D08+D17+D18 — encoder depth measured PER SITE (law: max total nesting = 993 − W, W = Python frames at the encode call; json.dump and json.dumps alike; slope 1 slot/frame verified W=3..9): session/mix save sites W=4 budget 989, record_cost/git sites W=5 budget 988 (both via render_lane); Dumps takes a depth budget and returns ErrDepth; save_cache anchor corrected to SL:308 invoked from main()'s render stack"
  - "2026-11-19T00:20:00Z (1.2.4) pass-5 sweep C end-to-end re-measurement (isolated temp HOME+cwd, real legacy) — PC-6 law restated: 995 − s (json.dump) / 994 − s (json.dumps), s = Python frames at the encode call inclusive; json.dump accepts one level more than json.dumps at equal stack; budgets session/mix saves 991 (measured flip: stdin rate_limits value 990 saves / 991 skips), record_cost/git 990, composition 991/990; mix/git/cost payloads flat so their encoder limits are unreachable from input; exposure window corrected to 991..992"
  - "2026-11-19T03:45:00Z (1.2.5): ADV-P6 remediation D08 — PC-6 table gains the missing SL:924 row: subagent stdout json.dumps, chain <module>→main_subagent→render_subagent_rows, s = 3, budget 991; measured end to end this burst on real legacy with an isolated temp HOME+cwd and deeply nested task[\"id\"] chains (chain 990 = wire object 991 renders; chain 991 = stdin document 994 exceeds the stdin decoder limit 993 and is swallowed inside main_subagent — empty stdout, exit 0), so the wire budget is exactly attainable from stdin"
deprecated: null
deprecated_by: null
replacement: null
retired: null
removed: null
removal_reason: null
---

# Behavioral Contract BC-5.02.006: pyfmt.Dumps: json.dump cache-file bytes (separators, ensure_ascii, float repr, order)

## Description

`pyfmt.Dumps(v Value, budget int) ([]byte, error)` (json.go, design IM-03) reproduces CPython `json.dump`
defaults byte for byte over an ordered `Value`: separators `", "` and `": "`, ensure_ascii
escaping, `NaN`/`Infinity` tokens, float repr per BC-5.01.005, int-versus-float preserved,
insertion order — for the four cache files (session, mix, git, cost-history) AND the
subagent stdout line (`json.dumps` at SL:924, BC-1.07.004's NDJSON wire; ADV-P3-D10).
Go structs with `encoding/json` are banned for caches: they reorder keys and reformat floats (ruling
(b), P3r2 §0). Helper-level contract per OD-141. `budget` is the per-site recursion budget
(PC-6); exceeding it returns `ErrDepth` (ARCH-06).

## Preconditions

1. `v` is an ordered `Value` loaded per IM-01 (insertion order from the file read earlier;
   mutations preserve positions).
2. Ordered-`Value` semantics (Set/Delete keep positions; WTF-8 strings) per BC-5.02.004.

## Postconditions

1. Output equals CPython `json.dumps(obj)` defaults for every `Value` the cache writers
   produce: member order = `Value` insertion order; `, ` / `: ` separators; strings
   escaped ensure_ascii (non-ASCII → `\uXXXX` plus the standard two-char escapes);
   `NaN`/`Infinity` tokens; floats via Repr (`1794615009.0`, `1e-05`); the int-versus-float
   distinction preserved (BC-SL-102).
2. Shared primitive with `DumpsLen` (IM-04): both emit/count the same bytes, so the
   composition counter and the cache writer cannot drift.
3. The cache writers assemble/mutate the `Value` and emit via Dumps; no `encoding/json`
   marshal path exists for the four caches (D15: no second encoder).
4. Equal to CPython for the generated cache-value table (realistic cache shapes loaded,
   mutated, emitted) under the pinned oracle (OD-104).
5. **Encoder failure** (ADV-P3-D12): an int past the 4,300-digit encoder limit (accumulated
   token sums can reach it; SL:202-203 raises `ValueError` there) returns typed `ErrValue`
   and the calling cache writer performs the legacy no-write — error swallowed, the
   partial temp file leaks exactly as legacy's does (covered by the temp-file exclusion
   class) and the previous cache file is left untouched. `Dumps` never writes a partial
   destination itself (it returns bytes; the writer owns the file).
6. **Depth boundary (measured per site, ADV-P4-D17 as corrected by ADV-P5-D08/D17,
   re-measured end to end pass-5 sweep C).** CPython's encoder consumes ONE recursion
   slot per container nesting level and one slot per Python frame, at every legacy
   encode site. Measured law (`python3 -I`, CPython 3.11.7, isolated temp dir and
   HOME, slope verified over five stacked frames; `s` = Python frames on the stack at
   the encode call, invoking frame inclusive, `<module>` = 1): the maximum encodable
   **total object nesting** is `995 − s` for `json.dump` (cache writes) and `994 − s`
   for `json.dumps` (C encoder) — `json.dump` accepts exactly one level more than
   `json.dumps` at equal stack. **Per-site budgets** (legacy runtime: `<module>→main`
   is `s = 2` before the caller chain):

   | Encode site | Legacy chain | s | Budget |
   |---|---|---|---|
   | `effective_rl` session-cache save | SL:308 | 4 | 991 |
   | `get_sample` session-cache save | SL:351/355 | 4 | 991 |
   | `claude_window_start` session-cache save | SL:288 | 4 | 991 |
   | `_mix_counts` mix-cache save | SL:1150 | 4 | 991 (flat payload — unreachable from input) |
   | `record_cost` cost-history save | SL:237 (via `render_lane`, SL:606) | 5 | 990 (flat payload — unreachable from input) |
   | `git_segment` git-cache save | SL:411 (via `render_lane`, SL:455) | 5 | 990 (flat payload — unreachable from input) |
   | `_mix_counts` `json.dumps` (inner scalar SL:1140; tool_use input SL:1147) | `main→_mix_counts` | 3 | 991 |
   | `_mix_counts` `json.dumps` (tool_result list genexp, SL:1138) | `main→_mix_counts→genexp` | 4 | 990 |
   | subagent stdout `json.dumps` (task-row wire line) | SL:924 (`<module>→main_subagent→render_subagent_rows`) | 3 | 991 (attainable from stdin: the echoed `task["id"]`) |

   Consequently legacy's `save_cache` call in `effective_rl` (SL:308) — reached from
   `main()`'s render stack — can fail with `RecursionError` on a stdin whose `rate_limits`
   decoded fine (the decoder accepts total depth 993 at the stdin site): any saved object
   nested deeper than the site budget is skipped and NOTHING is written: the previous
   cache file is untouched and the partial temp file leaks (temp-file exclusion class).
   hylo reproduces the observable: `Dumps` takes `budget` and, for a `Value` nested deeper
   than `budget`, returns typed `ErrDepth` (sibling of `ErrValue`) instead of bytes, and
   the calling cache writer performs the same legacy no-write; shallower values encode
   regardless of depth. Each call site passes its own pinned constant from the table
   (named constant, D15); the boundary constants are oracle-table-pinned, never magic
   numbers in logic. **Reconciliation with the decoder law (BC-5.02.003 PC-7):** both
   laws spend one slot per frame and one per level; at equal chain depth every cache's
   Save budget EQUALS its Load budget (session/mix 991/991, git/cost 990/990), so
   `Decode(Save(x))` never rejects what `Save` produced, and a shallower stack never has
   the smaller budget (budget is strictly monotone decreasing in frame depth on both
   sides). The exposure is real and legacy-identical, and was measured end to end this
   burst (isolated temp HOME+cwd): a `rate_limits` nested to total value depth 991..992
   decodes fine and skips the write (value 990 — encoded document 991 — is the deepest
   that still saves). **The SL:924 row was measured end to end this burst too
   (ADV-P6-D08, isolated temp HOME+cwd, deeply nested `task["id"]` chains, real legacy
   `--subagent` dispatch):** stdin `{"tasks":[{"id": <chain of d objects>}]}` renders
   the task row while the dumped wire object nests ≤ 991 — chain depth 990 (wire
   object 991, stdin document 993) renders; chain 991 (stdin document 994) exceeds the
   stdin decoder limit 993 (BC-5.02.003), the `RecursionError` is swallowed inside
   `main_subagent` (SL:929-931), and stdout is EMPTY at exit 0 — zero rows, not the
   degraded line. The wire budget 991 at s = 3 is therefore exactly attainable from
   stdin and is the boundary the row pins; a Go port that encoded only 990 levels at
   this site would drop a row legacy renders.

## Invariants

1. Insertion order, including order inherited from `entry = dict(c)` (SL:327) and the
   appended `fetch_ts, up, ts, sample, hist` keys (SL:349, BC-SL-091).
2. No trailing newline; the writer does not add one.

## Edge Cases

| ID | Description | Expected Behavior |
|----|-------------|-------------------|
| EC-001 | `Dumps(decode('{"b":1,"a":2}'))` | `{"b": 1, "a": 2}` (source order) |
| EC-002 | float thresholds survive | `{"a": 1e-05}` for source `{"a":1e-5}` |
| EC-003 | Value holding NaN/±Inf | `{"a": NaN}` / `{"a": Infinity}` tokens |
| EC-004 | int-vs-float preserved: `{"a":1}` vs `{"a":1.0}` | `{"a": 1}` vs `{"a": 1.0}` |
| EC-005 | WTF-8 str member with a lone surrogate | re-escaped `\udXXX` (BC-5.02.003) |
| EC-006 | Nested empty containers | `{"a": {}, "b": []}` |
| EC-007 | `Value` at the helper reference (`s = 1`, module scope), total nesting 993 (994 for `json.dump`) | encodes; bytes equal the CPython oracle (ADV-P4-D17; re-verified 2026-11-18, sweep C: boundary `994 − s` / `995 − s`) |
| EC-008 | `Value` exceeding the site budget (e.g. total nesting 992 at a 4-frame save site, budget 991) | typed `ErrDepth`; cache writer no-write, previous file untouched (temp-file class) |

## Canonical Test Vectors

| Input | Expected Output | Category |
|---|---|---|
| `Dumps(load('{"b":1,"a":2}'), 991)` | bytes `{"b": 1, "a": 2}` | happy-path |
| `Dumps(load('{"a":1.0}'), 991)` | bytes `{"a": 1.0}` | edge-case |
| `Dumps(Value with NaN, 991)` | bytes `{"a": NaN}` | edge-case |
| `Dumps(load('{"a":1e-5}'), 991)` | bytes `{"a": 1e-05}` | edge-case |
| nested object, total nesting 993 at `s = 1` (module-scope helper reference) | encodes; bytes equal the CPython oracle | edge-case |
| nested object, total nesting 992 at a 4-frame site (budget 991) | `ErrDepth`; cache writer performs the legacy no-write | error |

Pinned against CPython 3.11 (OD-104 oracle discipline; realistic cache shapes from the
corpus cases).

## Verification Properties

| VP-NNN | Property | Proof Method |
|--------|----------|-------------|
| VP-024 | Dumps output equals CPython `json.dumps` bytes for every corpus cache shape | CPython oracle table |
| VP-024 | Dumps and DumpsLen agree byte-for-byte on shared shapes | Go property test (testing/quick) |

## Traceability

| Field | Value |
|-------|-------|
| Source | new — OD-141 (helper-level contract), OD-103; design IM-03; pitfalls PR-07/PR-08/PR-19; ruling (b) P3r2 §0 |
| Parity / exclusion | n.a. (byte-exact helper) |
| L2 Capability | CAP-009 (enabler, OD-103) |
| L2 Domain Invariants | DI-012 (byte parity machinery) |
| Architecture Module | `internal/pyfmt` json.go (BC-COMPONENT-MAP: internal/pyfmt/json.go (Dumps) — ARCH-06) |
| Stories | S-TBD (filled by story-writer) |

## Related BCs (Recommended)

- BC-5.02.004 — composes with (ordered-Value semantics)
- BC-5.01.005 — composes with (Repr)
- BC-1.06.001, BC-1.05.009, BC-1.03.002, BC-1.02.013 — consumers (the four cache writers)

## Architecture Anchors (Recommended)

- `architecture/ARCH-06-pyfmt.md#json` — internal/pyfmt/json.go (Dumps) (json.go helpers) (BC-COMPONENT-MAP: ARCH-06 (ARCH-06-pyfmt.md))

## Story Anchor (Recommended)

S-TBD — pyfmt json helpers

## VP Anchors (Recommended)

- VP-024 — cache-byte equality

#### Purity Classification

| Property | Assessment |
|----------|-----------|
| **I/O operations** | none |
| **Global state access** | none |
| **Deterministic** | yes |
| **Thread safety** | safe for concurrent use (stateless functions) |
| **Overall classification** | pure core |

Owning component `py/json.go (Dumps)` (BC-COMPONENT-MAP: py/json.go (Dumps) - ARCH-06); the ARCH-00 package table classifies `internal/pyfmt` pure core - bytes/values in, values out, no I/O, clock never read.
