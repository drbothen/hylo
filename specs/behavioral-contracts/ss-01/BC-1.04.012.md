---
document_type: behavioral-contract
level: L3
version: "1.3.5"
status: draft
producer: product-owner
timestamp: 2026-11-18T21:00:00Z
phase: 1a
inputs: [domain-spec/L2-INDEX.md, domain-spec/capabilities.md, behavioral-contracts/BC-ALLOCATION.md, semport/hylo-legacy/statusline-target-design.md, semport/hylo-legacy/hylo-legacy-pass-3-behavioral-contracts.md]
input-hash: "ff74134"
traces_to: domain-spec/L2-INDEX.md
origin: brownfield
extracted_from: "legacy/dgx_statusline.py:render_telemetry_fields (SL:822-834)"
subsystem: "SS-01"
capability: "CAP-010"
legacy_id: "BC-SL-051"
parity_class: byte-exact
confidence: H
lifecycle_status: active
introduced: v0.1.0
modified:
  - "1.3 2026-11-17: pass-2 remediation ADV-P2-C2-05/12"
  - "1.3.1 2026-11-18: pass-8 remediation ADV-P8-C2-01 (the marker named as the config key statusline.glyphs.idle with default ☾, OD-189 sibling treatment)"
  - "1.3.2 2026-11-18: pass-9 remediation ADV-P9-C2-09 (PC1 names the registered keys statusline.idle.after_s and statusline.idle.running_below beside their default literals)"
  - "1.3.5 2026-11-18: pass-13 residual (orchestrator residual sweep, CP-C register alignment): EC-006 cites crash id CP-C32, minted by error-taxonomy 1.20 for this contract's foreign cached-sample value leg; no behavioral change"
  - "1.3.3 2026-11-18: pass-11 remediation ADV-P11-C2-09 (version field raised to match the trailing modified entry — it sat behind v1.3.2) + OD-194 consumer (PC4 names statusline.labels.idle beside its default; separating-space scaffolding carries the named-format-constant note)"
  - "1.3.4 2026-11-18: pass-13 remediation ADV-P13-C2-01 (foreign cached-sample value edge case added: EC-006 string last TypeError at the SL:825 gate comparison; OD-160 class; VP-012 closure and VP-001 never-blank rows added; oracle-verified CPython 3.11.7)"
deprecated: null
deprecated_by: null
replacement: null
retired: null
removed: null
removal_reason: null
---

# Behavioral Contract BC-1.04.012: Idle segment

## Description

Row 2 ends with `☾ idle <age>` when the local lane has not received a request for more than
5 minutes and nothing is running on the backend. Only local-lane recency counts, so
cloud-lane traffic cannot mask an idle backend. Notation: `\e` is byte 0x1B.

## Preconditions

1. `last = m.get("dgx_llm_last_dgx_request_timestamp_seconds")` (local-lane last request,
   exported metric; legacy wire name kept, D7).
2. `now` = the single per-render clock read (Go reads it once; legacy reads `time.time()`
   twice at SL:825-826 — output-neutral under the frozen harness clock, design IM-14).
