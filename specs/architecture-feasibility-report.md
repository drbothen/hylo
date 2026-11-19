---
document_type: architecture-feasibility-report
level: ops
version: "1.16"
status: approved
producer: architect
timestamp: 2026-11-25T09:00:00Z
modified: ["1.9 2026-11-18: pass-5 sync A2-21 — catalog count amended to 41 VPs (VP-041); pass-5 remediation burst 6", "1.10 2026-11-18: pass-6 A2-08 — six error classes amended to seven (OD-178 Text class)", "1.11 2026-11-19: pass-6 residual sweep — BC-1.06.001 parity class synced to temp-file in the §8 constraint row (OD-163 own-temp-cleanup divergence; ADV-P6-C16)", "1.12 2026-11-19T16:00:00Z: sync-check adv-p6 closure (SC-26) — modified history re-spun oldest-first so the version field matches the last entry; no behavioral change", "1.13 2026-11-21T00:00:00Z: pass-9 residual sweep (ADV-P9-A09) — both 'AD-03 overlay decision' cells respelled per R-001: the AD-03 decision — the in-memory overlay option was rejected (AD-03 rejected the overlay option; the old cells misdescribed it as an overlay decision)", "1.14 2026-11-21T20:00:00Z: pass-12 fix (A2-13) — prd_version re-pinned 0.1 → 0.2.22 (tracks prd.md) and the settled-rulings range widened OD-115..OD-149 → OD-115..OD-194 with the re-pin disclosed in the intro", "1.15 2026-11-24T16:00:00Z: pass-13 residual (item 6) — the S1 Subsystem-to-Module Mapping row classifies `internal/cost` as pure core (no I/O; `internal/statusline` loads and saves the cost-history file through its `CacheStore`), per orchestrator call 7 / ADV-P13-A02 and the amended ARCH-00 package table", "1.16 2026-11-25T09:00:00Z: pass-14 fix (ADV-P14-A2-09) — prd_version re-pinned 0.2.22 → 0.2.25 (tracks prd.md) and the settled-rulings range widened OD-115..OD-194 → OD-115..OD-195 (OD-195 is the pass-14 stop rule), re-pin disclosed in the intro"]
phase: 1b
inputs: [prd.md, prd-supplements/nfr-catalog.md, prd-supplements/module-criticality.md, prd-supplements/interface-definitions.md, architecture/ARCH-INDEX.md, verification-properties/VP-INDEX.md]
input-hash: "00c5cc7"
traces_to: prd.md
prd_version: "0.2.25"

---

# Architecture Feasibility Report

Architect review of the L3 PRD (`prd.md` v0.2.25 at review, re-pinned from v0.2.22,
pass-14 A2-09; 145 BCs at v0.1 review time, subsystem
breakdown S1-S6 active
/ S7-S12 reserved) for subsystem-grouping feasibility. Scope: NFR coherence, integration
feasibility, purity-boundary alignment, verifiability. Owner rulings OD-115..OD-195 are
treated as settled and were not reopened (range re-widened OD-115..OD-194 →
OD-115..OD-195 with the pass-14 stop rule, after the pass-12 re-pin from the
review-time OD-115..OD-149 range, pass-12 A2-13; the body tracks the amended PRD
through pass 9 and this pass).

## Executive Summary

