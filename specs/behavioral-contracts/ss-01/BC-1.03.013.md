---
document_type: behavioral-contract
level: L3
version: "1.3.2"
status: draft
producer: product-owner
timestamp: 2026-11-17T12:00:00Z
phase: 1a
inputs: [domain-spec/L2-INDEX.md, domain-spec/capabilities.md, domain-spec/invariants.md, behavioral-contracts/BC-ALLOCATION.md, semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts-r4.md, semport/hylo-legacy/statusline-target-design.md, owner-decisions-log-2026-11-14.md]
input-hash: "6a5b563"
traces_to: domain-spec/L2-INDEX.md
origin: brownfield
extracted_from: "legacy/dgx_statusline.py:_mix_counts (SL:1016-1017; _MIX_CACHE SL:951)"
subsystem: "SS-01"
capability: "CAP-009"
legacy_id: "BC-SL-070"
parity_class: "byte-exact"
confidence: "H"
priority: P0
lifecycle_status: active
introduced: "0.1"
modified:
  - "1.3 2026-11-18T23:00:00Z: pass-5 remediation (ADV-P5-C12) — `日本` row promoted to the canonical vectors as the per-code-point discriminator; EC-002 corrected (per-byte gives 100, masked by truncation) and EC-002/EC-006 remarks aligned"
  - "1.3.1 2026-11-19T02:00:00Z: sync-check adv-p5 closure (SC-15) — frontmatter YAML repaired (stray leading comma removed from the modified list); no behavioral change"
  - "1.3.2 2026-11-19T03:00:00Z: pass-6 remediation (ADV-P6-C09 / call 12) — Inv3 points to `pyfmt.SubNonWord` over Value code points (BC-5.03.003), never plain rune iteration (WTF-8 surrogate bytes would give three RuneErrors, not one `_`)"
deprecated: null
deprecated_by: null
replacement: null
retired: null
removed: null
removal_reason: null
---

# Behavioral Contract BC-1.03.013: Mix cache sid sanitized per code point

## Description

The mix-cache file name embeds the session id after Python `re.sub(r"[^A-Za-z0-9_-]", "_", sid)[:40]`: every
**code point** outside ASCII letters, digits, `_` and `-` becomes one `_`, and the result is truncated to 40
**code points**. A missing/falsy session id becomes `"nosession"` (shared by all id-less sessions). A truthy
non-string session id makes the substitution raise, which degrades the refresh (crash path CP-S14, byte-parity
scope).

## Preconditions

1. BC-1.03.001's checks passed (a regular transcript file exists); only then is the sid read.
2. `sid = d.session_id` if truthy, else `"nosession"`.

## Postconditions

1. `sid` is a string → `sid' = Truncate(SubNonWord(sid, '_'), 40)` with per-code-point semantics
   (`pyfmt.SubNonWord`, `pyfmt.Truncate`, BC-5.03.003 / BC-5.03.001); file name `statusline-mix-<sid'>.json`.
2. A lone surrogate (WTF-8) is one code point → one `_`.
3. `sid` truthy and not a string (number, `true`, array, object) → the refresh degrades: the 29-byte degraded line,
   exit 0 (BC-1.01.001), before any mix-cache read or write; earlier side effects (none at this step) persist.
4. The 40-code-point truncation is a named constant (T-061, rationale: derived — ≥ 36, the length of a session
   UUID, so real ids are never truncated; file-name format shared with legacy), not config.

## Invariants

1. The substitution happens before truncation (so multi-byte characters never produce more than one `_` each).
2. The session cache (`statusline-<sid>.json`) uses the **raw** sid, not this sanitized form (OD-03; BC-1.06.001).
3. The regex is RE2-safe; Go iterates code points via `pyfmt.SubNonWord` over the decoded `Value` (BC-5.03.003
   PC1: every code point outside `A-Za-z0-9_-` becomes one `_`), never plain `range` rune iteration — a plain
   range over WTF-8 surrogate bytes (`ED A0 80`) yields three `RuneError`s, which would give `___` where the
   contract pins one `_` (BC-1.03.013 PC2; ADV-P6-C09 / call 12).

## Edge Cases

