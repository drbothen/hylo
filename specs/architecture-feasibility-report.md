---
document_type: architecture-feasibility-report
level: ops
version: "1.0"
status: approved
producer: architect
timestamp: 2026-11-16T12:00:00Z
phase: 1b
inputs: [prd.md, prd-supplements/nfr-catalog.md, prd-supplements/module-criticality.md, prd-supplements/interface-definitions.md, architecture/ARCH-INDEX.md, verification-properties/VP-INDEX.md]
input-hash: "0221974"
traces_to: prd.md
prd_version: "0.1"
---

# Architecture Feasibility Report

Architect review of the L3 PRD (`prd.md` v0.1, 145 BCs, subsystem breakdown S1-S6 active
/ S7-S12 reserved) for subsystem-grouping feasibility. Scope: NFR coherence, integration
feasibility, purity-boundary alignment, verifiability. Owner rulings OD-115..OD-149 are
treated as settled and were not reopened.

## Executive Summary

The PRD is feasible as written. The six active subsystems partition the 145 BCs along
lines that map one-to-one onto verifiable Go packages, every headline NFR is coherent
within its owning subsystem, and the 37-VP catalog covers all 145 BCs with viable
empirical strategies. No PRD changes are required.

## Constraint Mapping

| PRD Section | BC-S.SS.NNN | Requirement | Architecture Constraint | Feasibility | Resolution |
|-------------|-------------|-------------|------------------------|-------------|-----------|
| §1.2, §4 | BC-6.03.002, BC-6.04.001 | Byte parity vs CPython 3.11.7 oracle, 0 unexplained diffs | Three-tier harness (AD-09); referee stronger than refereed | feasible | Tier A/B/C in ARCH-07; exclusion closure VP-012 |
| §4 NFR-001 | BC-6.04.002 | p95 <= 25 ms render on the owner's Mac, metrics wait excluded | Pure hot path, no allocation-heavy idioms; gate binds only with `HYLO_TIMING_GATE=1` | feasible | Measured VP-036; OD-117 binding note honored |
| §4 NFR-002 | BC-1.01.001 et al. | Never-blank, exit-0 under all CP-* triggers | Guard backstop + typed degrades; write order preserved | feasible | Fault-injection tables VP-001/VP-003 |
| §1.2 (OD-107) | BC-2.01.001 | P1 config = `HYLO_*` env over built-in defaults only | Registry closed; six error classes closed (OD-114/134/140) | feasible | Resolution totality VP-015/VP-016/VP-017 |
| §8 (ruling b) | BC-1.06.001/.002, BC-6.02.004 | Go is byte-exact cache writer/reader across Python/Go swaps, four caches | Byte-exact writers over ordered `pyfmt.Value`; atomic write + Windows retry (AD-08) | risky | Swap-parity tier VP-019; failed-replace semantics pinned by AD-03 overlay decision |
| §1.6 S3 | BC-3.02.001/.002 | Native per-OS ancestor probe replaces `ps` | Build-tag-confined `internal/platform`; x/sys sole runtime dep (AD-07) | feasible | Probe register VP-033; D4-EX-1 bound VP-014; OQ-3 measurement deferred by design |
| §2.5 (OD-103) | BC-5.01..5.04 | Python-semantics formatting (half-even, WTF-8, `_mktime`, 4,300-digit grammar) | One sink package `internal/pyfmt`, four files, CPython-generated tables (AD-04) | feasible | Equivalence VPs VP-023..026; `math/big` at two duration sites (OD-137) |
| §8 DI-012 | BC-6.03.004 | Closed, glob-free exclusion set; new class needs owner decision | Exclusion machinery fails closed (AD-09) | feasible | VP-012 property test; `cp-x03` rides the closed set (OD-136) |

## Subsystem Grouping Assessment

| L2 Subsystem (CAP-NNN) | PRD Grouping Valid? | NFR Profile Coherent? | Notes |
|------------------------|--------------------|-----------------------|-------|
| S1 Status line (CAP-009/010/011; DI-007/008) | yes | yes | 93 BCs, one mixed core-dominant package. Latency (NFR-001), reliability (NFR-002) and bounds (NFR-005) do not conflict: the metrics HTTP wait is off the timed path by case model, removing the only latent tension |
| S2 Configuration (CAP-015; DI-010/008) | yes | yes | 13 BCs; typed validation gates every setting; closed class register makes the error surface exhaustively testable |
| S3 Platform (CAP-009 support; DI-008) | yes | yes | 3 BCs; inherently effectful (syscalls, per-OS divergence) — grouped apart from the pure core, which is the correct call |
| S4 CLI (CAP-009/015; DI-008) | yes | yes | 3 BCs; thin dispatch, closed verb-scoped exit surface; MEDIUM tier is proportionate |
| S5 Pyfmt (enabler, OD-103) | yes | yes | 19 BCs; pure-core island whose NFR profile is purely parity; isolating it from I/O is what makes the equivalence targets reachable |
| S6 Parity harness (DI-012 machinery) | yes | yes | 14 BCs; test-only infrastructure, never in the render path; hygiene NFR-006 anchored here |
| S7-S12 reserved | yes (out of cycle) | n/a | No BCs; ARCH-09 preserves their seams (FileLayer, backends validator) without designs |