The PRD is feasible as written. The six active subsystems partition the 145 BCs along
lines that map one-to-one onto verifiable Go packages, every headline NFR is coherent
within its owning subsystem, and the 38-VP catalog covers all 145 BCs with viable
empirical strategies. No PRD changes are required. *(Amended 2026-11-17, pass-2 A2-23
and OD-155: the catalog is 38 VPs, the oracle pin is CPython 3.11.x per OD-104, and
OD-155 ports the subagent panel — BC-1.07.001..008, 153 BCs total — into S1/
`sl/subagent.go` without moving a subsystem boundary; feasibility verdict unchanged.)*
*(Amended 2026-11-18, adv-p2 sync check SC-05: the review-time counts in this paragraph
predate the pass-2 VP rebuild — the on-disk PRD totals 153 BCs and the catalog 40 VPs
(VP-039 subagent elapsed clock, VP-040 frame/width property legs; module-criticality
tallies regenerated to match). Original figures and verdict retained.)*
*(Amended 2026-11-18, pass-3 consolidated sync: BC-5.01.007 (mixed int/float `Num` semantics,
ADV-P3-D08) brings the on-disk total to 154 BCs; S5 Pyfmt is now 20. Subsystem grouping and
feasibility verdict unchanged; original figures retained.)*
*(Amended 2026-11-18, pass-5 sync A2-21: the catalog is 41 VPs — VP-041 (pass 4,
dense-grid/`_hm`/`win_ms` property legs) was not propagated into this report by the
pass-4 sweep; VP-INDEX remains the catalog source of truth and shows 41; verdict
unchanged.)*

## Constraint Mapping

| PRD Section | BC-S.SS.NNN | Requirement | Architecture Constraint | Feasibility | Resolution |
|-------------|-------------|-------------|------------------------|-------------|-----------|
| §1.2, §4 | BC-6.03.002, BC-6.04.001 | Byte parity vs the CPython 3.11.x oracle (OD-104), 0 unexplained diffs | Three-tier harness (AD-09); referee stronger than refereed | feasible | Tier A/B/C in ARCH-07; exclusion closure VP-012 |
| §4 NFR-001 | BC-6.04.002 | p95 <= 25 ms render on the owner's Mac, metrics wait excluded | Pure hot path, no allocation-heavy idioms; gate binds only with `HYLO_TIMING_GATE=1` | feasible | Measured VP-036; OD-117 binding note honored |
| §4 NFR-002 | BC-1.01.001 et al. | Never-blank, exit-0 under all CP-* triggers | Guard backstop + typed degrades; write order preserved | feasible | Fault-injection tables VP-001/VP-003 |
| §1.2 (OD-107) | BC-2.01.001 | P1 config = `HYLO_*` env over built-in defaults only | Registry closed; seven error classes closed (OD-114/134/140; seventh Text class OD-178 — pass-6 A2-08) | feasible | Resolution totality VP-015/VP-016/VP-017 |
| §8 (ruling b) | BC-1.06.001/.002, BC-6.02.004 | Go is byte-exact cache writer/reader across Python/Go swaps, four caches | Byte-exact writers over ordered `pyfmt.Value`; atomic write + Windows retry (AD-08). BC-1.06.001 rides the `temp-file` class (OD-110) for the OD-163 own-temp-cleanup divergence — payload bytes stay byte-exact | risky | Swap-parity tier VP-019; failed-replace semantics pinned by the AD-03 decision — the in-memory overlay option was rejected |
| §1.6 S3 | BC-3.02.001/.002 | Native per-OS ancestor probe replaces `ps` | Build-tag-confined `internal/platform`; x/sys sole runtime dep (AD-07) | feasible | Probe register VP-033; D4-EX-1 bound VP-014; OQ-3 measurement deferred by design |
| §2.5 (OD-103) | BC-5.01..5.04 | Python-semantics formatting (half-even, WTF-8, `_mktime`, 4,300-digit grammar) | One sink package `internal/pyfmt`, four files, CPython-generated tables (AD-04) | feasible | Equivalence VPs VP-023..026; `math/big` at the ruled duration-format sites (OD-137, extended to the `_fmt_lines` lines/thresholds path by OD-156 — pass-4 A2-15) |
| §8 DI-012 | BC-6.03.004 | Closed, glob-free exclusion set; new class needs owner decision | Exclusion machinery fails closed (AD-09) | feasible | VP-012 property test; `cp-x03` rides the closed set (OD-136) |

## Subsystem Grouping Assessment

