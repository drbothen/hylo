---
document_type: gene-transfusion-assessment
level: L3
version: "1.6"
status: draft
producer: architect
timestamp: 2026-11-17T22:30:00Z
phase: 1b
inputs:
  - architecture/ARCH-INDEX.md
  - semport/hylo-legacy/semport-assessment.md
  - semport/hylo-legacy/statusline-target-design.md
traces_to: architecture/ARCH-INDEX.md
input-hash: "ac73d2a"

---

# Gene Transfusion Assessment: hylo — P1 (status line)

## Reference frame

The "reference implementation" is hylo's own frozen Python prototype, `legacy/dgx_statusline.py`
(**SL**; `SL:n` = a line in that file), analyzed by the semport corpus:

- Inventory, complexity, translation order and effort: `.factory/semport/hylo-legacy/semport-assessment.md`
  (cited **SA §n**), typed `document_type: gene-transfusion-assessment`, scope P1.
- Idiom map, package layout, purity boundary: `.factory/semport/hylo-legacy/statusline-target-design.md`
  (cited **TD §n**).

"Transfusion" means a semantics-preserving Python→Go port at byte parity (D4): the Go code must
reproduce legacy's observable output on recorded inputs, so a fresh design would have to match
legacy byte-for-byte anyway. Detail lives in SA/TD; this file fixes the **per-package strategy**
that stories will carry as `implementation_strategy` (`gene-transfusion` | `hybrid` | `fresh`),
the reference ranges, and the risks. Scope: the six P1 code packages plus the parity harness
(Subsystem Registry SS-01…SS-06); P2–P4 components are out of scope (SA "Modules Without Candidates").

## Summary

| Metric | Value |
|---|---|
| Modules assessed | 7 P1 packages (SS-01…SS-06) |
| Transfusion candidates | 2 full (`internal/statusline`, `internal/cost`) + 1 semantic (`internal/pyfmt`) + 2 hybrid (`internal/config`, `internal/platform`); 2 fresh (`cmd/hylo`, `internal/parity`) |
| Estimated effort saved (story points) | ≈ **38 SP** (≈ 100 SP from scratch vs ≈ 62 SP transfused, range 50–80; SA §4; 1 SP = 1 ideal engineer-day) |
| Languages involved | Python 3 (CPython 3.11.x oracle, OD-104) → Go ≥ 1.26, standard library first |

Strategy table (headline deliverable; legacy range citations are definitive in SA §1 / TD §2.2):

