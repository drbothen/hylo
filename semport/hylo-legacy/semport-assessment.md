---
document_type: gene-transfusion-assessment
level: L3
version: "1.0"
status: draft
producer: codebase-analyzer (semport-analyze, Phase 2, scoped)
timestamp: 2026-11-15T00:00:00
phase: 1b
scope: "P1 only — the status line module (legacy/dgx_statusline.py), minus --subagent (OD-14)"
inputs:
  - statusline-target-design.md
  - hylo-legacy-pass-8-deep-synthesis.md
  - hylo-legacy-pass-3-deep-behavioral-contracts-r4.md
  - hylo-legacy-pass-4-deep-nfr-r7.md
  - hylo-legacy-pass-5-deep-conventions-r3.md
  - brownfield/porting-decision.md
  - specs/owner-decisions-log-2026-11-14.md
  - specs/research/general-go-port-parity-crossplatform-2026-11-14.md
traces_to: semport/hylo-legacy/statusline-target-design.md
input-hash: "d55c415"
---

# Gene Transfusion Assessment: hylo — P1 status line (`hylo statusline`)

Scoped to P1 (porting-decision §1, §4). The "reference implementation" is hylo's own frozen prototype module
`legacy/dgx_statusline.py`, and "transfusion" means a semantics-preserving Python-to-Go port at byte parity (D4). All
detail lives in the companion plan, `statusline-target-design.md` (cited **TD §n**). Line citations are `SL:n` in
`legacy/dgx_statusline.py`.

## Summary

| Metric | Value |
|---|---|
| Modules assessed | 1 module (`legacy/dgx_statusline.py`, 1,245 lines, 742 statements; pass-8 §5 rank 2), decomposed into 13 function families (§1) |
| Transfusion candidates | 12 families port. 1 family is not ported (`--subagent`, OD-14) |
| Estimated effort saved (story points) | about **38 SP** saved against a from-scratch rewrite to the same parity bar: about 100 SP from scratch versus about **62 SP** to transfuse (1 SP = 1 ideal engineer-day; assumptions in §4) |
| Languages involved | Python 3 (CPython 3.11.x oracle, OD-104) → Go (go.mod `go 1.26.0`, `toolchain go1.27.4`) |

## 1. Module inventory (function families)

LOC are physical source lines from the function boundaries in `legacy/dgx_statusline.py`. BCs come from the P3r4 §7.3
index.

| # | Family | Source lines | LOC | BCs | Go home (TD §2) | Port? |
|---|---|---|---|---|---|---|
| F1 | Tunables, primitives, palette, query | SL:72-153 | 82 | 004, 056, 087 (+ config rows T-001..T-064) | `internal/config`, `statusline/theme.go`, `width.go`, `context.go` | yes (env parsing → typed config, D4-EX-3) |
| F2 | VictoriaMetrics fetch + cache I/O | SL:156-206 | 51 | 040, 052, 078 | `statusline/telemetry.go`, `cache.go` | yes |
| F3 | Cost history | SL:209-262 | 54 | 028, 029, 079, 101, 102 | `internal/cost/history.go` | yes |
| F4 | Window start (⌂, `ps` walk) | SL:265-295 | 31 | 023, 080 | `internal/platform/proc_*.go` | yes, rewritten as a native probe (D4-EX-1) |
| F5 | Rate-limit smoothing | SL:298-312 | 15 | 018, 093 | `statusline/limits.go` | yes |
| F6 | Sample state machine | SL:315-359 | 45 | 041, 042, 091, 092 | `statusline/sample.go` | yes |
| F7 | Git branch + cache | SL:362-413 | 52 | 009, 010 | `statusline/git.go` | yes |
| F8 | Row 1 (`fmt_ctx`, `render_lane`) + `_fmt_lines`/`_fmt_tok_c` | SL:416-637, 849-873 | 247 | 006-008, 011, 013-017, 019-022, 024-027, 057-064, 081-083 | `statusline/{lane,context,limits,session,tokens,cost}.go` | yes |
| F9 | Row 2 (sparkline, telemetry fields) | SL:640-835 | 196 | 043-051, 073-075, 084-086 | `statusline/{row2,sparkline}.go` | yes |
| F10 | `--subagent` rows | SL:837-847, 876-936 | 64 | 097 | — | **no** (OD-14) |
| F11 | Transcript parser + composition labels | SL:938-1183 | 246 | 012, 030-039, 065-072, 088, 094-096, 098-100, 103 | `statusline/transcript*.go`, `mixcache.go`, `context.go` | yes (with D4-EX-2) |
| F12 | Width, trim, `main`, guard | SL:1185-1245 | 61 | 001-003, 005, 053-055, 076, 077, 089, 090 | `statusline/{width,statusline,guard,input}.go` | yes |
| F13 | Module docstring (contract notes) | SL:1-58 | 58 | — | `docs/` (reference) | no code |

