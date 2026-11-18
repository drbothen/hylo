---
document_type: behavioral-contract
level: L3
version: "1.2.2"
status: draft
producer: product-owner
timestamp: 2026-11-18T01:45:10Z
phase: 1a
inputs: [domain-spec/L2-INDEX.md, domain-spec/capabilities.md, domain-spec/invariants.md, behavioral-contracts/BC-ALLOCATION.md, semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts-r4.md, semport/hylo-legacy/statusline-target-design.md, owner-decisions-log-2026-11-14.md]
input-hash: "44590c6"
traces_to: domain-spec/L2-INDEX.md
origin: brownfield
extracted_from: "legacy/dgx_statusline.py:_mix_counts (SL:1113-1119, 1094; REBUILD_EXCESS SL:968-972)"
subsystem: "SS-01"
capability: "CAP-009"
legacy_id: "BC-SL-036"
parity_class: "byte-exact"
confidence: "H"
priority: P0
lifecycle_status: active
introduced: "0.1"
modified: ["1.2.1 2026-11-17: rebuild_excess valid range >= 0 (OD-162; ADV-P2-C03)", "1.2.2 2026-11-17: pass-3 remediation (ADV-P3-C03/C10/C16): corrected negative-X rationale, CP-O07 rebuild-check overflow edge case and canonical vector (owner of the SL:1117 site)"]
deprecated: null
deprecated_by: null
replacement: null
retired: null
removed: null
removal_reason: null
---

# Behavioral Contract BC-1.03.007: Rebuild rule at 20,000 excess input tokens

## Description

A counted API call is a cache **rebuild** when its cache write exceeds its context growth by more than
`rebuild_excess` (20,000) tokens: it re-wrote context that was already cached. The parser counts rebuilds in `rb`
and carries the previous call's prompt size in `pp`. The first counted call after a reset or a compaction boundary
is never a rebuild because `pp` is null.

## Preconditions

1. A counted usage object (BC-1.03.005) with `_i`, `_w`, `_r` as in BC-1.03.006.
2. `pp` = cached previous prompt size or null; `rb` = cached rebuild count (0 after reset).
3. `X = statusline.transcript.rebuild_excess` (default 20000; T-056, rationale: **measured** — validated on 9,650
   calls in 120 transcripts: normal calls max 4,145 excess (99.9 % under 577), smallest rebuild 61,901; 20K sits
   about 5× above the worst normal call and 3× below the smallest rebuild; SL:968-971). **Valid range (OD-162):
   `>= 0`**, derived from legacy semantics — `X` is a token-excess comparison threshold against
   `_w − max(0, prompt − pp)` (SL:1117): the excess is negative whenever context growth exceeds the write, so a
   negative `X` would count ordinary growing calls (excess between `X` and 0) as rebuilds (ADV-P3-C16);
   out-of-range values are number-range config errors (S2 schema, OD-114).

## Postconditions

1. `prompt = _i + _w + _r`.
2. If `pp` is not null and `_w - max(0, prompt - pp) > X` (strict), then `rb += 1`.
3. `pp = prompt` (always, for every counted usage, after the test).
4. Lines whose usage is not counted (dedup, BC-1.03.005) leave `rb` and `pp` unchanged.
5. A `compact_boundary` line sets `pp = null` (BC-1.03.008); a reset sets `pp = null`, `rb = 0` (BC-1.03.002).
6. `rb` and `pp` are written to the cache (`"rb"` int, `"pp"` int/float/null).

## Invariants

1. Context shrinkage counts as zero growth (`max(0, …)`), so after a shrink the whole write counts as excess.
2. The comparison is strict: an excess of exactly X is not a rebuild.
3. `max` argument order follows legacy (`max(0, prompt - pp)`); with NaN operands Python returns the first
   argument, 0 (BC-5.01.003).

## Edge Cases

| ID | Description | Expected Behavior |
|----|-------------|-------------------|
| EC-001 | First counted call (pp null) with a 50,000 write | not a rebuild; `pp` = its prompt |
| EC-002 | Excess exactly 20,000 | not a rebuild |
| EC-003 | Excess 20,001 | rebuild |
| EC-004 | Prompt shrank (growth clamped to 0), write 20,001 | rebuild |
| EC-005 | Duplicate-id line with a large write | ignored (not counted) |
| EC-006 | After `compact_boundary`, a 50,000 write | not a rebuild (`pp` null) |
| EC-007 | Overflow at the rebuild check (CP-O07, ADV-P3-C03): a parse state carrying an int `tin` with a float `pp` (legal stored form, postcondition 6) meets a huge exact int write — \|value\| ≥ 2^1024 − 2^970 — in `_w − max(0, prompt − pp)`; a legacy-written cache always couples a float `pp` with a float `tin`, so its next huge-int line raises earlier at SL:1108 | Python raises `OverflowError` at SL:1117 (oracle-verified 2026-11-18: seed `tin` int 0, `pp` 5.0, one line with `cache_creation_input_tokens` 10^309); legacy degrades sticky; hylo skips the line (D4-EX-2 extension, ruling OD-156; this BC owns the SL:1117 site), `rb` and `pp` unchanged (BC-1.03.018) |

## Canonical Test Vectors