| Package | SS | Strategy | Reference source (legacy file:function range) | License | Reference test coverage | Key risks |
|---|---|---|---|---|---|---|
| `internal/statusline` | SS-01 | **gene-transfusion** | `legacy/dgx_statusline.py` F2–F9, F11, F12: telemetry+cache I/O SL:156–206; smoothing SL:298–312; sample machine SL:315–359; git SL:362–413; row 1 SL:416–637, 849–873; row 2 SL:640–835; transcript SL:938–1183; width/main/guard SL:1185–1245; subagent panel
SL:837–847, 876–936 (OD-155) | Apache-2.0, same repo (D8) — compatible by construction | 0 tests in-repo (SA §2); Phase 0 oracle corpus substitutes: 103 BCs incl. 63-row `json.dumps` table (BC-SL-096), 20-row turn table (BC-SL-094), 21-row D4-EX-2 table (BC-SL-099), row goldens A/B/C (BC-SL-089), 11-step sample sequence (BC-SL-091), the catalogued crash-path register (error-taxonomy.md: 47 catalogued crash paths as of pass 4 — CP-X01..X04, CP-S01..S17, CP-T01..T07, CP-N01..N03, CP-O01..O11, CP-A01..A05); 100 % line citation coverage | R1 (Python JSON/number semantics), R2 (side-effect order), R3 (FMA on arm64), R4 (hidden exception paths), R5 (Windows), R10 (stdin churn) — SA §5 |
| `internal/cost` | SS-01 | **gene-transfusion** | `legacy/dgx_statusline.py` F3: `record_cost` SL:224–237, `cost_thresholds` SL:240–262, constants SL:217–221 | Apache-2.0, same repo | 0 in-repo; fully pinned goldens: 20-session cost goldens (BC-SL-101), throttle boundary (BC-SL-102), OD-30 string-form key (BC-SL-079) | R1 (float repr/int-vs-float in writes); OD-30 ruled difference bookkeeping (R6) |
| `internal/pyfmt` | SS-05 | **hybrid — semantic transfusion** | Authority is CPython 3.11 stdlib semantics (`round`, `json.dumps`/`loads`, `str`/`repr`, `int`/`float` parse, `//`/`%`, datetime), exercised by legacy call sites SL:72–153, 203, 983, 1061 and pinned by CPython-generated tables (TD §2.6); not a line port of legacy | Apache-2.0 + CPython PSF license (Python stdlib behavior; behavior reproduced, no code copied — no license conflict) | CPython-generated expectation tables per file (gen scripts in `internal/pyfmt/testdata/gen/`), 10,893 naive-time goldens (PR-14), fuzz targets `Decode`/`DumpsLen`/`FromISOFormat`/`ParseFloat` | R1 (decoder breadth: WTF-8, big ints, depth, NaN), R11 (oracle patch drift) |
| `internal/config` | SS-02 | **hybrid** | Defaults and env-grammar behavior transfused from legacy import-time parsing SL:72–100 and render-time `LOCAL_MODEL_PREFIXES` SL:444 (D4-EX-3 boundary, TD IM-16); registry/types/errors fresh from BCs (D15, OD-01/05/57/102) | Apache-2.0, same repo | Threshold register P4r7 §B.2.1 (79 rows) + OD-57 rationales; D4-EX-3 test classes in TD S2 | R8 (D4-EX-3 boundary unspecified), R9 (P1 config source, tension T7) |
| `internal/platform` | SS-03 | **hybrid** | Ancestor-walk semantics transfused from `claude_window_start` SL:265–295 (parent-first, ≤ 6 levels, stop at pid ≤ 1, whole-second truncation); native probes fresh (D4-EX-1 driver; TD IM-19) — no oracle for real probe values | Apache-2.0, same repo | No legacy counterpart (no `ps` on Windows); parity via seeded `proc_start` (BC-SL-023/080); per-OS probe unit tests (TD S7) | R5-adjacent: probe correctness LOW-MEDIUM on Linux (`CLK_TCK`, `node` comm) and Windows (PID reuse); tension T2 difference bookkeeping |
| `cmd/hylo` | SS-04 | **fresh** | None beyond argv tolerance SL:1240 (legacy routes on the exact `--subagent` element anywhere in argv[1:] — the routing test sits at SL:1240, BC-1.07.001 — INCLUDING after a bare `--`, before any flag handling; Go matches: the unknown-flag error line fires for any other `-` argument, a bare `-` is positional, and a bare `--` ends only the flag SCAN — it does not ignore trailing arguments and does not hide `--subagent` from routing, per OD-155/OD-112/BC-4.01.002/BC-1.07.001/VP-002 — pass-2 A2-21 correction, argv-scoping corrected pass-3 A2-02, SL:1238 citation added pass-3 sync, corrected to SL:1240 per sync SC-01 — SL:1238 is the __main__ guard, not the test) | Apache-2.0, same repo | BCs at CLI level (`hylo config validate`/`path`; `statusline` flag-error discipline, golden `cmd/hylo/testdata/usage.golden`) | Minimal; argv tolerance pins BC-4.01.002 EC-003/004/005 |
| `internal/parity` | SS-06 | **fresh** | None — harness is Go-only infrastructure that *drives* legacy via the sitecustomize shim (OD-58); legacy is exercised, not ported (TD §5) | Apache-2.0, same repo | The harness *is* the coverage mechanism (Tiers A/B/C, SA §3–4; OD-104/105) | R4 (Tier C only surfaces P27-class paths), R6 (exclusion-list discipline), R7 (daily-use parity vs OD-101) |

## Candidate analysis (condensed factor tables)

### `internal/statusline` — YES, transfuse

