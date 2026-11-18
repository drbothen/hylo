---
document_type: prd-supplement-nfr-catalog
level: L3
version: "1.3"
status: draft
producer: product-owner
timestamp: 2026-11-18T01:38:15Z
phase: 1a
stage: "3 of 3 (integration)"
inputs: [prd.md]
input-hash: "c2ae96e"
traces_to: prd.md, domain-spec/L2-INDEX.md
---

# Non-Functional Requirements Catalog: hylo P1

> PRD supplement — extracted from PRD Section 4.
> Referenced by: architect, performance-engineer, formal-verifier.

## NFR Registry

| ID | Category | Requirement | Target | Validation Method | Priority | Risk Source |
|----|----------|-------------|--------|------------------|----------|-------------|
| NFR-001 | Performance | Steady-state render latency on the owner's Mac (darwin/arm64), synthetic fixture corpus, metrics HTTP wait excluded | p95 <= 25 ms (OD-117). Legacy baseline measured 2026-11-15: median 84.5 ms, p90 101 ms; ~25 ms interpreter start removed by the port | owner-Mac timing gate (schedule and sampling in the binding note, ADV-P2-A16): per case 1 warm-up + 20 timed runs, sorted, nearest-rank p95 = 19th sample; p95 computed per case, gate binds per case, no pooling; fake-VM handling time subtracted; gate fails only with `HYLO_TIMING_GATE=1` | P0 | porting-decision latency tension |
| NFR-002 | Reliability | Never-blank, exit-0 rendering under every fault in the main render: stdin faults, transcript faults, metrics faults, cache faults, config errors, unknown flags. Carve-out (OD-155): in `--subagent` mode zero stdout bytes is a legitimate outcome (renderer off, zero eligible rows, unparseable input, and config error per OD-168; BC-1.07.002/.003/.004); the subagent crash-path degrades still land on the 29-byte line | 100% of CP-S01..S17, CP-T01..T07, CP-N01/N02, CP-O01..O05, CP-O10/O11, CP-A01..A05 triggers produce >= 1 stdout byte and exit 0 | fault-injection table tests per owning BC | P0 | DI-008 |
| NFR-003 | Correctness (parity) | Byte parity vs the CPython oracle: stdout bytes + exit code per step; named caches byte-for-byte. Interpreter pin is dual (ADV-P3-A19): vector and oracle facts are pinned on CPython 3.11.7 locally; CI installs 3.11.x (setup-python resolves the latest patch) | 0 unexplained diffs; every explained diff on the named exclusion list with its own table test | parity harness (BC-6.03.002) + Tier C differential fuzz (BC-6.04.003) | P0 | D4 exit criterion |
| NFR-004 | Portability | Three-OS support (D5): macOS, Linux, Windows; OS-specific code confined to `internal/platform` | CI green on ubuntu-24.04, macos-15 (arm64), windows-2025 for every change; Go 1.26.x; -race clean on the Linux and macOS legs (windows-2025 leg runs without -race, as ARCH-08 defines the matrix) | CI matrix leg per OS | P0 | D5 |
| NFR-005 | Resource bounds | Bounded per-refresh state, legacy caps only — the list is exhaustive: 256-id usage dedup (legacy `ids[-256:]`, SL:1153), 32-point metric histories (legacy `hist[-32:]`, SL:350), 512 KB transcript read step (legacy `_READ_CAP = 524288`, SL:952), 90 s history age cap (legacy `SPARK_MAX_AGE = 90.0`, SL:83; BC-1.04.003). No cap outside this list exists in legacy; none may be invented (P13, ADV-P2-A20) | table-verified caps identical to legacy | table tests | P1 | legacy equivalence |
| NFR-006 | Security/hygiene | Public-repo hygiene: synthetic committed fixtures only; real inputs only from git-ignored captures/; secret scan clean | gitleaks + category pattern scan clean on every push and CI leg | CI leg + `TestCorpusHygiene` | P0 | policy 21 |

## NFR Categories

| Category | Description | Validation Agent |
|----------|-------------|-----------------|
| Performance | Render latency, timing gate | performance-engineer |
| Reliability | Never-blank, degraded ladder | formal-verifier |
| Correctness | Byte parity, exclusion closure | performance-engineer (harness), formal-verifier |
| Portability | Cross-platform CI | devops-engineer |
| Resource bounds | Memory/step caps | formal-verifier |
| Security/hygiene | Fixture provenance, secret scan | security-reviewer |

## NFR-to-Module Mapping

| NFR ID | Affected Modules | Architectural Impact |
|--------|-----------------|---------------------|
| NFR-001 | `internal/statusline`, `internal/pyfmt` | pure render path; no allocation-heavy idioms on the hot path; metrics fetch off the timed path per case model |
| NFR-002 | `internal/statusline` (guard), `cmd/hylo` | top-level recover + typed CP-* degrades; write ordering preserved (BC-1.01.009) |
| NFR-003 | `internal/parity`, `internal/pyfmt` | Go `encoding/json` and `strconv` banned on protocol inputs (IM-01, BC-5.01.002 invariant 1) |
| NFR-004 | `internal/platform` | build tags; per-OS probes with named edge differences (BC-3.02.001/.002) |
| NFR-005 | `internal/statusline` | caps are named constants where legacy fixed them (T-061/062 class), registry keys where tunable |
| NFR-006 | `internal/parity` corpus, CI | committed testdata is synthetic; captures/ git-ignored |

## Binding note (OD-117) and gate schedule (ADV-P2-A16)

The NFR-001 gate binds on the owner's Mac target only; CI legs print the report and pass
whatever the numbers are (BC-6.04.002 EC-002/003). The p95 figure excludes the metrics
HTTP wait by case model (BC-6.02.003), matching how the 84.5 ms legacy baseline was
measured on 2026-11-15.

**When the owner-Mac gate runs (ADV-P2-A16):** the gate is an explicit P1-exit step run
locally on the owner's Mac — not a CI job. After the Tier A parity harness is green on
the full corpus, the owner runs the timing gate with `HYLO_TIMING_GATE=1` on the owner's
Mac (darwin/arm64) over the same synthetic corpus; the P1 exit record cites that run. No
CI job sets `HYLO_TIMING_GATE=1`; OD-158's test-coverage gate (line coverage
>= 95% for S1/S5) is the only additional P1 exit gate.

**Sampling (defined):** per corpus case, 1 discarded warm-up + 20 timed runs; samples
sorted per case; nearest-rank p95 = 19th of the 20 sorted samples (with 5 samples the
statistic degenerates to the maximum — hence 20). p95 is computed per case and the gate
binds per case; samples are not pooled across cases. Fake-VM handling time is subtracted
per the case model.

## Test-coverage gating (OD-158)

The P1 exit gate for the module-critical modules (S1 Status Line, S5 Pyfmt) is **line
coverage >= 95%** per package, from the coverage report of the package `go test` runs.
The mutation kill-rate targets in `module-criticality.md` (>= 95% CRITICAL, >= 90% HIGH,
>= 80% MEDIUM) are **Phase 6 targets**, tracked by the formal-verifier; they do not gate
P1.