3. Config: `statusline.idle.after_s` 300 (T-011, labeled judgment: "longer than a normal
   think/tool gap between turns", review #20.2), `statusline.idle.running_below` 1
   (T-108, DOC: review #20 "gating (> 5 min AND running < 1) correct"; OD-162 range:
   finite Float ≥ 0, out-of-range = number-range config error, NaN rejected).

## Postconditions

1. Segment exists iff `last` is truthy, `last > 0`,
   `now - last > statusline.idle.after_s` (default 300; strict) and
   `(m.get("vllm:num_requests_running") or 0) < statusline.idle.running_below`
   (default 1).
2. `idle_min = int((now - last) // 60)` (float floor division, CPython `float_divmod`
   semantics, BC-5.01.003).
3. Age text and boundaries per BC-1.04.017: `<d>d<hh>h` from 1440 min, `<h>h<mm>m` from
   60 min, else `<m>m`.
4. Segment = `"\e[36m" + glyphs.idle + " " + labels.idle + " " + age + "\e[0m"`, appended last in row 2,
   where `glyphs.idle` = `statusline.glyphs.idle` (Text, default `☾` U+263E,
   BC-2.01.004 PC-6; the ☾ literals in the vectors are the default spelling,
   ADV-P8-C2-01) and `labels.idle` = `statusline.labels.idle` (Text, default `idle`,
   SL:834, OD-194; the separating spaces stay literal — named format constants, not
   config: template scaffolding).

## Invariants

1. A running request (≥ 1) always suppresses the segment.
2. Stale mode does not change this segment.

## Edge Cases

| ID | Description | Expected Behavior |
|----|-------------|-------------------|
| EC-001 | `last` absent, 0, negative, NaN | no segment |
| EC-002 | running 1 | no segment |
| EC-003 | running 0.5 | shown (`< 1`) |
| EC-004 | running NaN | no segment (`nan < 1` false) |
| EC-005 | running absent or 0.0 | treated as 0 → shown |
| EC-006 | `last` a non-empty string (foreign cached sample, exclusion id **OD-160**; truthy, so the gate continues) | TypeError at the `last > 0` gate comparison (SL:825, ">" not supported between instances of 'str' and 'int', oracle-verified CPython 3.11.7; crash id **CP-C32**) → errDegraded — the idle sibling of the render sites BC-1.04.004 invariant 3 registers (ADV-P13-C2-01) |

## Canonical Test Vectors

`now` = 2000000000.0.

| Input | Expected Output | Category |
|-------|----------------|----------|
| last = now - 360, running absent | `\e[36m☾ idle 6m\e[0m` | happy-path |
| last = now - 66000 | `\e[36m☾ idle 18h20m\e[0m` | happy-path |
| last = now - 300.0 | no segment | edge-case |
| last = now - 400, running 1 | no segment | error |

## Verification Properties

| VP-NNN | Property | Proof Method |
|--------|----------|-------------|
| VP-030 | Seven-case review #20 table reproduces legacy bytes | manual (table) |
| VP-001 | The promised output set holds on the EC-006 foreign cached-sample value degrade leg: render output or the 29-byte degraded line — never blank, exit 0 (DI-008) (ADV-P13-C2-01) | fault-injection ladder (assertPromisedOutputSet, DI-008) |
| VP-012 | The named deviation this contract carries — exclusion id `OD-160` (EC-006 foreign cached-sample value shape) — is covered by the exclusion-closure check: `TestParityExclusions_ClosedSet` validates the `OD-160` entry and its riding table test `TestForeignCacheShape_OD160_Vectors` (this contract has no riding test of its own, same citation class as BC-1.04.002/BC-1.04.003/BC-1.04.018), and the mutation test fails closed if that entry is dropped (ADV-P13-C2-01) | property test (VP-012, go test) |

## Traceability

| Field | Value |
|-------|-------|
| Source | legacy/dgx_statusline.py:render_telemetry_fields (SL:822-834); IDLE_AFTER (SL:90-93) |
| Legacy contract | BC-SL-051 (P3 base; r1 refined, review #20, 7 cases) |
| L2 Capability | CAP-010 |
| L2 Domain Invariants | DI-007, DI-008 (the EC-006 degrade rides the never-blank ladder), DI-012 (foreign cached-sample value shape EC-006 under the OD-160 named-deviation rule) |
| Decisions | OD-113; D7 (metric name frozen) |
| Architecture Module | `internal/statusline/row2.go` |
| Stories | TBD |

## Related BCs (Recommended)

- BC-1.04.017 — refined by: strict gate and age format
- BC-5.01.003 — depends on: float floor division

## Architecture Anchors (Recommended)

- `architecture/ARCH-03-statusline.md#interfaces-design-doc-22-reused-as-the-contract` — internal/statusline/row2.go (idle) (row-2 renderer) (BC-COMPONENT-MAP: ARCH-03 (ARCH-03-statusline.md))

## Story Anchor (Recommended)

TBD — row 2 + metrics client (design §4 step S5)

## VP Anchors (Recommended)

- VP-030 — idle table
- VP-001 — never-blank/exit-0 ladder; the EC-006 degrade leg rides it (ADV-P13-C2-01)
- VP-012 — OD-160 exclusion-closure citation (EC-006; ADV-P13-C2-01)

---

### Brownfield-Specific Sections

#### Source Evidence

| Property | Value |
|----------|-------|
| **Path** | `legacy/dgx_statusline.py` (SL:822-834) |
| **Confidence** | high — re-executed on CPython 3.11.7 |
| **Extraction Date** | 2026-11-15 |

#### Evidence Types Used

- **guard clause**: SL:825
- **documentation**: comment SL:822-823, 827

#### Purity Classification

| Property | Assessment |
|----------|-----------|
| **I/O operations** | none (clock injected) |
| **Global state access** | reads config |
| **Deterministic** | yes given `now` |
| **Thread safety** | Safe for concurrent use |
| **Overall classification** | pure |

#### Refactoring Notes

Pass `now` in; read the clock once per render (removes legacy's minute-straddle between
SL:825 and SL:826 with a live clock; identical under the frozen clock).