All 103 BCs are mapped one by one in TD §8. Parity class after the owner rulings: BX 96 · D4-EX-2 4 · D4-EX-3 1 · OD-30
difference 1 · OOS 1.

## 2. Candidate analysis

### Status line (F1-F9, F11, F12)

| Factor | Assessment |
|---|---|
| Reference | `legacy/dgx_statusline.py`, the post-review version frozen 2026-11-14 (RESUME "How we got here"; D10 keeps it runnable until P5) |
| Source language | Python 3; the oracle is CPython 3.11.x, an explicit harness setting (OD-104) |
| Target language | Go ≥ 1.26, standard library first; `golang.org/x/sys` is the one runtime dependency (window-age probe; research Q5) |
| License | Apache-2.0 (D8). Same owner and same repository, so it is compatible by construction |
| Test coverage | **0 tests in legacy** (pass-8 §2.8). Phase 0 compensates with **103 BCs**, most with oracle-pinned examples: the 63-case `json.dumps` table (BC-SL-096), the 20-row turn table (BC-SL-094), the 21-row D4-EX-2 table (BC-SL-099), the 20-session cost goldens (BC-SL-101), row goldens A/B/C (BC-SL-089), the 11-step sample sequence (BC-SL-091), 10,893 naive-time goldens (PR-14), and 43 catalogued crash paths. Line-level citation coverage is 100 % (pass-8 §9.3) |
| Last maintained | frozen 2026-11-14 after a 21-widget owner review with about 30 fixes (docs/STATUSLINE-REVIEW-2026-11-13.md; RESUME) |
| Known vulnerabilities | none applicable. No listener. One outbound GET to a configured metrics URL over plain HTTP by default (SL:73; T-005). sha1 is used only as a cache-file name, not for security (SL:405; research Q6). Cache files are written 0600 (mkstemp) |
| Translation complexity | **HIGH** at the byte level; **LOW-MEDIUM** at the logic level. 137 of 232 BCs program-wide (96 of the status line's 103) are byte-exact and depend on Python semantics Go does not share: banker's `round`, `json.dumps` bytes, code points, NaN `max`/`min`, naive local time, FMA (22 pitfalls; pass-8 §1 finding 1; market-intel R3). The logic itself is a pure-ish function of stdin, transcript, metrics and caches (PLAN §7 P1 "lowest risk") |
| Paradigm gap | **moderate.** Dynamic `dict`/JSON values with Python truthiness and `isinstance` (bool counts as int) → an ordered `pyfmt.Value` model (TD IM-01/02). Exceptions as control flow (43 crash paths, sticky states) → `errDegraded` plus per-site predicates (TD IM-15). Mutable caches re-read within one run → an ordered effect script (TD §3.1). No generators, decorators, metaprogramming or concurrency |
| Estimated from-scratch effort | about **100 SP** (judgment: without the Phase 0 corpus, each of about 140 boundary behaviors would have to be rediscovered against the oracle, and the 43 crash paths, sticky states and cache-format rules found by fuzzing and diffing) |
| Estimated transfusion effort | about **62 SP** (range 50-80; §4) |
| Recommendation | **YES — transfuse** (port in place at byte parity; D4) |
| Justification | D4 makes parity the definition of done, so a fresh design would still have to match legacy byte for byte. The Phase 0 corpus already pins the expected outputs. The module is the lowest operational-risk phase (PLAN §7) and creates the shared helpers that P2-P4 reuse: `internal/pyfmt` (ledger `json.dumps`, exporter `repr`, hook `str`/`repr`) and `internal/config` (D15 registry) |

### Complexity rating per family

| Family | Rating | Driver |
|---|---|---|
| F11 transcript parser | **HIGH** | 156-line stateful `_mix_counts` (pass-8 §2.9). Decoder edges (BOM, invalid UTF-8, NaN, depth, big ints) flow into the counts. Ordered mix-cache format with a raw `cur.out`. Turn machine. D4-EX-2 W-predicates with no partial mutation |
| F8 row 1 | **MEDIUM-HIGH** | about 25 widgets and many boundary rules: float `divmod`, half-even vs half-up, `repr` of non-str labels, FMA in `heat` and the ⌂ gate, 13 stdin crash paths |
| F1 config | **MEDIUM** | about 62 CFG keys with rationale and operator (CV-19); typed validation; the D4-EX-3 line; the OD-101 path exception |
| F6 sample state + F2 fetch | **MEDIUM** | inherited key order in the session cache; the catch-list subtlety (a `TypeError` drops the whole sample, SL:179 vs SL:186) |
| F4 window age | **MEDIUM** | three native probes with no oracle for their real values (parity relies on seeding) |
| F9 row 2 | **LOW-MEDIUM** | formatting plus two NaN crash paths, all pinned |
| F3 cost history | **LOW-MEDIUM** | fully pinned goldens; percentile index rule; OD-30 string-form key |
| F5, F7, F12 | **LOW** | small, pinned, mechanical |

## 3. Recommended translation order

From TD §4 (RESUME P1 step 5; market-intel R3). The harness grows in parallel from S0.

| Step | Content | BCs | Confidence |
|---|---|---|---|
| S0 | skeleton, CI on 3 OSes with CPython 3.11 from day one | — | HIGH |
| S1 | `internal/pyfmt` (`num.go`, `json.go`, `str.go`, `time.go`) with CPython-generated tables and fuzz | 067, 069, 071, 096 + helper halves | MEDIUM (JSON decoder breadth); HIGH for num/str/`LocalToUnix` |
| S2 | frame: config subset + D4-EX-3 + `config validate`, guard, stdin, width/trim, `CacheStore`, orchestrator, `Env` seams | 001-005, 052, 054, 055, 076, 077, 078, 087, 090 | HIGH |
| S3 | row-1 widgets + rate-limit smoothing | 006-022, 024-027, 056-064, 081-083, 093 | HIGH (017/022/058/059 MEDIUM) |
| S4 | transcript parser + mix cache + D4-EX-2 | 030-039, 065-072, 088, 094-096, 098-100, 103 | MEDIUM |
| S5 | row 2 + metrics client + session cache | 040-051, 053, 073-075, 084-086, 091, 092 | HIGH (040/091 MEDIUM) |
| S6 | cost history (`internal/cost`) + `$`/`$/h` coloring | 028, 029, 079, 101, 102 | HIGH |
| S7 | window age (`internal/platform`, 3 OSes) | 023, 080 | MEDIUM |
| S8 | goldens A/B/C, full corpus on 3 OSes, Tier C nightly | 089, 090, 077 | MEDIUM |

## 4. Effort estimate

**Unit.** 1 SP = 1 ideal engineer-day: focused time for one developer fluent in Go and already familiar with the Phase 0
corpus. **Includes** table tests, goldens and per-step harness work. **Excludes** owner review latency, the rulings on TD
§7.1 tensions, CI queue time, and release tooling (D12; not P1-gating).

| Work item | SP | Basis |
|---|---|---|
| S0 skeleton + CI | 2 | research Q7 recipe |
| S1 `pyfmt`: num 2.5, json 4.5, str 1.5, time 2.5, generators and fuzz 2 | 13 | the 22-pitfall register; the JSON decoder/encoder is the largest single piece |
| S2 config subset (≈ 62 CFG keys + toggles, glyphs, paths, with rationale text) + D4-EX-3 + frame | 7 | P4r7 §B.2.1, OD-57 rationales already written |
| S3 row-1 widgets | 6 | 33 BCs, mostly pinned |
| S4 transcript parser + D4-EX-2 | 7 | 22 BCs (067 shared with S1); 21-row and 20-row tables already derived |
| S5 row 2 + metrics client + session cache | 5 | 21 BCs |
| S6 cost history | 2.5 | goldens pinned (BC-SL-101/102) |
| S7 window age, three OS probes + `CacheDir` | 4 | research Q4a: 80-150 lines per OS |
| H harness: shim, case runner, settings translation, fake VictoriaMetrics, transcript generator, cache-swap, exclusion list, Tier A/B (8); Tier C (2.5) | 10.5 | research Q3a-Q3c; OD-58, OD-104, OD-105 |
| S8 goldens + cross-OS burn-down + review-rule table sweep | 5 | Windows path/stdio/rename issues; hidden exception paths |
| **Total** | **62** | range **50-80** (−20 % / +30 %, a judgment call: the high side covers JSON-decoder surprises and Windows CI) |

Assumptions:

1. Tensions T1-T10 are ruled before S2 (config domain, prefix default, P1 config source) and before S7 (the macOS/Linux
   probe differences).
2. CPython 3.11 is available on all three CI images.
3. No VictoriaMetrics capture is needed beyond the synthetic DTU-3 (the NaN paths are latent in production, P3r7).
4. Owner daily use (OD-96) starts once S8 is green; it is not counted here.

## 5. Risk areas

| # | Risk | Severity | Where it bites | Mitigation |
|---|---|---|---|---|
| R1 | Python JSON/number semantics (WTF-8 strings, big ints, NaN tokens, ordered dicts, depth) mis-ported → every cache byte and many counts differ | HIGH | F2, F3, F6, F11 | S1 first with CPython tables + fuzz; cache-swap tests (TD IM-01/03) |
| R2 | Side-effect order on degraded runs (a crash at step k keeps writes 1..k-1) | MEDIUM | F12 orchestration | ordered effect script, cache comparison after every step (TD §3.1; BC-SL-077) |
| R3 | FMA contraction changes truecolor bytes or the ⌂ gate on arm64 only | MEDIUM | `heat` SL:146-147, SL:558-559 | explicit `float64()`; macos-15 arm64 gating leg (PR-15, CONV-ABS-77) |
| R4 | Hidden exception paths beyond the 43-path catalogue (research P27) | MEDIUM | all | Tier C nightly; `recover` backstop |
| R5 | Windows: sharing violations on rename, `ntpath`, `TZ` ignored by Go, the stdio shim | MEDIUM | F2, F7, F8, F11 | retries + swallow; `*.windows.golden`; explicit `Loc` table tests |
| R6 | Approved-difference bookkeeping: byte differences outside D4-EX-1/2/3 (OD-30, OD-76 / native probe on macOS/Linux, temp cleanup) collide with OD-105's "no blanket exclusions" | MEDIUM | harness | owner ruling on TD tension T2 |
| R7 | P1 daily-use parity broken by the separate hylo cache dir and an empty cost history (OD-96 vs OD-101/OD-106) | MEDIUM | F3 coloring | owner ruling on TD tension T1 |
| R8 | D4-EX-3 boundary unspecified (which legacy-accepted env values become config errors) | MEDIUM | F1 | registry spec states each key's domain (TD tension T10) |
| R9 | P1 config source: no YAML in the P1 dependency budget vs the owner's real telemetry URL | LOW-MEDIUM | F1, owner rollout | owner ruling on TD tension T7 |
| R10 | Claude Code stdin churn | MEDIUM | F8 | newer-optional-field fixtures (market-intel §6.1); defensive `Value.Get` |
| R11 | Oracle patch drift (3.11.x vs production 3.11.7) | LOW | goldens | record the patch in golden metadata |

## Modules Without Candidates

| Module | Reason |
|---|---|
| `--subagent` rows (SL:837-847, 876-936; BC-SL-097) | not ported: OD-14 ruling; Claude Code 2.1.323 removed `subagentStatusLine` (PLAN §3 non-goal). Flag handling is still a spec item (TD tension T8) |
| `tools/backfill_cost_history.py` (cost-history seeding) | out of P1 scope: OD-36 schedules `hylo cost backfill` for P6; P1 ports only the status line's read/record side (porting-decision §4.5) |
| Module docstring (SL:1-58) | no code; its contract notes are already captured in the BCs and docs/STATUSLINE-WIDGETS.md |
| Other `legacy/` components (proxy, exporter, hook, launcher, preflight, coordinator, services) | out of P1 scope (porting-decision §3; P2-P4) |
