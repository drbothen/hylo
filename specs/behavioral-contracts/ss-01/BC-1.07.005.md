---
document_type: behavioral-contract
level: L3
version: "1.1.3"
status: draft
producer: product-owner
timestamp: 2026-11-18T08:00:00Z
phase: 1a
inputs: [behavioral-contracts/BC-ALLOCATION.md, domain-spec/L2-INDEX.md, semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts-r2.md, semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts-r8.md]
input-hash: "fff619b"
traces_to: domain-spec/L2-INDEX.md
origin: brownfield
extracted_from: "legacy/dgx_statusline.py:_SUB_GLYPH + render_subagent_rows (SL:845-846, 893-896, 921-922)"
subsystem: "SS-01"
capability: "CAP-009"
legacy_id: BC-SL-097
parity_class: byte-exact
confidence: H
lifecycle_status: active
introduced: v0.2.2
modified: ["1.1.1 2026-11-18T03:00:00Z: VP citation reconciliation: no-VP-yet row replaced with VP-010 matrix leg", "1.1.2 2026-11-18T07:00:00Z: adv-p3 remediation: running glyph corrected to U+00BB with SL:845-846/921-922 cites (ADV-P3-C02); goldens re-derived ensure_ascii-escaped (ADV-P3-C01); glyph/color pairs sourced from statusline.subagent.* config keys, no Go map literal (ADV-P3-C05); str() rendering of non-string chain/status values specified (ADV-P3-C14)", "1.1.3 2026-11-18T08:00:00Z: pass-4 remediation: PC3 suffix gate tied to the legacy `if st and st != \"running\"` truthy gate with a present-falsy-status edge case (ADV-P4-C06); unknown-status fallback named statusline.subagent.glyphs.unknown, independent of glyphs.killed (ADV-P4-C07, design call 4)"]
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
the status map (running U+00BB yellow `\e[33m`; completed U+2714 green `\e[32m`; failed U+2718 red
`\e[31m`; killed U+25CD grey `\e[90m`); any other status falls back to U+25CD grey. The display name
is the first non-falsy value of `name → label → description → agentType` (empty strings fall through),
else `?`. Rows with a non-running status append a grey status-text suffix.

## Preconditions

1. ASSUMPTION (ASSUMP-107-1): the Claude Code 2.1.326 `subagentStatusLine` stdin payload is assumed
   compatible with the 2.1.322 contract legacy parsed; to be verified by a capture before Phase 3.
2. Task survived eligibility (BC-1.07.004); status is hashable (else BC-1.07.008 CP-A02).

## Postconditions

1. `status` exact-match against the four map keys; unknown/missing status → glyph U+25CD
   (`\e[90m`), color grey. The fallback is its own config key (ADV-P4-C07, orchestrator design call 4):
   `statusline.subagent.glyphs.unknown` (Text, default `◍` = U+25CD) with the colour from
   `statusline.theme.grey` (default `90`); it is an independent key and does NOT follow
   `glyphs.killed`.
2. Display name = first non-falsy of `name`, `label`, `description`, `agentType`; none present → the
   literal `?`. An empty-string `name` with a `label` present shows the label.
3. `status` present, truthy, and not `"running"` → grey suffix ` <status>` (e.g. `completed`, `failed`,
   `killed`, `paused`) — the legacy gate is `if st and st != "running"` (SL:921); a present but falsy
   status (`""`, `0`, `False`, `null`) adds NO suffix (Inv3); status `"running"` → no suffix.
4. Opening bit bytes: `<col>` + glyph + space + name + `\e[0m`.
5. Truthy non-string values in the chain or in the suffix render through Python f-string `str()`
   coercion (`pyfmt.Str`): `True`, `1.0`, `['x']`, `{'a': 1}` display as exactly those literals
   (verified wire forms below); a truthy non-string hashable `status` (e.g. `True`, `1`, `1.5`) shows
   the U+25CD fallback glyph plus a grey `str(status)` suffix (verified: ` True`, ` 1`, ` 1.5`).

## Invariants

1. Glyph lookup keys on the RAW status value; the map covers exactly
   {running: (U+00BB, yellow), completed: (U+2714, green), failed: (U+2718, red), killed: (U+25CD,
   grey)} (SL:845-846, `_SUB_GLYPH`); with defaults the pairs come from the
   `statusline.subagent.glyphs.<status>` / `statusline.subagent.colors.<status>` config keys whose
   legacy defaults are exactly these bytes (ADV-P3-C05 ruling; registered by the architect in the
   BC-2.01.004 registry) — no Go map literal owns them (D15).
2. The name chain is `or`-based: `""` does not terminate it; `0`/`False`/missing do not either.
3. Missing status behaves as unknown (\u25cd grey) AND as a settled row for the suffix rule only if the
   status key exists and is truthy — a missing status adds no suffix.

## Edge Cases

| ID | Description | Expected Behavior |
|----|-------------|-------------------|
| EC-001 | `status` missing entirely | U+25CD grey glyph, no status suffix |
| EC-002 | `status = "paused"` (not in map) | U+25CD grey, suffix ` paused` grey |
| EC-003 | `name = ""` with `label = "lab"` | shows `lab` (or-chain falls through empty string) |
| EC-004 | All name fields missing | literal `?` after the glyph |
| EC-005 | `failed` row (U+2718 red) with all name fields | U+2718 red + `?` + grey ` failed` trail |
| EC-006 | Unicode names (accented letters, emoji, CJK) | rendered verbatim on the wire inside ensure-ASCII JSON (BC-1.07.004) |
| EC-007 | Truthy non-string chain value (`name=True` / `1.0` / `['x']` / `{'a': 1}`) | displayed as the `str()` literal (`True`, `1.0`, `['x']`, `{'a': 1}`) — PC5 |
| EC-008 | `status` present but falsy (`""`, `0`, `False`, `null`) | fallback glyph U+25CD grey (not a map key), NO status suffix — the `and` half of the SL:921 gate (ADV-P4-C06; oracle-checked 2026-11-18) |

