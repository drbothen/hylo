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
extracted_from: "legacy/dgx_statusline.py:_SUB_GLYPH + render_subagent_rows (SL:884-886, 893-896, 922-923)"
subsystem: "SS-01"
capability: "CAP-009"
legacy_id: BC-SL-097
parity_class: byte-exact
confidence: H
lifecycle_status: active
introduced: v0.2.2
modified: ["1.1.1 2026-11-18T03:00:00Z: VP citation reconciliation: no-VP-yet row replaced with VP-010 matrix leg"]
deprecated: null
deprecated_by: null
replacement: null
retired: null
removed: null
removal_reason: null
---

# Behavioral Contract BC-1.07.005: Status glyph, name-fallback chain, and settled-status suffix

## Description

Each row opens with `<col><glyph> <name><RESET>`. The glyph/color pair is looked up from `status` in
`_SUB_GLYPH` (running `»` yellow `\e[33m`; completed `✔` green `\e[32m`; failed `✘` red `\e[31m`;
killed `◍` grey `\e[90m`); any other status falls back to `◍` grey. The display name is the first
non-falsy value of `name → label → description → agentType` (empty strings fall through), else `?`.
Rows with a non-running status append a grey status-text suffix.

## Preconditions

1. ASSUMPTION (ASSUMP-107-1): the Claude Code 2.1.326 `subagentStatusLine` stdin payload is assumed
   compatible with the 2.1.322 contract legacy parsed; to be verified by a capture before Phase 3.
2. Task survived eligibility (BC-1.07.004); status is hashable (else BC-1.07.008 CP-A02).

## Postconditions

1. `status` exact-match against the four map keys; unknown/missing status → glyph `◍` (`\e[90m`),
   color grey.
2. Display name = first non-falsy of `name`, `label`, `description`, `agentType`; none present → the
   literal `?`. An empty-string `name` with a `label` present shows the label.
3. `status` present and not `"running"` → grey suffix ` <status>` (e.g. `completed`, `failed`, `killed`,
   `paused`); status `"running"` → no suffix.
4. Opening bit bytes: `<col>` + glyph + space + name + `\e[0m`.

## Invariants

1. Glyph lookup keys on the RAW status value; the map covers exactly
   {running: («, yellow), completed: (✔, green), failed: (✘, red), killed: (◍, grey)}
   (SL:884-886, `_SUB_GLYPH`).
2. The name chain is `or`-based: `""` does not terminate it; `0`/`False`/missing do not either.
3. Missing status behaves as unknown (◍ grey) AND as a settled row for the suffix rule only if the
   status key exists and is truthy — a missing status adds no suffix.

## Edge Cases

| ID | Description | Expected Behavior |
|----|-------------|-------------------|
| EC-001 | `status` missing entirely | ◍ grey glyph, no status suffix |
| EC-002 | `status = "paused"` (not in map) | ◍ grey, suffix ` paused` grey |
| EC-003 | `name = ""` with `label = "lab"` | shows `lab` (or-chain falls through empty string) |
| EC-004 | All name fields missing | literal `?` after the glyph |
| EC-005 | `failed` row (✘ red) with all name fields | ✘ red + `?` + grey ` failed` trail |
| EC-006 | Unicode names (é, emoji, CJK) | rendered verbatim on the wire inside ensure-ASCII JSON (BC-1.07.004) |

## Canonical Test Vectors

| Input (task dict) | Expected Output (content bits) | Category |
|---|---|---|
| `{"id":"a3","status":"paused"}` | `\e[90m◍ ?\e[0m · \e[90mpaused\e[0m` (JSON: `\u001b[90m◍ ?\u001b[0m · \u001b[90mpaused\u001b[0m`) | happy-path |
| `{"id":"a2","label":"exploré","status":"completed","model":"claude-haiku-5","tokenCount":2500000,"startTime":<now-600000>}` with `model_prefixes = [claude-sonnet]` | `\e[32m✔ exploré\e[0m · \e[35m◨ANTH\e[0m \e[90mclaude-haiku-5\e[0m · \e[36m2.50M tok\e[0m · \e[90mcompleted\e[0m` | happy-path |
| `{"id":"a5","name":"","label":"lab","status":"running"}` | opens `\e[33m» lab` | edge-case |
| `{"id":"a5b","status":"running"}` (no name fields) | opens `\e[33m» ?` | edge-case |
| `{"id":"a14","status":"killed"}` | `\e[90m◍ ?\e[0m · \e[90mkilled\e[0m` | edge-case |

Verified 2026-11-18 against CPython 3.11.7 (`python3 -I`): all five rows byte-reproduced via
`render_subagent_rows`; bytes: ◍=`◍`, »=`»`, ✔=`✔`, ✘=`✘`, ◨=`◨`, é=`é`.

## Verification Properties

| VP-NNN | Property | Proof Method |
|--------|----------|-------------|
| VP-010 | Python-written goldens pin the glyph/name-fallback/settled-suffix matrix bytes; arbitrary-combo differential beyond committed goldens remains open | Tier B golden comparison (Python oracle writes; Go matches) |

## Traceability

| Field | Value |
|-------|-------|
| L2 Capability | CAP-009 |
| L2 Domain Invariants | DI-008 (lookup fault paths degrade, BC-1.07.008), DI-012 (byte parity) |
| Architecture Module | `internal/statusline` (row body) |
| Stories | TBD (filled by story-writer) |
| Source | legacy/dgx_statusline.py: `_SUB_GLYPH` (SL:884-886), glyph/name chain (SL:893-896), status suffix (SL:922-923) |
| Legacy contract | BC-SL-097 (P3r2 §A7, vector set amended r8) |
| Decisions | OD-155, D4 (byte parity); presentation rationale: review 2026-11-13 (#21.2/#21.4) |

## Related BCs (Recommended)

- BC-1.07.004 — composes with (framing)
- BC-1.07.006 — composes with (model segment)
- BC-1.07.007 — composes with (token/clock segments)
- BC-1.07.008 — related to (unhashable status CP-A02 ends in the degraded line)

## Architecture Anchors (Recommended)

- `architecture/ARCH-03-statusline.md` — row-body builder; `_SUB_GLYPH` pinned as a Go map literal

## Story Anchor (Recommended)

TBD — filled by story-writer

## VP Anchors (Recommended)

- VP-010 (glyph/name-fallback/settled-suffix matrix goldens)

---

### Brownfield-Specific Sections

#### Source Evidence

| Property | Value |
|----------|-------|
| **Path** | `legacy/dgx_statusline.py` (SL:884-886, 893-896, 922-923) |
| **Confidence** | high (pinned runs 2026-11-18) |
| **Extraction Date** | 2026-11-18 |

#### Evidence Types Used

- **assertion**: pinned runs for all four glyphs plus fallback and suffix rules
- **guard clause**: `_SUB_GLYPH.get(status, ("◍", GREY))` (SL:894)

#### Purity Classification

| Property | Assessment |
|----------|-----------|
| **I/O operations** | none |
| **Global state access** | none |
| **Deterministic** | yes |
| **Thread safety** | safe for concurrent use (read-only map) |
| **Overall classification** | pure |

#### Refactoring Notes

Go: pinned `map[string]struct{Glyph string; Col string}`; use comma-ok lookup with a packed default.
Keys are the exact four lowercase statuses — do not lowercase/space-normalize input (parity).