### Proposed Restructuring (if any)

None. The L2-derived grouping is preserved verbatim; the only decomposition the
architect adds below module level (splitting `internal/cost` out of `internal/statusline`)
does not move a subsystem boundary and stays inside S1's CRITICAL scope.

## Subsystem-to-Module Mapping (Preliminary)

| L2 Subsystem | Proposed Modules | Pure/Effectful | Notes |
|-------------|-----------------|---------------|-------|
| S1 | `internal/statusline`, `internal/cost` | mixed (core-dominant) / boundary | Pure widgets + ordered effect script via `Env` seams (AD-03); cost inherits S1 CRITICAL kill-rate target |
| S2 | `internal/config` | boundary | Pure registry/grammars; env read once at `Load` |
| S3 | `internal/platform` | infrastructure | Syscalls, `/proc`, `sysctl`, Win32; build tags |
| S4 | `cmd/hylo` | effectful shell | `os.Args`/`os.Std*`/`os.Exit`; no logic |
| S5 | `internal/pyfmt` | pure core | No I/O of any kind; clock never read |
| S6 | `internal/parity` | infrastructure | Spawns interpreters; test-only |

Component homes for all 145 BCs: `architecture/BC-COMPONENT-MAP.md`.

## Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| Python/Go cache-swap byte divergence (four caches) | medium | high | Byte-exact writers over ordered `pyfmt.Value`; Tier B goldens + four-cache swap tier (VP-019); failed-replace semantics pinned by the AD-03 overlay decision |
| p95 <= 25 ms miss on the owner's Mac | medium | medium | Legacy baseline measured (median 84.5 ms); hot-path allocation discipline; per-OS timing report; gate binds only where OD-117 says |
| Windows-only edge cases marked "not executed" (BC-1.06.001 EC-008, BC-1.06.002 EC-003/005; sitecustomize shim) | medium | medium | Pinned on the windows-2025 CI leg and the harness canary (PRD Assumption 5); disclosed, not hidden |
| Fake-pass parity: harness weaker than refereed | low | high | AD-09 fail-closed machinery, canary (BC-6.01.003), exclusion closure property test (VP-012); HIGH kill-rate tier |
| Purity-annotation drift: per-BC Purity Classification sections present in 90/145 BC files, uneven in enabler/effectful shards (ss-02 1/13, ss-05 4/19) | low | low | Boundary is carried at module level (ARCH-00 table) and per-VP effectful-shell declarations; recommend annotating the remaining shards during Pass 3 anchor back-fill — documentation consistency, not a feasibility gap |

## Decision Log

| Decision | Alternatives Considered | Chosen | Rationale |
|----------|------------------------|--------|-----------|
| Accept subsystem grouping as-is | Merge S2 into S1; split S1 parser into own subsystem | Accept | Referencing AD-01/AD-02: the grouping already equals the acyclic package map; merging would blur the config error surface, splitting would add an import seam without a verification benefit |
| Endorse AD-03 (pure widgets + ordered effect script, not one pure function) | One pure render + final commit block | Option 2 in ARCH-03 | Referencing AD-03 because legacy read-back semantics (failed replace persists nothing) make a single pure function unable to satisfy BC-1.01.009/BC-1.06.002; order-preserving effects are required for cache-state parity |
| `internal/cost` inherits S1 CRITICAL rather than getting its own tier | Classify separately | Inherit | Referencing SS-01 because the PO's module-criticality row for `internal/statusline` already enumerates "cost history" in its rationale; the package split is architectural only |
| Treat VP-INDEX as catalog source of truth for coverage claims | Per-BC anchors only | VP-INDEX | Referencing AD-13/POLICY 9; BC VP-anchor back-fill is Pass 3 (deferred by schedule, not by feasibility). Architect-side nit found and logged: the ARCH-INDEX by-home aggregate buckets VP-022 under ARCH-07/08 while the VP-INDEX catalog row says ARCH-04/09 — to be corrected in ARCH-INDEX at the next architect burst (derived view, no PRD impact) |
| Confirm "architect to confirm" module anchors in BC Traceability tables | Defer to story-writer | Confirmed via BC-COMPONENT-MAP | Referencing BC-COMPONENT-MAP (145/145 homes): Pass 3 back-fill can replace the placeholders mechanically |

## Approval

| Role | Decision | Date |
|------|----------|------|
| Architect | approve | 2026-11-16 |
| Product Owner | acknowledged | — |

PRD CHANGES REQUIRED: none
