---
document_type: behavioral-contract
level: L3
version: "1.0.5"
status: draft
producer: product-owner
timestamp: 2026-11-18T08:00:00Z
phase: 1a
inputs: [behavioral-contracts/BC-ALLOCATION.md, domain-spec/L2-INDEX.md, semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts-r2.md, semport/hylo-legacy/statusline-target-design.md]
input-hash: "96cf453"
traces_to: domain-spec/L2-INDEX.md
origin: brownfield
extracted_from: "legacy/dgx_statusline.py:main_subagent (SL:928-936)"
subsystem: "SS-01"
capability: "CAP-009"
legacy_id: BC-SL-097
parity_class: byte-exact
confidence: H
priority: P0
lifecycle_status: active
introduced: "0.1"
modified: ["1.0.1 2026-11-18T03:00:00Z: VP citation reconciliation: no-VP-yet row replaced with VP-005", "1.0.2 2026-11-18T07:00:00Z: adv-p3 remediation: non-English term replaced with 'short-circuit' (ADV-P3-C22)", "1.0.3 2026-11-18T08:00:00Z: pass-4 remediation: parse notes re-anchored to pyfmt.Decode(ModeText), never encoding-json, with the four decoder-divergence reasons (ADV-P4-C03); non-UTF-8 leg tied to the BC-1.01.008 locale pin and BOM case added (ADV-P4-C14)", "1.0.4 2026-11-18T23:00:00Z: pass-5 remediation (ADV-P5-C15) — VP-006 citation added (row and anchor): reciprocal with VP-006 bcs listing", "1.0.5 2026-11-18T23:45:00Z: pass-6 remediation (ADV-P6-C12) — frontmatter template conformance: priority P0 added (prd.md S1.07), introduced normalized to the sibling \"0.1\" format"]
deprecated: null
deprecated_by: null
replacement: null
retired: null
removed: null
removal_reason: null
---

# Behavioral Contract BC-1.07.003: Subagent stdin is total — unparseable or non-object input renders zero rows

## Description

`main_subagent` absorbs every stdin fault: `json.load(sys.stdin)` wrapped in `try/except Exception`
yields `{}` on any failure, and a successful parse that is not a dict is replaced by `{}` before
rendering. Unparseable stdin therefore degrades to "no rows" (zero bytes, exit 0), never to the 29-byte
degraded line and never to a crash (DI-008 rung: silent emptiness).

## Preconditions

1. ASSUMPTION (ASSUMP-107-1): the Claude Code 2.1.326 `subagentStatusLine` stdin payload is assumed
   compatible with the 2.1.322 contract legacy parsed; to be verified by a capture before Phase 3.
2. The process was routed to the subagent renderer (BC-1.07.001) with the switch on (BC-1.07.002).

## Postconditions

1. Any stdin parse failure (invalid JSON, truncated input, non-UTF-8 bytes, EOF on empty stdin) results
   in the empty task list: zero bytes on stdout, exit code 0. The "non-UTF-8 → zero bytes" leg holds
   under the strict UTF-8 stdio mode pinned by BC-1.01.008 (owner ruling: production locale, no
   surrogateescape; decode semantics per BC-1.01.002); a UTF-8 BOM (U+FEFF) before the first byte is
   likewise a `json.load` JSONDecodeError → `{}` (BC-1.01.008 EC-002, BC-1.01.002 EC-003).
2. A successfully parsed stdin whose top-level value is not a JSON object (scalar, array, `true`,
   `null`) results identically in zero bytes, exit 0.
3. A parsed object is rendered by BC-1.07.004's rules; exit code is 0 whether rows were produced or not.
4. A stdin fault never reaches the 29-byte degraded line from this contract alone — absorption happens
   inside `main_subagent` before any rendering; only render-time faults can degrade (BC-1.07.008).

## Invariants

1. stdin is read exactly once per process.
2. No stdin content can raise out of `main_subagent` via the parse path; the parse wrapper is total.
3. Zero-byte stdout is a valid, parity-pinned outcome (distinct from the degraded line, which is
   non-empty and non-JSON).

## Edge Cases