| ID | Description | Expected Behavior |
|----|-------------|-------------------|
| EC-001 | `a.b/c d` | `a_b_c_d` |
| EC-002 | `é` × 50 | 40 × `_` (a per-byte substitution would give 100, and truncation to 40 masks the difference — this case alone does not discriminate; the discriminating canonical case is `日本`, EC-006) |
| EC-003 | `../../etc` | `______etc` (no path traversal) |
| EC-004 | 50 × `x` | 40 × `x` |
| EC-005 | `""` / null / missing | `nosession` |
| EC-006 | `日本` | `__` (2 code points substitute to 2 `_` with no truncation involved; per-byte would give 6. Canonical discriminator, promoted to the vector table ADV-P5-C12) |
| EC-007 | sid `123` (int) with an existing transcript | degraded line (CP-S14); `TypeError: expected string or bytes-like object` in legacy |
| EC-008 | sid `true` / `["a"]` | degraded (CP-S14) |
| EC-009 | sid `0` / `false` | falsy → `nosession`, no degrade |
| EC-010 | Windows file-name rules | OD-03: legacy behavior kept as-is (the sanitized form contains only `[A-Za-z0-9_-]`, valid on all OSes) |

## Canonical Test Vectors

Re-pinned 2026-11-15 with the legacy oracle (CPython 3.11).

| Input | Expected Output | Category |
|-------|----------------|----------|
| sid `a.b/c d` | `statusline-mix-a_b_c_d.json` | happy-path |
| sid `ok-_9` | `statusline-mix-ok-_9.json` | happy-path |
| sid = 50 × `é` | `statusline-mix-________________________________________.json` (40 underscores) | edge-case |
| sid `../../etc` | `statusline-mix-______etc.json` | edge-case |
| sid `日本` | `statusline-mix-__.json` (2 underscores; per-byte would give 6 — the per-code-point discriminator, ADV-P5-C12) | edge-case |
| sid `""` | `statusline-mix-nosession.json` | edge-case |
| sid `123` (JSON number), transcript exists | stdout = `\x1b[90mstatusline degraded\x1b[0m\n` (29 bytes), exit 0, no mix cache | error |

## Verification Properties

| VP-NNN | Property | Proof Method |
|--------|----------|-------------|
| VP-029 | `sid'` equals CPython's for random Unicode strings (incl. astral and lone surrogates) | fuzz (differential) |
| VP-029 | `sid'` matches `^[A-Za-z0-9_-]{0,40}$` | Go property test (testing/quick) |

## Traceability

| Field | Value |
|-------|-------|
| L2 Capability | CAP-009 |
| L2 Domain Invariants | DI-008 |
| Source | legacy/dgx_statusline.py:_mix_counts (SL:1016-1017); `_MIX_CACHE` (SL:951) |
| Legacy contract | BC-SL-070 (pass-3 r1, new) |
| Threshold | T-061 (40 chars) — named constant |
| Parity class | byte-exact |
| Decisions | OD-03 (keep legacy: raw sid in session cache, sanitized mix cache) |
| Architecture Module | `internal/statusline/mixcache.go`; `internal/pyfmt` str |
| Stories | S-TBD |

## Related BCs (Recommended)

- BC-1.03.002 — composes with: the cache file name
- BC-5.03.003 — depends on: `SubNonWord` per code point
- BC-1.06.001 — related to: raw sid in the session cache
- BC-1.01.001 — related to: degraded line for CP-S14

## Architecture Anchors (Recommended)

- `architecture/ARCH-03-statusline.md#interfaces-design-doc-22-reused-as-the-contract` — internal/statusline/mixcache.go (sid sanitize) (BC-COMPONENT-MAP: ARCH-03 (ARCH-03-statusline.md))

## Story Anchor (Recommended)

S-TBD — mix cache

## VP Anchors (Recommended)

- VP-029 — sanitizer differential

---

### Brownfield-Specific Sections

#### Source Evidence

| Property | Value |
|----------|-------|
| **Path** | `legacy/dgx_statusline.py` (SL:951, 1016-1017) |
| **Confidence** | high |
| **Extraction Date** | 2026-11-15 |

#### Evidence Types Used

- **type constraint**: `re.sub` requires str (raises on other types)
- **inferred**: per-code-point semantics of Python `re` on `str`

#### Purity Classification

| Property | Assessment |
|----------|-----------|
| **I/O operations** | none |
| **Global state access** | none |
| **Deterministic** | yes |
| **Thread safety** | yes |
| **Overall classification** | pure |

#### Refactoring Notes

`mixCacheName(sid Value) (string, error)`; the error wraps `errDegraded` (CP-S14).
