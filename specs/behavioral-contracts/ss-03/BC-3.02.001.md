---
document_type: behavioral-contract
level: L3
version: "1.3.4"
status: draft
producer: product-owner
timestamp: 2026-11-17T21:45:00Z
phase: 1a
inputs: [domain-spec/L2-INDEX.md, behavioral-contracts/BC-ALLOCATION.md, semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts-r4.md, semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts.md, semport/hylo-legacy/statusline-target-design.md, owner-decisions-log-2026-11-14.md]
input-hash: "0b9280d"
traces_to: domain-spec/L2-INDEX.md
origin: brownfield
extracted_from: "legacy/dgx_statusline.py"
subsystem: "SS-03"
capability: "CAP-009"
legacy_id: "BC-SL-023"
parity_class: D4-EX-1
confidence: M
lifecycle_status: active
introduced: "0.1"
modified:
  - "1.2.1 2026-11-17T21:45:00Z: patch bump + ADV-P2 pass-2 remediation (owner rulings OD-155..165)"
  - "1.2.2 2026-11-18: ADV-P4 remediation D06/D32/D29 — Windows name comparison folds case after case-insensitive .exe strip; PID-reuse guard rejection = non-matching level (walk continues); fake-ps weekday corrected to Fri"
  - "2026-11-19T01:10:00Z (1.2.3) ADV-P5 remediation D22 — chain-poison refinement: after a PID-reuse guard rejection the walk keeps climbing but accepts no match at or above the rejected level (a stranger's claude can no longer produce a wrong home marker); match-before-rejection legs pinned"
  - "2026-11-19T21:00:00Z (1.3.0): ADV-P8 remediation D09 (orchestrator call 15) — walk rule realigned to the ARCH-05 binding terminate rule: a PID-reuse guard rejection TERMINATES the walk with result None (no climb to the depth cap, no post-rejection probes); table legs respelled (match before rejection; rejection terminates); supersedes the pass-4 D06 walk-continues wording"
  - "2026-11-20T18:30:00Z (1.3.1): ADV-P9 remediation D02+D01 (orchestrator call 7) — Inv 4 respelled: NO unseeded corpus case exists (pass-8 D10 aligned); the probe is exercised by the dedicated Go table tests with a fake process table, never by parity cases; EC-008 states the D4-EX-1 rider-test closure (NO exclusions.json entry)"
  - "2026-11-22T00:00:00Z (1.3.2): ADV-P12 remediation D01 (orchestrator call 2, superseding pass-11 call 2) — Inv 4 and EC-008 restated: every corpus case either seeds proc_start or is cache-003, which probes on NEITHER side (oracle: empty fake PATH raises FileNotFoundError at the ps call, caught SL:293-294; hylo: HYLO_STATUSLINE_WINDOW_AGE_MAX_DEPTH=0, zero probes); the load-time rejection's admission branch is the conditional fake PATH, whose only committed declarer is cache-003; the former 'no P1 corpus case declares the fake process table' universal dissolved"
  - "2026-11-23T00:00:00Z (1.3.3): ADV-P13 remediation A2-04 BC half — the three probe-mechanics VP rows keep VP-014 (whose amended v1.6 statement pins the three walk behaviours jointly with VP-033, so a routed row no longer outruns the verifying statement) alongside VP-033 and the VP-012 frontmatter-closure citation; a fourth VP-014 row + VP-Anchors entry minted for the ruled ⌂ Windows canonical-table pin itself; reciprocity (VP-014 bcs: gains BC-1.02.017) is the architect's half, done in VP-014 v1.6"
  - "2026-11-26T15:00:00Z (1.3.4): pass-14 residual sweep (OD-160 owner id-range alignment): EC-011 minted — a giant exact-int cache proc_start (both signs) is returned as is and the window-age consumer raises OverflowError at SL:558, the CP-C34 register id (co-owner BC-1.02.017); no behavioral change"
deprecated: null
deprecated_by: null
replacement: null
retired: null
removed: null
removal_reason: null
---

# Behavioral Contract BC-3.02.001: Window start via native per-OS ancestor probe; whole-second truncation; proc_start key first

## Description

The process-age window (`⌂`) needs the start time of the client process behind the status line. A numeric
`proc_start` already in the session cache wins; otherwise Go walks up from its parent process with a native per-OS
probe (no `ps` subprocess), takes the first ancestor whose process name is `claude`, truncates its start time to whole
seconds, stores it as a float under `proc_start`, and returns it. Failures return "no start" and are not cached. On
Windows this can show `⌂` where legacy never could: approved deviation **D4-EX-1**.

## Preconditions

1. Stdin `session_id` is truthy (SL:1229: `win_start = claude_window_start(cache_path) if d.get("session_id") else
   None`). With a falsy `session_id` this contract is not invoked and the start is None.