| L2 Subsystem (CAP-NNN) | PRD Grouping Valid? | NFR Profile Coherent? | Notes |
|------------------------|--------------------|-----------------------|-------|
| S1 Status Line (CAP-009/010/011; DI-007/008) | yes | yes | 101 BCs incl. the OD-155 subagent panel (BC-1.07.001..008), one mixed core-dominant package. Latency (NFR-001), reliability (NFR-002) and bounds (NFR-005) do not conflict: the metrics HTTP wait is off the timed path by case model, removing the only latent tension |
| S2 Configuration (CAP-015; DI-010/008) | yes | yes | 13 BCs; typed validation gates every setting; closed class register makes the error surface exhaustively testable |
| S3 Platform (CAP-009 support; DI-008) | yes | yes | 3 BCs; inherently effectful (syscalls, per-OS divergence) — grouped apart from the pure core, which is the correct call |
| S4 CLI (CAP-009/015; DI-008) | yes | yes | 3 BCs; thin dispatch, closed verb-scoped exit surface; MEDIUM tier is proportionate |
| S5 Pyfmt (enabler, OD-103) | yes | yes | 19 BCs *(amended 2026-11-18, pass-3 sync: 20 after BC-5.01.007)*; pure-core island whose NFR profile is purely parity; isolating it from I/O is what makes the equivalence targets reachable |
| S6 Parity Harness (DI-012 machinery) | yes | yes | 14 BCs; test-only infrastructure, never in the render path; hygiene NFR-006 anchored here |
| S7-S12 reserved | yes (out of cycle) | n/a | No BCs; ARCH-09 preserves their seams (FileLayer, backends validator) without designs |

### Proposed Restructuring (if any)

None. The L2-derived grouping is preserved verbatim; the only decomposition the
architect adds below module level (splitting `internal/cost` out of `internal/statusline`)
does not move a subsystem boundary and stays inside S1's CRITICAL scope.

## Subsystem-to-Module Mapping (Preliminary)

