---
document_type: prd-supplement-nfr-catalog
level: L3
version: "1.11"
status: draft
producer: product-owner
timestamp: 2026-11-21T03:00:00Z
phase: 1a
stage: "3 of 3 (integration)"
inputs: [prd.md]
input-hash: "69dbef0"
traces_to: prd.md, domain-spec/L2-INDEX.md
---

# Non-Functional Requirements Catalog: hylo P1

> PRD supplement — extracted from PRD Section 4.
> Referenced by: architect, performance-engineer, formal-verifier.

## NFR Registry

| ID | Category | Requirement | Target | Validation Method | Priority | Risk Source |
|----|----------|-------------|--------|------------------|----------|-------------|
| NFR-001 | Performance | Steady-state render latency on the owner's Mac (darwin/arm64), synthetic fixture corpus, metrics HTTP wait excluded | p95 <= 25 ms (OD-117). Legacy baseline measured 2026-11-15: median 84.5 ms, p90 101 ms; ~25 ms interpreter start removed by the port | owner-Mac timing gate (schedule and sampling in the binding note, ADV-P2-A16): per case 1 warm-up + 20 timed runs, sorted, nearest-rank p95 = 19th sample; a TIMED RUN = one full execution of the case's step sequence, wall-clocked end to end, with caches and seeds reset to the case's declared state before EVERY run, warm-up included — all samples of a case measure one identical workload (pass-11 A11/call 16); p95 computed per case, gate binds per case, no pooling; fake-VM handling time subtracted; gate fails only with `HYLO_TIMING_GATE=1`; the >512 KB timing-fixture exemption is conditional (OD-187): it applies only when that fixture misses the 25 ms target, and its use is reported. The exempt fixture is identified by a validated case flag `timing_exempt: large-transcript` (exactly one case, transcript exceeding 512 KB — more than 524,288 bytes; 512 KiB, equal to the `transcript.read_cap_bytes` default), the gate still fails if that fixture's p95 exceeds 100 ms (OD-191, judgment call: 4x the target, well under the refresh interval), and the job prints one report line when the exemption is used (pass-7 A02/call 3) | P0 | porting-decision latency tension |
| NFR-002 | Reliability | Never-blank, exit-0 rendering under every fault in the main render: stdin faults, transcript faults, metrics faults, cache faults, config errors, unknown flags. Carve-out (OD-155): in `--subagent` mode zero stdout bytes is a legitimate outcome (renderer off, zero eligible rows, unparseable input, and config error per OD-168; BC-1.07.002/.003/.004); the subagent crash-path degrades still land on the 29-byte line | 100% of CP-S01..S17, CP-T01..T07, CP-N01/N02/N03, CP-O01..O05, CP-O10/O11/O12, CP-A01..A05, CP-T09 triggers produce >= 1 stdout byte and exit 0 | fault-injection table tests per owning BC | P0 | DI-008 |
| NFR-003 | Correctness (parity) | Byte parity vs the CPython oracle: stdout bytes + exit code per step; named caches byte-for-byte. Interpreter pin is dual (ADV-P3-A19): vector and oracle facts are pinned on CPython 3.11.7 locally; CI installs 3.11.x (setup-python resolves the latest patch, OD-104/OD-185). Harness self-check (OD-185): at start the harness re-measures the JSON depth boundaries and `unicodedata.unidata_version` against the resolved oracle and fails closed on any mismatch, printing the resolved version; golden metadata records the resolved patch | 0 unexplained diffs; every explained diff on the named exclusion list with its own table test | parity harness (BC-6.03.002) + Tier C differential fuzz (BC-6.04.003) | P0 | D4 exit criterion |
| NFR-004 | Portability | Three-OS support (D5): macOS, Linux, Windows; OS-specific code confined to `internal/platform` | CI green on ubuntu-24.04, macos-15 (arm64), windows-2025 for every change; Go 1.26.x; -race clean on the Linux and macOS legs (windows-2025 leg runs without -race, as ARCH-08 defines the matrix) | CI matrix leg per OS | P0 | D5 |
| NFR-005 | Resource bounds | Bounded per-refresh render state, legacy caps only — the four-cap list is exhaustive FOR PER-RENDER STATE: 256-id usage dedup (legacy `ids[-256:]`, SL:1153), 32-point metric histories (legacy `hist[-32:]`, SL:350), 512 KB transcript read step (legacy `_READ_CAP = 524288`, SL:952), 90 s history age cap (legacy `SPARK_MAX_AGE = 90.0`, SL:83; BC-1.04.003). No render-state cap outside this list exists in legacy; none may be invented (P13, ADV-P2-A20). Legacy also fixes protocol/stdlib constants that are NOT render-state caps, pinned in their owning contracts (scope corrected pass-11 A05): http.client `_MAXHEADERS`=100 / `_MAXLINE`=65536 and urllib `max_repeats`=4 / `max_redirections` (BC-1.04.001 family), the per-call-site JSON depth budgets (interface-definitions §stdin JSON Contract), CPython's 4,300-digit int limits (BC-5.01.002), `window_age.max_depth`=6 (BC-3.02.001). Scope note (pass-5 A13/call 16): the tunable keys `transcript.read_cap_bytes` / `transcript.dedup_memory` / `sparkline.history_cap` additionally carry judgment-call config-VALIDATION upper bounds (67108864 / 65536 / 1000 — interface-definitions.md); these are config range bounds, not new runtime caps, and do not contradict the legacy-cap list | table-verified caps identical to legacy; config-range bounds per the registry | table tests | P1 | legacy equivalence |
| NFR-006 | Security/hygiene | Public-repo hygiene: synthetic committed fixtures only; real inputs only from git-ignored captures/; secret scan clean | gitleaks + category pattern scan clean on every CI leg; the category pattern scan additionally runs nightly and on manual dispatch from `main` against the checked-out `factory-artifacts` ref (a push trigger there is impossible — the ref carries no `.github/`; pass-10 A03/call 16); the local pre-push hook stays the push-time guard | CI leg + scheduled/manual `factory-artifacts` scan job + local pre-push hook + `TestCorpusHygiene` | P0 | policy 21 |

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
CI job sets `HYLO_TIMING_GATE=1`. The other P1 exit conditions are two (pass-10 A09):
OD-149's one clean nightly Tier C differential-fuzz run on all three OSes (30 minutes per
OS, `HYLO_PARITY_FUZZSECONDS=1800`) and OD-158's test-coverage gate (>= 95% for S1/S5,
measured as Go statement coverage; ADV-P11-A03).

