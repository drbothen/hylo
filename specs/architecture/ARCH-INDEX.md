---
document_type: architecture-index
level: L3
version: "1.0"
status: draft
producer: architect
timestamp: 2026-11-16T00:00:00Z
phase: 1b
inputs: [prd.md, behavioral-contracts/BC-INDEX.md, semport/hylo-legacy/statusline-target-design.md, owner-decisions-log-2026-11-14.md]
input-hash: "c243f11"
traces_to: ../prd.md
deployment_topology: single-service
---

# Architecture Index: hylo P1 (status line)

> Lightweight index; agents load only the sections they need. Owner-approved section
> breakdown 2026-11-15 (approved by the owner, OD-146). Design reference for all IM/PR/CP/T
> rows: `../semport/hylo-legacy/statusline-target-design.md`.

## Document Map

| Section | File | Tokens | Primary Consumer | Purpose |
|---------|------|--------|-----------------|---------|
| Overview | ARCH-00-overview.md | ~900 | orchestrator, all agents | Principles (D4/D15/pure-core-effects/never-blank), package map, acyclic dependency direction |
| Binary & CLI | ARCH-01-binary-cli.md | ~700 | story-writer, implementer | cmd/hylo dispatch, closed exit-code surface, unknown-flag precedence |
| Configuration | ARCH-02-configuration.md | ~900 | implementer, test-writer | Key registry (D15/OD-114), HYLO_* grammars, D4-EX-3, resolution skeleton |
| Status line pipeline | ARCH-03-statusline.md | ~1100 | story-writer, implementer, formal-verifier | Pure widgets + ordered effect script, Env seams, effect-step script |
| Data files | ARCH-04-data-files.md | ~800 | implementer | Cache dir layout, byte-exact writers, atomic writes, reserved ledger |
| Platform | ARCH-05-platform.md | ~700 | implementer | Build-tag confined per-OS dirs, native ancestor probe, x/sys |
| Pyfmt | ARCH-06-pyfmt.md | ~1000 | implementer, formal-verifier | Python-semantics helpers, CPython tables, fuzz targets, math/big |
| Parity harness | ARCH-07-parity-harness.md | ~1200 | devops, test-writer | Tiers A/B/C, oracle exec, exclusion closure, OD-145 names table |
| Build/CI/release | ARCH-08-build-ci-release.md | ~700 | devops-engineer | go 1.26, dep policy, 3-OS matrix, timing gate, releases, hygiene |
| Reserved boundaries | ARCH-09-reserved-boundaries.md | ~700 | story-writer guard | P2-P7 package boundaries, known constraints, no design |

## Cross-References

| If you need... | Read these together |
|----------------|-------------------|
| Story decomposition inputs | ARCH-03 + ARCH-02 + BC-COMPONENT-MAP.md |
| Verification plan for a module | ARCH-00 purity table + owning section + prd-supplements/test-vectors.md |
| Harness implementation | ARCH-07 + prd-supplements/nfr-catalog.md (timing) |
| P1-exit vs later phases | ARCH-09 + docs/PLAN.md phases |

## Subsystem Registry (canonical; Policy 6)

> BC frontmatter `subsystem:` and stories use the Name column verbatim. The PRD's
> S1-S12 numbering is the alias key.

| SS ID | Name | Alias | Architecture Doc | Implementing Modules | Phase |
|-------|------|-------|-----------------|---------------------|-------|
| SS-01 | Status Line | S1 | ARCH-03 (+ARCH-04 caches) | `internal/statusline`, `internal/cost` | P1 |
| SS-02 | Configuration | S2 | ARCH-02 | `internal/config` | P1 |
| SS-03 | Platform | S3 | ARCH-05 | `internal/platform` | P1 |
| SS-04 | CLI | S4 | ARCH-01 | `cmd/hylo` | P1 |
| SS-05 | Pyfmt | S5 | ARCH-06 | `internal/pyfmt` | P1 |
| SS-06 | Parity Harness | S6 | ARCH-07 | `internal/parity` | P1 |
| SS-07 | Exporter | S7 | ARCH-09 (boundary) | reserved (P2) | P2 |
| SS-08 | Proxy And Routing | S8 | ARCH-09 (boundary) | reserved (P3) | P3 |
| SS-09 | Ledger | S9 | ARCH-09 (boundary) | reserved (P3) | P3 |
| SS-10 | Launcher Hook Doctor CA | S10 | ARCH-09 (boundary) | reserved (P4) | P4 |
| SS-11 | UIs | S11 | ARCH-09 (boundary) | reserved (P4/P6) | P4/P6 |
| SS-12 | Multi-Backend | S12 | ARCH-09 (boundary) | reserved (P6) | P6 |

