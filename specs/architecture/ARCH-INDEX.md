---
document_type: architecture-index
level: L3
version: "1.14"
status: draft
producer: architect
timestamp: 2026-11-25T16:00:00Z
phase: 1b
inputs: [prd.md, behavioral-contracts/BC-INDEX.md, semport/hylo-legacy/statusline-target-design.md, owner-decisions-log-2026-11-14.md]
input-hash: "b153c99"
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
| Binary & CLI | ARCH-01-binary-cli.md | ~700 | story-writer, implementer | cmd/hylo dispatch incl. `--subagent` routing (OD-155), closed exit-code surface, unknown-flag precedence |
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
| Risk register / mitigations | ../prd-supplements/risk-register.md (R-001..R-009, OD-152) |
| P1-exit vs later phases | ARCH-09 + docs/PLAN.md phases |

## Subsystem Registry (canonical; Policy 6)

> Rule (pass-3 A13, matching on-disk practice 154/154): BC frontmatter `subsystem:`
> carries the **SS-ID** (e.g. `"SS-01"`); stories and prose refer to subsystems by the
> **Name column** (e.g. "Status Line"). The PRD's S1-S12 numbering is the alias key.

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
| AD-01 | Single static binary, modular monolith, seven P1 packages (pass-4 A19) | ARCH-00 | One binary per OS is the PLAN §3 goal; subcommands later |
| AD-02 | Strictly acyclic deps; pyfmt/platform sinks; x/sys sole runtime dep | ARCH-00 | Cycles defeat verification scoping; stdlib-first budget |
| AD-03 | Pure widgets + ordered effect script (not one pure function) | ARCH-03 | Failed-replace read-back semantics require order-preserving effects |
| AD-04 | Hand-written pyfmt with CPython-generated tables, banned Go stdlib codecs on protocol inputs | ARCH-06 | Every cache/widget byte depends on CPython fidelity |
| AD-05 | P1 resolution = HYLO_* env -> built-in defaults; file layer reserved P4 | ARCH-02 | OD-107; zero-dependency budget holds (no YAML) |
| AD-06 | Closed key registry; error classes closed at six, extended to seven (Text) by OD-178 (2026-11-18) with the five canonical tests `TestD4EX3_{Boolean,Enum,URL,Number,Text}` | ARCH-02 | Enumerable domain => closable error set => exhaustively testable |
| AD-07 | Native per-OS ancestor probe replaces ps | ARCH-05 | Removes 6 s latency tail; differences are ruled OD-76/OD-110 entries |
| AD-08 | Byte-exact cache writers over ordered pyfmt.Value; atomic write + Windows retry + temp cleanup | ARCH-04 | Ruling (b) swap coverage; temp cleanup is the ruled temp-file exclusion |
| AD-09 | Three-tier harness; exclusion machinery fails closed | ARCH-07 | Referee must be stronger than refereed; closures provable |
| AD-10 | Env seam set; HYLO_TEST_NOW is a harness hook, not a setting | ARCH-03 | Determinism seams double as harness hooks (RK-5 disposition) |
| AD-11 | Closed verb-scoped exit-code table; 3-OS gate; GitHub Releases | ARCH-01/08 | Exhaustive test surface; D5/D12 |
| AD-12 | Reserved P2-P7 boundaries named; P1 skeleton pre-provisions only FileLayer + backends validator | ARCH-09 | Feature Mode needs unblocked seams, not designs |
| AD-13 | Synthetic-corpus co-location: corpus root `internal/statusline/testdata/parity/cases/` with the committed exclusions file `internal/statusline/testdata/parity/exclusions.json` beside it (OD-148 layout: fixtures stay with the subject package); the generic runner and its `-update` flag live in `internal/parity` and read the fixtures from the subject package; Tier B goldens stay under `internal/statusline/testdata/goldens` | ARCH-07 | One fixture home per fixture class; testdata is opaque to Go, cross-read is deliberate (OD-148; the pass-4 D10 fix aligned all live docs to this layout) |
| AD-14 | Test-only dependencies, pinned in go.mod at adoption: `github.com/flyingmutant/rapid` (metamorphic property generators, ARCH-06/ARCH-00) and `gremlins` (mutation-testing CLI, P19 tool named in ARCH-00) | ARCH-00/06/08 | Each carries a stated reason per the dependency policy; they never enter the runtime binary; the go.mod test-dep additions land on main with the owner's approval (ADV-P2-A19, spec-only in pass 2) |