Lines `{"type": "assistant", "message": {"content": "", "id": "m<i>", "usage": <u_i>}}`. Five calls, no cache:
u0 = `{"input_tokens": 1000, "cache_read_input_tokens": 100000}`, u1 = `{"cache_creation_input_tokens": 90000,
"cache_read_input_tokens": 11500}` (growth 500 → excess 89,500 → rebuild), u2 = `{"cache_creation_input_tokens":
20000, "cache_read_input_tokens": 101500}` (excess 0), u3 = `{"cache_creation_input_tokens": 40001,
"cache_read_input_tokens": 121500}` (excess 0), u4 = `{"cache_creation_input_tokens": 20001}` (shrink, excess
20,001 → rebuild). Re-pinned 2026-11-15 with the legacy oracle.

| Input | Expected Output | Category |
|-------|----------------|----------|
| u0..u4 in one refresh | `{"size": 678, "res": 0, "conv": 0, "think": 0, "tin": 505502, "tout": 0, "c_wr": 170002, "c_rd": 334500, "mixv6": 1, "c_in": 1000, "rb": 2, "pp": 20001, "ids": ["m0", "m1", "m2", "m3", "m4"], "lr": null, "lu": null, "cur": null}` | happy-path |
| then refresh 2 appends `{"type": "system", "subtype": "compact_boundary"}` and m9 with `{"cache_creation_input_tokens": 50000}` | `{"size": 839, …, "tin": 555502, …, "c_wr": 220002, "c_rd": 334500, …, "rb": 2, "pp": 50000, "ids": ["m0", "m1", "m2", "m3", "m4", "m9"], …}` | edge-case |
| a: `{"cache_read_input_tokens": 100000}`; b: `{"cache_creation_input_tokens": 20000, "cache_read_input_tokens": 80000}` | `"rb": 0`, `"pp": 100000` (excess exactly 20,000) | edge-case |
| same with b write 20001, read 79999 | `"rb": 1`, `"pp": 100000` | edge-case |

Pass-3 r1 pinned an equivalent 5-call scenario (`rb` 2, tin 501,502); the vectors above are an independent re-pin.

CP-O07 vector (ADV-P3-C10; legacy legs oracle-verified 2026-11-18): seed cache exactly `{"size": 0, "res": 0, "conv": 0,
"think": 0, "tin": 0, "tout": 0, "c_wr": 0, "c_rd": 0, "mixv6": 1, "c_in": 0, "rb": 0, "pp": 5.0, "ids": [], "lr": null,
"lu": null, "cur": null}`; transcript is the single line `{"type": "assistant", "message": {"content": "", "id": "y",
"usage": {"cache_creation_input_tokens": 10^309}}}` (415 bytes with LF).

| Input | Expected Output | Category |
|-------|----------------|----------|
| seed + the line above | legacy: `OverflowError` at SL:1117, degraded line, exit 0, cache keeps its seed bytes; hylo (D4-EX-2): cache exactly `{"size": 415, "res": 0, "conv": 0, "think": 0, "tin": 0, "tout": 0, "c_wr": 0, "c_rd": 0, "mixv6": 1, "c_in": 0, "rb": 0, "pp": 5.0, "ids": [], "lr": null, "lu": null, "cur": null}` | error |

## Verification Properties

| VP-NNN | Property | Proof Method |
|--------|----------|-------------|
| VP-029 | `rb` increments iff `pp ≠ null ∧ _w − max(0, prompt − pp) > X` | Go property test (testing/quick) |
| VP-029 | `pp` after a counted call equals that call's prompt | Go property test (testing/quick) |

## Traceability

| Field | Value |
|-------|-------|
| L2 Capability | CAP-009 |
| L2 Domain Invariants | DI-007 |
| Source | legacy/dgx_statusline.py:_mix_counts (SL:1113-1119, 1094); constant SL:968-972 |
| Legacy contract | BC-SL-036 (base; pinned pass-3 r1) |
| Threshold | T-056 → `statusline.transcript.rebuild_excess` = 20000 (measured) |
| Parity class | byte-exact |
| Architecture Module | `internal/statusline/transcript.go` |
| Stories | S-TBD |

## Related BCs (Recommended)

- BC-1.03.006 — depends on: `_i/_w/_r`
- BC-1.03.008 — composes with: compaction clears `pp`
- BC-1.03.005 — depends on: only counted usage participates

## Architecture Anchors (Recommended)

- `architecture/ARCH-03-statusline.md#interfaces-design-doc-22-reused-as-the-contract` — internal/statusline/transcript.go (rebuild 20,000) (BC-COMPONENT-MAP: ARCH-03 (ARCH-03-statusline.md))

## Story Anchor (Recommended)

S-TBD — transcript parser

## VP Anchors (Recommended)

- VP-029 — rebuild predicate

---

### Brownfield-Specific Sections

#### Source Evidence

| Property | Value |
|----------|-------|
| **Path** | `legacy/dgx_statusline.py` (`_mix_counts`, SL:1113-1119; `REBUILD_EXCESS` SL:968-972) |
| **Confidence** | high |
| **Extraction Date** | 2026-11-15 |

#### Evidence Types Used

- **guard clause**: `if pp is not None and _w - max(0, prompt - pp) > REBUILD_EXCESS` (SL:1117)
- **documentation**: measured rationale SL:968-971

#### Purity Classification

| Property | Assessment |
|----------|-----------|
| **I/O operations** | none |
| **Global state access** | none (reads the config value) |
| **Deterministic** | yes |
| **Thread safety** | yes |
| **Overall classification** | pure |

#### Refactoring Notes

No refactoring needed; `X` comes from `config.Statusline` (D15).