2. The session cache path is `<cache dir>/statusline-<raw sid>.json` (BC-1.06.001, OD-03); it is loaded with the
   never-raise loader (missing or unreadable file gives an empty object).
3. Inputs: `startPID = os.Getppid()`; `maxDepth = statusline.window_age.max_depth` (default 6, legacy T-025, SL:279);
   process name = `statusline.window_age.process_name` (default `claude`, OD-133; D15
   registration of the value legacy hard-coded at SL:285); a `ProcStarter` seam
   (`ProcInfo{PID, PPID, Comm, Start}` per PID) injected for tests.

## Postconditions

1. **Cache first.** If the loaded cache's `proc_start` passes Python `isinstance(x, (int, float))` (int, float, bool,
   NaN, ±Inf included; design IM-02), that value is returned unchanged and no probe runs and nothing is written
   (SL:273-275).
2. **Walk.** Otherwise, with `pid = startPID`, repeat at most `maxDepth` times (SL:279):
   a. Probe `pid`. If the probe fails (process gone, permission denied, unsupported OS) → return None (SL:282-283:
      empty `ps` output returns None immediately; it does not continue).
   b. If `basename(Comm)` equals the configured process name (default `claude`; on POSIX
      exact and case-sensitive; on Windows a trailing `.exe` is first stripped
      case-insensitively and the remainder is then compared case-insensitively — fold —
      so `claude`, `Claude.exe` and `CLAUDE.EXE` all match, ADV-P4-D06) **and** a start
      time is available → `start = float64(floor(Start in Unix seconds))`;
      set `proc_start = start` in the loaded cache object (keeping key order: an existing non-numeric `proc_start`
      keeps its position, a new key is appended last; IM-03), save the whole object with the atomic never-raise
      writer, and return `start` (SL:285-289).
   c. Else `pid = PPID`; if `pid <= 1` → return None (SL:290-292). The start PID is probed
      first, so pid 1 IS examined when it is itself the start PID (`Getppid() == 1`); what
      never happens is descending below it — the walk stops when the next ancestor pid is
      ≤ 1 (SL:290-292).
3. After `maxDepth` non-matching levels → None (SL:295). Any error anywhere in the walk → None (SL:293-294).
4. A None result writes nothing; the walk re-runs on the next refresh (failures are not cached).
5. The stored value is a JSON float with Python repr: `1794615009.0` (never an int, never a fraction), so
   `int(win_ms // 60000)` flips on the same refresh as legacy, whose `ps lstart` has whole-second resolution
   (P3r1 §A7).

## Invariants

1. No subprocess is spawned (D5: no OS tool without a fallback; design IM-19). The
   former inert key `statusline.window_age.ps_timeout_s` was removed by OD-147
   (owner, 2026-11-16); setting it is an unknown setting: ignored with one stderr
   warning, never changing output or exit status (OD-01, BC-2.01.001 PC-6; ADV-P1-D04).