## Owner tensions (all resolved by owner rulings)

1. **Inert key `statusline.window_age.ps_timeout_s`** — resolved by OD-147 (owner,
   2026-11-16): the key is removed from the registry. `HYLO_STATUSLINE_WINDOW_AGE_PS_TIMEOUT_S`
   is thereafter an unknown `HYLO_*` setting: one stderr warning (`hylo: warning: unknown
   setting <NAME> (ignored)`), then it is ignored — it never changes the output or the
   exit status. There is no unknown-key config-error class to build a story against
   (BC-2.01.001 PC-6, BC-2.01.002 PC-5, VP-015; ADV-P1-A03).
2. **Fixture co-location** (AD-13) — resolved by OD-148 (owner, 2026-11-16): fixtures
   stay with the subject package — corpus root `internal/statusline/testdata/parity/cases/`
   and committed exclusions file `internal/statusline/testdata/parity/exclusions.json`
   beside it; the runner `internal/parity` stays generic and reads the fixtures from the
   subject package (multi-step `steps` live inside `case.json`); AD-13 confirmed. Tier B
   goldens remain under `internal/statusline/testdata/goldens`. The pass-4 D10 fix
   aligned every live doc (ARCH-07, BC-6.02.001/.003, BC-6.03.003/.004, BC-6.04.003,
   the ss-01/ss-02 exclusion rows and the VP-009/VP-012 harness skeletons) to this
   OD-148 layout (BC-6.03.003/.004 PC-1).
3. **Tier C clean-run count** — resolved by OD-149 (owner, 2026-11-16): the Tier C exit
   condition is ONE clean nightly differential-fuzz run on all three OSes, 30 minutes
   of fuzzing per OS (`HYLO_PARITY_FUZZSECONDS=1800`); owner judgment call.
4. **OD-146 recording** — the section breakdown is approved by the owner, OD-146;
   ARCH frontmatter uses 2026-11-15 approval provenance.

## Deferred to Pass 2 / Pass 3

Pass 2 (DONE, 2026-11-16): 38 VP-NNN files + VP-INDEX under
`../verification-properties/` (catalog source of truth). Pass 3 (DONE, 2026-11-16):
VP/architecture anchors inserted into the BC files' Verification Properties / VP Anchors
body sections (spot-checked 2026-11-17 across ss-01/02/04/05/06). ARCH sections carry the
verification-feasibility assessments that Pass 2 formalized.

## Verification Properties (Pass 2 cross-reference)

Catalog: `../verification-properties/VP-INDEX.md` — 41 VPs covering all 154 BCs
(machine-checked; pass-4 orchestration call 18: `VP-041` = the S1.02 for-all property
legs split from VP-028, which keeps the bounded golden tables — as VP-040 was split
from VP-027 in pass 3). By class: invariant 33,
safety 7, performance 1. By primary method: unit/table 20, property/fuzz 13, golden 3,
parity 2, static analysis 1, measured 1, CI observation 1 (matching the VP-INDEX Totals
block, which remains the machine-checked source; VP-011's body class reads "safety, not
liveness (A2-26)"). Zero formal proofs claimed (iron law: Go cycle — the
provable-grade pure cores are verified by exhaustive oracle tables + property/fuzz,
declared per VP). Aggregate VP mapping by primary home (first ARCH home in each
VP-INDEX catalog row; every VP listed exactly once): ARCH-00 P4 → VP-001; ARCH-01 →
VP-002/004; ARCH-02 → VP-015/016/017; ARCH-03 →
VP-003/005/007/008/021/022/027/028/029/030/031/038/039/040/041; ARCH-04 → VP-018/019/020;
ARCH-05 → VP-014/032/033; ARCH-06 → VP-006/023/024/025/026; ARCH-07 →
VP-009/010/011/012/013/034/035; ARCH-08 → VP-036/037. Eight VPs carry a second ARCH
home in VP-INDEX (VP-001, VP-005, VP-014, VP-019, VP-020, VP-022, VP-035, VP-038); all
homes follow the catalog rows (CA-08 alignment generalized 2026-11-17, SC-05).