## Canonical Test Vectors

| Input (task dict) | Expected Output (content bits) | Category |
|---|---|---|
| `{"id":"a3","status":"paused"}` | content `"\u001b[90m\u25cd ?\u001b[0m \u00b7 \u001b[90mpaused\u001b[0m"` | happy-path |
| `{"id":"a2","label":"explor\u00e9","status":"completed","model":"claude-haiku-5","tokenCount":2500000,"startTime":<now-600000>}` with `model_prefixes = [claude-sonnet]` | content `"\u001b[32m\u2714 explor\u00e9\u001b[0m \u00b7 \u001b[35m\u25e8ANTH\u001b[0m \u001b[90mclaude-haiku-5\u001b[0m \u00b7 \u001b[36m2.50M tok\u001b[0m \u00b7 \u001b[90mcompleted\u001b[0m"` | happy-path |
| `{"id":"a5","name":"","label":"lab","status":"running"}` | opens `\e[33m` + U+00BB + ` lab` | edge-case |
| `{"id":"a5b","status":"running"}` (no name fields) | opens `\e[33m` + U+00BB + ` ?` | edge-case |
| `{"id":"a14","status":"killed"}` | content `"\u001b[90m\u25cd ?\u001b[0m \u00b7 \u001b[90mkilled\u001b[0m"` | edge-case |
| `{"id":"c","name":true,"status":"completed"}` | content `"\u001b[32m\u2714 True\u001b[0m \u00b7 \u001b[90mcompleted\u001b[0m"` (`str()` coercion, PC5) | edge-case |
| `{"id":"c","status":1}` | content `"\u001b[90m\u25cd ?\u001b[0m \u00b7 \u001b[90m1\u001b[0m"` (fallback glyph + `str()` suffix, PC5) | edge-case |

Verified 2026-11-18 against CPython 3.11.7 (`python3 -I`): all rows byte-reproduced via
`render_subagent_rows`; goldens re-derived escaped after the adv-p3 C01 escape-decoding incident.
Source-level UTF-8 bytes of the glyphs: running=c2 bb, completed=e2 9c 94, failed=e2 9c 98,
killed=e2 97 8d, pill-square=e2 97 a8, accented-e=c3 a9, joiner=c2 b7; on the wire each appears
only as its `\uXXXX` escape (BC-1.07.004 PC3).

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
| Source | legacy/dgx_statusline.py: `_SUB_GLYPH` (SL:845-846), glyph/name chain (SL:893-896), status suffix (SL:921-922) |
| Legacy contract | BC-SL-097 (P3r2 §A7, vector set amended r8) |
| Decisions | OD-155, D4 (byte parity); adv-p3: ADV-P3-C05 config-key sourcing; presentation rationale: review 2026-11-13 (#21.2/#21.4) |

## Related BCs (Recommended)

- BC-1.07.004 — composes with (framing)
- BC-1.07.006 — composes with (model segment)
- BC-1.07.007 — composes with (token/clock segments)
- BC-1.07.008 — related to (unhashable status CP-A02 ends in the degraded line)

## Architecture Anchors (Recommended)

- `architecture/ARCH-03-statusline.md` — row-body builder in `subagent.go`; glyph/color pairs loaded
  from the `statusline.subagent.glyphs.<status>` / `statusline.subagent.colors.<status>` config keys
  (legacy defaults = the SL:845-846 bytes), registered per the ADV-P3-C05 ruling — not a Go map literal

## Story Anchor (Recommended)

TBD — filled by story-writer

## VP Anchors (Recommended)

- VP-010 (glyph/name-fallback/settled-suffix matrix goldens)

---

### Brownfield-Specific Sections

#### Source Evidence

| Property | Value |
|----------|-------|
| **Path** | `legacy/dgx_statusline.py` (SL:845-846, 893-896, 921-922) |
| **Confidence** | high (pinned runs 2026-11-18) |
| **Extraction Date** | 2026-11-18 |

#### Evidence Types Used

- **assertion**: pinned runs for all four glyphs plus fallback and suffix rules
- **guard clause**: `_SUB_GLYPH.get(status, ("\u25cd", GREY))` (SL:894)

#### Purity Classification

| Property | Assessment |
|----------|-----------|
| **I/O operations** | none |
| **Global state access** | none |
| **Deterministic** | yes |
| **Thread safety** | safe for concurrent use (read-only map) |
| **Overall classification** | pure |

#### Refactoring Notes

Go: load the four glyph/color pairs from resolved config (`statusline.subagent.glyphs.<status>` /
`statusline.subagent.colors.<status>`, defaults exactly the legacy bytes); comma-ok lookup with the
fallback drawn from its own key `statusline.subagent.glyphs.unknown` (default `◍`, U+25CD) coloured
by `statusline.theme.grey` — an independent key that does not follow `glyphs.killed` (ADV-P4-C07).
Keys are the exact four lowercase statuses — do not
lowercase/space-normalize input (parity). Chain and suffix values render through the `pyfmt.Str`
convention (Python `str()` semantics).