2. Per-OS probe sources (design §2.5): macOS `sysctl kern.proc.pid` (`P_comm`, `Eproc.Ppid`, `P_starttime`) via
   `golang.org/x/sys/unix`; Linux `/proc/<pid>/stat` parsed after the last `)` (comm, ppid, starttime ticks) plus
   `btime` from `/proc/stat`; Windows `CreateToolhelp32Snapshot` + `GetProcessTimes` with a PID-reuse guard (a parent
   created after its child is rejected; ADV-P4-D32 as realigned by pass-8 D09: a guard
   rejection TERMINATES the walk with result None — it is not an error and no further
   candidate is probed). **Chain-poison refinement (ADV-P5-D22):** once a guard rejection occurs, the
   recorded ancestry is untrustworthy (the impostor's PPID may head an unrelated process
   chain, where a stranger's `claude` could match and show a wrong `⌂`); the walk
   TERMINATES immediately with result None (ruled design, ARCH-05's walk rule,
   pass-8 D09 / orchestrator call 15 — it does NOT keep climbing, and it is not an
   error). Matches found strictly BEFORE the rejection already returned at step b, so
   nothing after a rejection is accepted or probed. Never-raise discipline
   unchanged (the poisoned walk is indistinguishable from "no start": nothing written,
   retry next refresh). Table test legs (pass-8 D09 respell): match before rejection
   (returned at the match); guard rejection terminates the walk (None, no further
   probes).
3. The probe never degrades the status line (never-raise helper, design IM-15).
4. Parity runs never depend on a native value: EVERY corpus case either seeds `proc_start` on both sides (design
   §8 row 023 "T, seeded") or is the `temp-file` case `cache-003`, which probes on NEITHER side (pass-12
   call 2: the oracle child's conditional fake `PATH` is an EMPTY `bin` directory, so the
   `ps` subprocess raises `FileNotFoundError` (SL:280-281) caught at SL:293-294 and `claude_window_start`
   returns None, while the hylo child runs at `HYLO_STATUSLINE_WINDOW_AGE_MAX_DEPTH=0`, so `FindAncestor`
   makes zero probes and returns not-found; BC-6.01.002 PC-1). Native values have no oracle. The probe is
   exercised by the
   dedicated Go table tests with a fake process table — the BC-3.02.002 difference table
   (`TestWindowStart_OD76_*`) and the Windows `TestWindowAge_D4EX1_Windows*` legs — never by parity cases. The
   harness rejection remains in force at case-load time (ADV-P2-D12 disposition): a case with an unseeded
   `proc_start` and a truthy `session_id` is rejected unless it declares the conditional fake `PATH`
   (BC-6.02.003 PC-6) — and the only committed case that declares one is `cache-003`, whose Go side needs
   no probe.

## Edge Cases

| ID | Description | Expected Behavior |
|----|-------------|-------------------|
| EC-001 | Cache `proc_start` is `true` | Returned as is (bool passes `isinstance(int)`); no probe. Rendering consequence belongs to BC-1.02.017 |
| EC-002 | Cache `proc_start` is a string (`"x"`) | Not numeric → probe; on success the key is overwritten **in its original position** |
| EC-003 | Cache `proc_start` is `NaN` | Returned as is (NaN passes `isinstance(float)`) |
| EC-004 | Matching ancestor at depth 7 (six non-matching levels first) | None (depth cap 6) |
| EC-005 | Matching ancestor at depth 6 | Found |
| EC-006 | Chain reaches ppid 1 before a match | None, nothing written |
| EC-007 | Ancestor named `Claude` or `claude.exe` on macOS/Linux | No match (case-sensitive; `.exe` strip is Windows-only) |
| EC-008 | **Windows**, ancestor `claude.exe` found | Go returns its start and `⌂` can show; legacy has no `ps` on Windows, catches `FileNotFoundError`, and never shows `⌂`. Approved deviation **D4-EX-1** (D4, design §5.4): OD-105 named difference entry `D4-EX-1`, dedicated table tests `TestWindowAge_D4EX1_Windows*` with a fake `ProcStarter` that returns a start; each excluded case matches its own expected output file. ADV-P9-D01 / orchestrator call 7: NO `exclusions.json` entry exists for `D4-EX-1` — every corpus case either seeds `proc_start` or is `cache-003` (no probe on either side), so no Windows ⌂ case can exist; the id is closed by the rider test alone (BC-6.03.004) |
| EC-009 | Sub-second start (e.g. 1794615009.734) | Stored `1794615009.0` |
| EC-010 | Session cache file is a JSON non-object (e.g. `[]`) | Unreachable here: `effective_rl` degrades first (CP-C01, P3r1 §A7) |\n| EC-011 | Session cache `proc_start` an exact giant integer (magnitude >= 2**1024 - 2**970, both signs; 309..4300-digit literal; passes the SL:274-275 `isinstance(int)` gate; foreign cache, exclusion **OD-160**) | returned as is (exact); the consuming window-age subtraction `(time.time() - win_start) * 1000` (BC-1.02.017's `win_ms`, SL:558) raises OverflowError → the render degrades per DI-008; foreign cached values: CP-C34, OD-160, Go table tests (measured pass-14) |

## Canonical Test Vectors

Fake `ProcStarter`, `startPID = 500`, defaults (`max_depth` 6).

| Input | Expected Output | Category |
|-------|----------------|----------|
| cache `{"rl_ts": 1794615000.0}`; 500 = (`zsh`, ppid 400); 400 = (`claude`, ppid 300, start 1794615009.734) | returns `1794615009.0`; cache bytes `{"rl_ts": 1794615000.0, "proc_start": 1794615009.0}` | happy-path |
| cache `{"proc_start": 1794615009.0}` (probe would fail) | returns `1794615009.0`; file unchanged | happy-path |
| cache `{"proc_start": "x", "a": 1}`; 500 = (`claude`, start 1794615009.0) | returns `1794615009.0`; cache `{"proc_start": 1794615009.0, "a": 1}` | edge-case |
| no cache; chain 500..505 non-matching, 506 = `claude` | None; no file written | edge-case |
| no cache; 500 = (`zsh`, ppid 1) | None; no file written | edge-case |
| no cache; probe of 500 fails | None; no file written | error |
| Windows, fake 500 = (`CLAUDE.EXE`, start 1794615009.2) | returns `1794615009.0` (D4-EX-1 case; legacy None) | edge-case |

Legacy behavior behind rows 1-6 verified 2026-11-15 against CPython 3.11.7 running `claude_window_start` from
`legacy/dgx_statusline.py` with a fake `ps` on `PATH` (`TZ=America/Chicago`, line `400 claude Fri Nov 13 18:10:09
2026` → `1794615009.0`; same cache bytes as rows 1 and 3; depth-6 match found, depth-7 match None; `ps` absent → None).

## Verification Properties

| VP-NNN | Property | Proof Method |
|--------|----------|-------------|
| VP-033, VP-014, VP-012 (frontmatter closure) | A numeric cached `proc_start` short-circuits: zero probe calls, zero writes | unit test with a counting fake |
| VP-033, VP-014, VP-012 (frontmatter closure) | A stored `proc_start` is always integral-valued and serialized with a `.0` suffix | Go property test (testing/quick) over random starts |
| VP-033, VP-014, VP-012 (frontmatter closure) | At most `max_depth` probe calls per refresh | Go property test (testing/quick) over random chains |
| VP-014 | The Windows D4-EX-1 vector row's ruled ⌂ bytes are pinned by this contract's canonical vector table (with BC-1.02.017's), and the rider's expected output is that table's expected column | rider test `TestWindowAge_D4EX1_Windows_AncestorFound` + vector-table parity (VP-014 statement) |

## Traceability

| Field | Value |
|-------|-------|
| L2 Capability | CAP-009 |
| L2 Domain Invariants | DI-008, DI-012 |
| Architecture Module | `internal/platform` `proc.go`, `proc_{darwin,linux,windows,other}.go` (design §2.5) (BC-COMPONENT-MAP: internal/platform/proc.go + proc_*.go (ancestor probe) — ARCH-05) |
| Stories | TBD (filled by story-writer) |
| Source | legacy/dgx_statusline.py:claude_window_start (SL:273-275 cache-first; SL:276-294 ps walk; SL:295) and main (SL:1229) |
| Legacy contract | BC-SL-023 (P3 broad sweep; refined P3r1 §A7; index P3r4 §7.3, tagged D4-EX-1) |
| Decisions | D4 / D4-EX-1 (⌂ on Windows), D5, OD-105 (named exclusion), OD-76 and OD-110 (macOS/Linux differences, BC-3.02.002), OD-03 (raw sid file name), OD-118 (term "process-age window"), OD-133 (process name promoted to `statusline.window_age.process_name`, default `claude`) |

## Related BCs (Recommended)

- BC-3.02.002 — composes with (named macOS/Linux edge differences of the native probe)
- BC-1.02.017 — consumed by (⌂ suffix and its visibility gate)
- BC-1.02.028 — consumed by (window-age duration format)
- BC-1.06.001 — depends on (session cache load/save)
- BC-6.03.004 — related to (exclusion-list machinery for D4-EX-1)

## Architecture Anchors (Recommended)

- `architecture/ARCH-05-platform.md#platform-proc` — internal/platform/proc.go + proc_*.go (ancestor probe) (native ancestor probe) (BC-COMPONENT-MAP: ARCH-05 (ARCH-05-platform.md))

## Story Anchor (Recommended)

TBD — window age (design step S7)

> Names provisional — architect (OD-145): the proposed test names in this contract
> (`TestWindowAge_D4EX1_Windows*`) and any harness flags are delegated to the architect in
> create-architecture, subject to adversarial review. No behavior change.

## VP Anchors (Recommended)

- VP-033, VP-014, VP-012 — cache-first short-circuit, integral `.0` serialization, depth bound (VP-014's amended statement pins the three walk behaviours jointly with VP-033)
- VP-014 — the ruled ⌂ Windows vector bytes (the D4-EX-1 bound's canonical-table pin)

---

### Brownfield-Specific Sections

#### Source Evidence

| Property | Value |
|----------|-------|
| **Path** | `legacy/dgx_statusline.py` (SL:265-295, SL:1229) |
| **Confidence** | medium (legacy semantics high and re-run; native per-OS values have no oracle; design §8 conf M) |
| **Extraction Date** | 2026-11-15 |

#### Evidence Types Used

- **guard clause**: `isinstance(c.get("proc_start"), (int, float))` (SL:274); `if not out: return None` (SL:282-283); `if pid <= 1` (SL:291)
- **assertion**: pinned runs with a fake `ps` (P3r1 §A7; re-run 2026-11-15)

#### Purity Classification

| Property | Assessment |
|----------|-----------|
| **I/O operations** | reads OS process table; reads + writes the session cache |
| **Global state access** | reads process environment (parent pid) |
| **Deterministic** | no (depends on live processes) unless the `ProcStarter` seam is faked |
| **Thread safety** | n.a. (single-shot process) |
| **Overall classification** | effectful shell |

#### Refactoring Notes

`FindAncestor(startPID, name, maxDepth)` is pure over an injected `ProcStarter`; only the per-OS starters touch the OS.
The `ps` + `strptime` + `mktime` path is removed entirely (DET-20 and PR-14 leave this path).