**Sampling (defined):** per corpus case, 1 discarded warm-up + 20 timed runs; samples
sorted per case; nearest-rank p95 = 19th of the 20 sorted samples (with 5 samples the
statistic degenerates to the maximum — hence 20). p95 is computed per case and the gate
binds per case; samples are not pooled across cases. Fake-VM handling time is subtracted
per the case model. Timed-run unit and cache/seed state (pass-11 A11/call 16): one timed
run = one full execution of the case's step sequence (every refresh of the case, including
transcript appends, seeded state and any `--subagent` step, wall-clocked end to end), and
caches and seeds are reset to the case's declared state before every run, warm-up
included — cold-start discipline, so the 20 samples measure one identical workload and
no run inherits a predecessor's warm caches.

## Test-coverage gating (OD-158)

The P1 exit gate for the module-critical modules (S1 Status Line, S5 Pyfmt) is
**>= 95% per package**, measured as Go **statement coverage** — Go's `go test -cover`
metric counts statements, not lines (metric name corrected pass-11 A03/call 6). The gate
figure is computed from a merged cross-package profile: the coverage run uses
`-coverpkg=./internal/...`, so a package's percentage counts that package's statements
executed by ANY test binary in the run — Tier B output tests against committed goldens
and the parity-machinery tests DO count toward S1/S5 coverage; only the Tier A
oracle-differential runs are excluded from it. Gate scope is settled by OD-193 (owner
2026-11-18): S1 (`internal/statusline`,
`internal/cost`) and S5 (`internal/pyfmt`) only — `internal/parity` (S6) coverage is
reported, not gated; pass-7 call 12's addition of `internal/parity` to the gate is
withdrawn.
The mutation kill-rate targets in `module-criticality.md` (>= 95% CRITICAL, >= 90% HIGH,
>= 80% MEDIUM) are **Phase 6 targets**, tracked by the formal-verifier; they do not gate
P1.