| ID | Description | Expected Behavior |
|----|-------------|-------------------|
| EC-001 | Empty stdin (CC died mid-refresh) | JSONDecodeError → `{}` → zero bytes, exit 0 |
| EC-002 | stdin `"5"` (valid JSON scalar) | top-level non-dict → `{}` → zero bytes, exit 0 |
| EC-003 | stdin `[{"id":"a1"}]` (array) | top-level non-dict → `{}` → zero bytes, exit 0 |
| EC-004 | stdin `{"tasks": 0}`, `{"tasks": ""}`, `{"tasks": null}` | falsy tasks → `or []` → zero bytes, exit 0 (no iteration fault) |
| EC-005 | stdin is a JSON object with trailing garbage (`{...} x`) | JSONDecodeError → zero bytes, exit 0 |
| EC-006 | Non-UTF-8 byte sequence | decode error inside `json.load` → `{}` → zero bytes, exit 0 (strict UTF-8 stdio per BC-1.01.008; under a `PYTHONUTF8=1`/C-locale surrogateescape mode legacy could render rows — not the parity mode, BC-1.01.008 invariant 2) |
| EC-007 | stdin begins with a UTF-8 BOM (U+FEFF) | `json.load` raises JSONDecodeError ("Unexpected UTF-8 BOM") → `{}` → zero bytes, exit 0 (BC-1.01.008 EC-002) |

## Canonical Test Vectors

| Input | Expected Output | Category |
|-------|----------------|----------|
| stdin `` (empty) | zero bytes, exit 0 | error |
| stdin `{"tasks":[]}` | zero bytes, exit 0 (parsed, no rows — framing contract BC-1.07.004) | happy-path |
| stdin `not json` | zero bytes, exit 0 | error |
| stdin `"5"` | zero bytes, exit 0 | edge-case |

Verified 2026-11-18 against CPython 3.11.7 (`python3 -I`): `main_subagent` absorb semantics from
SL:929-933; falsy-tasks short-circuit from `render_subagent_rows` SL:890-891 (`d.get("tasks") or []`).

## Verification Properties

| VP-NNN | Property | Proof Method |
|--------|----------|-------------|
| VP-005 | For every byte string s, stdin=s yields exit 0 with either rows or zero bytes — never the degraded line via the parse path (stdin-absorb totality leg) | fuzz over stdin corpus |
| VP-006 | Per-call-site JSON depth budget at the subagent stdin-absorb site: depth 993 accepted, 994 rejected and absorbed as `{}` → zero bytes (not the degraded line); same 6-frame chain as stdin (VP-006 §main_subagent row) | fuzz (boundary L/L+1 vs oracle) |

## Traceability

| Field | Value |
|-------|-------|
| L2 Capability | CAP-009 |
| L2 Domain Invariants | DI-008 (exit 0), DI-007 (stdin is the only session input here) |
| Architecture Module | `internal/statusline` (subagent stdin ingestion) |
| Stories | TBD (filled by story-writer) |
| Source | legacy/dgx_statusline.py:`main_subagent` (SL:928-936) |
| Legacy contract | BC-SL-097 (P3r2 §A7) |
| Decisions | OD-155 (restores scope), D4 (byte parity) |

## Related BCs (Recommended)

- BC-1.07.001 — composes with (routes here)
- BC-1.07.004 — composes with (renders the parsed object)
- BC-1.07.008 — related to (render faults, by contrast, do degrade)

## Architecture Anchors (Recommended)

- `architecture/ARCH-03-statusline.md` — subagent stdin ingestion; errors modeled as empty-task-list
  sentinel, not `errDegraded`

## Story Anchor (Recommended)

TBD — filled by story-writer

## VP Anchors (Recommended)

- VP-005 (stdin-absorb totality leg)
- VP-006 (absorb-site decode-depth budget; VP-006 lists this BC in its `bcs:`)

---

### Brownfield-Specific Sections

#### Source Evidence

| Property | Value |
|----------|-------|
| **Path** | `legacy/dgx_statusline.py` (SL:929-933) |
| **Confidence** | high (code read; absorb wrapper is two lines) |
| **Extraction Date** | 2026-11-18 |

#### Evidence Types Used

- **guard clause**: `try: d = json.load(sys.stdin) except Exception: d = {}` (SL:929-932)
- **assertion**: `render_subagent_rows(d if isinstance(d, dict) else {})` (SL:933)

#### Purity Classification

| Property | Assessment |
|----------|-----------|
| **I/O operations** | reads stdin |
| **Global state access** | none |
| **Deterministic** | yes |
| **Thread safety** | n.a. (single-shot process) |
| **Overall classification** | effectful shell |

#### Refactoring Notes

Go: read all of stdin in the shell, then call the pure `pyfmt.Decode(b, ModeText)` (BC-1.01.002,
BC-5.02.003/004) with the stdin depth limit; on any error or non-object, render the
empty list. Never `encoding/json`: it rejects `NaN`/`Infinity` (legacy accepts and renders them),
rewrites `\ud800` to U+FFFD (contradicting BC-1.07.004 EC-005's lone-surrogate wire form), reads
big-int ids as float64 (breaking BC-1.07.004 PC4's verbatim echo), reorders object-id keys through
Go maps, and has no CPython recursion-depth budget. Distinguish "absorb to empty" from `errDegraded`
at the type level so the two DI-008 rungs cannot be conflated.