| Factor | Assessment |
|---|---|
| Reference | `legacy/dgx_statusline.py`, post-review version frozen 2026-11-14 (kept runnable until P5, D10) |
| Source / target language | Python 3 (CPython 3.11.x oracle, OD-104) → Go ≥ 1.26 stdlib-first; `golang.org/x/sys` is the one runtime dependency |
| License | Apache-2.0, same owner and same repository (D8) — compatible by construction |
| Test coverage | 0 tests in legacy; Phase 0 corpus substitutes (103 BCs, oracle-pinned tables and goldens listed above) |
| Translation complexity / paradigm gap | HIGH at byte level, LOW-MEDIUM at logic level (SA §2); gap moderate: dynamic dict/JSON values → `pyfmt.Value`, exceptions → `errDegraded` ladder, mutable caches → ordered effect script (TD §3.1) |
| From-scratch vs transfusion effort | ≈ 100 SP vs ≈ 62 SP (dominant share of SA §4) |
| Recommendation | **YES — transfuse** (D4 makes parity the definition of done; Phase 0 corpus already pins expected outputs) |

### `internal/cost` — YES, transfuse

Fully pinned (goldens BC-SL-101/102); smallest surface in P1 (≈ 2.5 SP, SA §4 S6). The P1 scope is
read/record only — `hylo cost backfill` arrives in P6 (OD-36); the seeding tool
`legacy/tools/backfill_cost_history.py` is not ported in P1. Coloring rules stay in
`internal/statusline/cost.go` per TD §2.3.

### `internal/pyfmt` — YES, semantic transfusion (hybrid)

The behavior transfused is CPython 3.11's, not hylo's: legacy proves which semantics are
observable (the 22-pitfall register, SA §2); the API shape is fresh (four files, OD-103; TD §2.6).
Build order is forced: S1 before any widget, because P2–P4 reuse this package (ledger `json.dumps`,
exporter `repr`, hook `str`/`repr` — SA §2 justification). Confidence MEDIUM overall (JSON decoder
breadth), HIGH for num/str/`LocalToUnix`.

### `internal/config` and `internal/platform` — hybrid

Both mix transfused parity-critical behavior with greenfield structure. Config: every default,
comparison operator and rationale is legacy-derived (D15; "defaults equal legacy until cutover"),
while the typed registry, `HYLO_*` grammar (OD-05) and D4-EX-3 error line are spec'd deviations.
Platform: the walk algorithm is legacy-derived; the probes cannot be (legacy shells out to `ps`),
so real-value correctness rests on unit tests, with parity secured through cache seeding.

## Modules without candidates

| Module | Reason |
|---|---|
| `cmd/hylo` (SS-04) | Thin subcommand dispatch; no legacy logic to transfuse beyond argv tolerance (SL:1240) |
| `internal/parity` (SS-06) | New infrastructure; its "reference" is the harness recipe (research Q3a–Q3c), not legacy code |
| `--subagent` rows (SL:837–847, 876–936; BC-SL-097) | PORTED in P1 per OD-155 (owner, 2026-11-17 — supersedes OD-14 (a); Claude Code 2.1.326 restored the setting): `sl/subagent.go`, contracts BC-1.07.001..008, off switch `statusline.subagent.enabled` (default true = legacy). Removed from the fresh/OOS set accordingly |
| Module docstring (SL:1–58) | No code; contract notes already captured in BCs and `docs/STATUSLINE-WIDGETS.md` |
| Remaining `legacy/` components (proxy, exporter, hook, launcher, …) | P2–P4 scope (porting-decision §3); their assessments activate with SS-07…SS-12 |

## Story mapping rule

Stories carry `implementation_strategy` from the table above: the strategy of the package that
owns the story's primary acceptance surface; cross-package stories cite the TD §4 step (S0–S8)
they implement. Any `gene-transfusion` or `hybrid` story must cite its legacy range
(`legacy/dgx_statusline.py:SL:a–b`) and its BC set in the story spec, so the parity harness
exclusion list (OD-105) stays auditable.

## Effort and assumptions

The SA §4 estimate carries over unchanged (62 SP, range 50–80; excludes owner review latency,
tension rulings T1–T10, CI queue time, release tooling). Assumptions 1–4 in SA §4 apply,
amended by later rulings (P12, ADV-P1-A2-18): tensions ruled before S2/S7; CPython 3.11.x
is installed on ALL THREE CI legs (OD-104) — the Windows oracle run writes the
`*.windows.golden` files (update flow with `-update`, BC-6.03.001, ADV-P2-A2-16) and the
OD-149 Tier C nightly runs the oracle on Windows too; and owner daily live use starts at the instant P5
cutover (OD-107, which amends OD-96) — not "after S8 is green".