**ID format:** SS-NN, append-only; reserved subsystems keep their SS-ID when activated.

## Architecture Decisions (inline ADRs; full records in the cited section)

| ID | Decision | Section | Rationale (one-line) |
|----|----------|---------|---------------------|
| AD-01 | Single static binary, modular monolith, six P1 packages | ARCH-00 | One binary per OS is the PLAN §3 goal; subcommands later |
| AD-02 | Strictly acyclic deps; pyfmt/platform sinks; x/sys sole runtime dep | ARCH-00 | Cycles defeat verification scoping; stdlib-first budget |
| AD-03 | Pure widgets + ordered effect script (not one pure function) | ARCH-03 | Failed-replace read-back semantics require order-preserving effects |
| AD-04 | Hand-written pyfmt with CPython-generated tables, banned Go stdlib codecs on protocol inputs | ARCH-06 | Every cache/widget byte depends on CPython fidelity |
| AD-05 | P1 resolution = HYLO_* env -> built-in defaults; file layer reserved P4 | ARCH-02 | OD-107; zero-dependency budget holds (no YAML) |
| AD-06 | Closed key registry; error classes closed at six | ARCH-02 | Enumerable domain => closable error set => exhaustively testable |
| AD-07 | Native per-OS ancestor probe replaces ps | ARCH-05 | Removes 6 s latency tail; differences are ruled OD-76/OD-110 entries |
| AD-08 | Byte-exact cache writers over ordered pyfmt.Value; atomic write + Windows retry + temp cleanup | ARCH-04 | Ruling (b) swap coverage; temp cleanup is the ruled temp-file exclusion |
| AD-09 | Three-tier harness; exclusion machinery fails closed | ARCH-07 | Referee must be stronger than refereed; closures provable |
| AD-10 | Env seam set; HYLO_TEST_NOW is a harness hook, not a setting | ARCH-03 | Determinism seams double as harness hooks (RK-5 disposition) |
| AD-11 | Closed verb-scoped exit-code table; 3-OS gate; GitHub Releases | ARCH-01/08 | Exhaustive test surface; D5/D12 |
| AD-12 | Reserved P2-P7 boundaries named; P1 skeleton pre-provisions only FileLayer + backends validator | ARCH-09 | Feature Mode needs unblocked seams, not designs |
| AD-13 | Fixture co-location under internal/statusline/testdata, runner in internal/parity | ARCH-07 | One fixture home; testdata is opaque to Go, cross-read is deliberate (confirmed by OD-148) |

## Owner tensions (all resolved by owner rulings)

1. **Inert key `statusline.window_age.ps_timeout_s`** — resolved by OD-147 (owner,
   2026-11-16): the key is removed from the registry; setting it is an ordinary
   unknown-key config error.
2. **Fixture co-location** (AD-13) — resolved by OD-148 (owner, 2026-11-16): fixtures
   stay with the subject package under `internal/statusline/testdata/parity/...`; the
   runner `internal/parity` stays generic; AD-13 confirmed.
3. **Tier C clean-run count** — resolved by OD-149 (owner, 2026-11-16): the Tier C exit
   condition is ONE clean nightly differential-fuzz run on all three OSes, 30 minutes
   of fuzzing per OS (`HYLO_PARITY_FUZZSECONDS=1800`); owner judgment call.
4. **OD-146 recording** — the section breakdown is approved by the owner, OD-146;
   ARCH frontmatter uses 2026-11-15 approval provenance.

## Deferred to Pass 2 / Pass 3

Pass 2 (DONE, 2026-11-16): 37 VP-NNN files + VP-INDEX under
`../verification-properties/` (catalog source of truth). Pass 3 (back-fill, later
burst): VP/architecture anchors inserted into BC files. ARCH sections carry the
verification-feasibility assessments that Pass 2 formalized.

## Verification Properties (Pass 2 cross-reference)

Catalog: `../verification-properties/VP-INDEX.md` — 37 VPs covering all 145 BCs
(machine-checked). By class: invariant 29, safety 6, liveness 1, performance 1. By
primary method: unit/table 19, golden/parity 8, property/fuzz 7, static analysis 1,
measured 1, CI observation 1. Zero formal proofs claimed (iron law: Go cycle — the
provable-grade pure cores are verified by exhaustive oracle tables + property/fuzz,
declared per VP). Aggregate VP mapping by home: ARCH-01 → VP-002/004; ARCH-02 →
VP-015/016/017; ARCH-03 (+ARCH-04 stores) → VP-001/003/005/006/007/008/018/020/021/
027/028/029/030/031/036; ARCH-05 → VP-014/032/033; ARCH-06 → VP-006/023/024/025/026;
ARCH-04/09 → VP-022; ARCH-07/08 → VP-009/010/011/012/013/019/034/035/037.