| L2 Subsystem | Proposed Modules | Pure/Effectful | Notes |
|-------------|-----------------|---------------|-------|
| S1 | `internal/statusline`, `internal/cost` | mixed (core-dominant) / pure core | Pure widgets + ordered effect script via `Env` seams (AD-03); `internal/cost` is PURE CORE — no I/O of any kind, pure functions over caller-passed values (the loaded cost history, the current session's numbers, `now`) returning the new history and the thresholds, while `internal/statusline` loads and saves the cost-history file through its `CacheStore` (ADV-P13-A02, orchestrator call 7; ARCH-00 package table, ARCH-03 §Interfaces declared API); cost inherits S1's CRITICAL tier — the >= 95 % kill rate is a Phase 6 target, tracked and reported by the formal-verifier, NOT a P1 gate (OD-158; pass-4 A2-21) |
| S2 | `internal/config` | boundary | Pure registry/grammars; env read once at `Load` |
| S3 | `internal/platform` | infrastructure | Syscalls, `/proc`, `sysctl`, Win32; build tags |
| S4 | `cmd/hylo` | effectful shell | `os.Args`/`os.Std*`/`os.Exit`; no logic |
| S5 | `internal/pyfmt` | pure core | No I/O of any kind; clock never read |
| S6 | `internal/parity` | infrastructure | Spawns interpreters; test-only |

Component homes for all 145 BCs *(amended 2026-11-18, adv-p2 sync check SC-05: 153 BCs
after OD-155; BC-COMPONENT-MAP is current for all 153)* *(pass-3 sync 2026-11-18: current for all 154 after BC-5.01.007)*: `architecture/BC-COMPONENT-MAP.md`.

## Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| Python/Go cache-swap byte divergence (four caches) | medium | high | Byte-exact writers over ordered `pyfmt.Value`; Tier B goldens + four-cache swap tier (VP-019); failed-replace semantics pinned by the AD-03 decision — the in-memory overlay option was rejected |
| p95 <= 25 ms miss on the owner's Mac | medium | medium | Legacy baseline measured (median 84.5 ms); hot-path allocation discipline; per-OS timing report; gate binds only where OD-117 says |
| Windows-only edge cases marked "not executed" (BC-1.06.001 EC-008, BC-1.06.002 EC-003/005; sitecustomize shim) | medium | medium | Pinned on the windows-2025 CI leg and the harness canary (PRD Assumption 5); disclosed, not hidden |
| Fake-pass parity: harness weaker than refereed | low | high | AD-09 fail-closed machinery, canary (BC-6.01.003), exclusion closure property test (VP-012); HIGH tier, whose kill-rate target is a Phase 6 target per OD-158, not a P1 gate (pass-4 A2-21) |
| Purity-annotation drift: per-BC Purity Classification sections present in 90/145 BC files, uneven in enabler/effectful shards (ss-02 1/13, ss-05 4/19) — *amended 2026-11-17 (CA-07): on-disk count is now 145/145; the remaining shards were annotated during the 2026-11-16 Pass 3 anchor back-fill. Original verdict retained.* | low | low | Boundary is carried at module level (ARCH-00 table) and per-VP effectful-shell declarations; recommend annotating the remaining shards during Pass 3 anchor back-fill — documentation consistency, not a feasibility gap *(completed 2026-11-16, 145/145; ss-05 shard now 20 files after BC-5.01.007, pass-3 sync 2026-11-18)* |

Canonical IDs (OD-152, 2026-11-17): the rows above are minted as R-001..R-005, and the
PRD-carried RK-5/RK-6 dispositions as R-006/R-007, in
[prd-supplements/risk-register.md](prd-supplements/risk-register.md).

## Decision Log

| Decision | Alternatives Considered | Chosen | Rationale |
|----------|------------------------|--------|-----------|
| Accept subsystem grouping as-is | Merge S2 into S1; split S1 parser into own subsystem | Accept | Referencing AD-01/AD-02: the grouping already equals the acyclic package map; merging would blur the config error surface, splitting would add an import seam without a verification benefit |
| Endorse AD-03 (pure widgets + ordered effect script, not one pure function) | One pure render + final commit block | Option 2 in ARCH-03 | Referencing AD-03 because legacy read-back semantics (failed replace persists nothing) make a single pure function unable to satisfy BC-1.01.009/BC-1.06.002; order-preserving effects are required for cache-state parity |
| `internal/cost` inherits S1 CRITICAL rather than getting its own tier | Classify separately | Inherit | Referencing SS-01 because the PO's module-criticality row for `internal/statusline` already enumerates "cost history" in its rationale; the package split is architectural only |
| Treat VP-INDEX as catalog source of truth for coverage claims | Per-BC anchors only | VP-INDEX | Referencing AD-13/POLICY 9; BC VP-anchor back-fill is Pass 3 (deferred by schedule, not by feasibility). Architect-side nit found and logged: the ARCH-INDEX by-home aggregate buckets VP-022 under ARCH-07/08 while the VP-INDEX catalog row says ARCH-03/ARCH-04/ARCH-09 — to be corrected in ARCH-INDEX at the next architect burst (derived view, no PRD impact). **Resolved 2026-11-17 (CA-08, quote corrected pass-3 A2-27):** the ARCH-INDEX by-home aggregate now reads `ARCH-03/ARCH-04/ARCH-09 → VP-022`, matching the VP-INDEX catalog row; nit closed |
| Confirm "architect to confirm" module anchors in BC Traceability tables | Defer to story-writer | Confirmed via BC-COMPONENT-MAP | Referencing BC-COMPONENT-MAP (154/154 homes incl. the OD-155 BC-1.07 rows; *pass-3 sync 2026-11-18: 154/154 after BC-5.01.007*): Pass 3 back-fill can replace the placeholders mechanically |

## Approval

| Role | Decision | Date |
|------|----------|------|
| Architect | approve | 2026-11-16 |
| Product Owner | acknowledged | — |

PRD CHANGES REQUIRED: none
