---
document_type: behavioral-contract
level: L3
version: "1.3.0"
status: draft
producer: product-owner
timestamp: 2026-11-18T06:25:00Z
phase: 1a
inputs: [domain-spec/L2-INDEX.md, behavioral-contracts/BC-ALLOCATION.md, semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts-r4.md, semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts.md, semport/hylo-legacy/hylo-legacy-pass-5-deep-conventions-r2.md, semport/hylo-legacy/statusline-target-design.md, owner-decisions-log-2026-11-14.md]
input-hash: "7aa5104"
traces_to: domain-spec/L2-INDEX.md
origin: brownfield
extracted_from: "legacy/dgx_statusline.py"
subsystem: "SS-03"
capability: "CAP-009"
legacy_id: "BC-SL-080"
parity_class: OD-76
confidence: M
lifecycle_status: active
introduced: "0.1"
modified:
  - "2026-11-18T00:00:00Z (1.2.1): ADV-P4 remediation D29 — fake-ps weekdays corrected to Fri (2026-11-06 and 2026-11-13)"
  - "2026-11-18T00:00:00Z (1.2.2): pass-5 residual sweep (ADV-P5-B14) — comma inside the flow-list element removed (YAML flow-scalar hazard); no behavioral change"
  - "2026-11-19T04:10:00Z (1.2.3): ADV-P6 remediation D05 / orchestrator call 3 — CTV intro states the D1-D4 difference rows and Chicago-valued vectors are GO TABLE TESTS under TZ=America/Chicago, never parity corpus cases (the corpus validator keeps rejecting non-UTC tz; the OD-76 parity half carries no D1 case)"
  - "2026-11-19T21:00:00Z (1.3.0): ADV-P8 remediation D10 (orchestrator call 16) — all OD-76 D1-D4 vectors are Go table tests; no D1-D4 case is a parity corpus case (corpus stays UTC-only): PC preamble, Inv 2, CTV note and VP row respelled; Pre-3 states the fake-PATH machinery has no P1 consumer (kept for the validator rejection rule and later phases)"
deprecated: null
deprecated_by: null
replacement: null
retired: null
removed: null
removal_reason: null
---

# Behavioral Contract BC-3.02.002: ps-parse replacement: named per-OS edge differences (macOS/Linux)

## Description

Legacy finds the window start by parsing `ps -o ppid=,comm=,lstart=` output with `split(None, 2)`, `strptime` in
the C locale and libc `mktime` (SL:280-286). Go replaces this parse with a native probe (BC-3.02.001). On macOS and
Linux most inputs give the same result; this contract names every input class where the bytes differ, and every
class where they must stay identical. The differences are owner-approved (OD-76 "report the true start", OD-110
named exclusion entry for "OD-76 + the native process probe on macOS/Linux"); D4-EX-1 (Windows) is BC-3.02.001.

## Preconditions

1. OS is macOS or Linux; stdin `session_id` truthy; the session cache has no numeric `proc_start` (otherwise
   BC-3.02.001 postcondition 1 applies identically on both sides).
2. An ancestor within 6 levels is the client process.
3. For parity tests the legacy side runs with a fake `ps` on the harness-constructed
   `PATH` — the constant `<case>/bin`, admitted by BC-6.01.002's conditional `PATH` bullet
   when the case declares a subprocess-fake table — and the Go side with a fake
   `ProcStarter` describing the same process (same pid chain, same true start instant).
   These cases run UNSEEDED (no cached `proc_start`) by design; BC-3.02.001 Invariant 4
   applies to ordinary render-parity cases, not to this difference table
   (ADV-P1-D05 resolution). Pass-8 D10 / call 16: because D1-D4 never run as corpus
   cases, NO P1 corpus case declares a subprocess-fake table — the conditional
   fake-`PATH` machinery of BC-6.01.002 has no P1 consumer; it is kept for the
   validator's rejection rule (BC-6.02.003 PC-6) and later phases.

## Postconditions

Each class below is one row of the named difference table. "Exclusion" rows are cases on the OD-105/OD-110 named
exclusion list under the entry id `OD-76` (native probe, macOS/Linux): their check is ENTIRELY the dedicated Go table
test (proposed name `TestWindowStart_OD76_*`; final name fixed by BC-6.03.004), which requires the Go output to match
the case's own expected-output file — pass-8 D10 / orchestrator call 16: NO D1-D4 case runs as a parity corpus case
(the corpus stays UTC-only; D2-D4 happen to work under UTC, but they never enter the corpus either). "Identical" rows
must pass the ordinary byte comparison.

| # | Input class | Legacy result (SL ref) | Go result | Class |
|---|---|---|---|---|
| D1 | Start wall time in the repeated DST hour where libc `mktime` picks the other occurrence than the real one (macOS libc: `Sun Nov  1 01:59:59 2026`, `TZ=America/Chicago` → second occurrence) | `1793519999.0` (SL:286, libc `mktime`, `tm_isdst=-1`) | the true start, e.g. `1793516399.0` for a process started in the first occurrence | Exclusion (OD-76) |
| D2 | Localized `ps` output (non-C `LC_TIME`, e.g. `Do Nov 13 18:10:09 2026`) | `strptime` ValueError → None, not cached, re-walked every refresh; no `⌂` (SL:286, 293) | start found; `proc_start` cached; `⌂` shown | Exclusion (OD-76) |
| D3 | `comm` contains a space (exec path such as `/opt/App Support/claude`) | `split(None, 2)` gives comm `/opt/App`; `basename` = `App` ≠ `claude`, so this level does not match and the walk continues with the (correct) `ppid`; with no other `claude` ancestor → None (SL:284-292) | native name `claude` matches; `⌂` shown | Exclusion (OD-76) |
| D4 | No `ps` binary, `ps` fails, or `ps` exceeds its 1 s timeout | exception caught → None, not cached (SL:280-281, 293) | start found | Exclusion (OD-76) |
| I1 | Ordinary start outside DST transitions, C-locale `ps` | `mktime(strptime(lstart))` (SL:286) | same epoch (truncated true start) | Identical |
| I2 | Space-padded day (`Fri Nov  6 18:10:09 2026`) | parses (format space matches 1+ whitespace) → `1794010209.0` (Chicago) | `1794010209.0` | Identical |
| I3 | Sub-second true start | `lstart` has whole seconds | truncated to whole seconds (BC-3.02.001) | Identical |
| I4 | Ancestor `comm` is not `claude` (e.g. Linux npm install whose comm is `node`) | no match → None | no match → None | Identical |
| I5 | Process with no start time (`ps` prints no `lstart`, empty `rest`) | no match, walk continues (SL:285) | no start → treated as no match, walk continues | Identical |
| I6 | A pid in the chain has exited (`ps` empty output) | None immediately (SL:282-283) | probe fails → None immediately | Identical |

## Invariants

1. Differences are limited to rows D1-D4; any other observed difference is a defect or needs a new owner ruling,
   never a silent exclusion ("no blanket exclusions", OD-105).
2. Every D-row case has an exclusion entry naming one concrete case and an expected-output file, checked by the
   dedicated Go table test — no D-row case is a parity corpus case (UTC-only corpus, pass-8 D10); no
   globs (OD-105).
3. Linux start = `btime + starttime_ticks / USER_HZ` with integer division (procps computes `lstart` the same way,
   so I1/I3 hold). `USER_HZ` is a named constant, 100, with the rationale "kernel ABI value for `/proc` tick fields on
   amd64 and arm64, the CI architectures"; labeled assumption, checked by the per-OS probe test against the runner's
   `ps -o lstart` for the test's own process.
4. Linux `comm` from `/proc/<pid>/stat` is parsed after the **last** `)` (comm may contain `)` and spaces); it is
   truncated by the kernel to 15 bytes, and `claude` fits.

## Edge Cases

| ID | Description | Expected Behavior |
|----|-------------|-------------------|
| EC-001 | Repeated-hour wall where libc picks the real occurrence (`Sun Nov  1 01:30:00 2026` Chicago → `1793514600.0`, first occurrence, for a process that started then) | Identical (I1 applies); not an exclusion case |
| EC-002 | DST gap: `ps` never prints a wall time inside a gap for a real process | No case; the gap side of PR-14 leaves this path |
| EC-003 | Symlinked install whose executed file name is not `claude` (e.g. a versioned binary behind a `claude` symlink) | **Deferred by owner ruling (OD-139):** the per-OS probe test measures the symlinked-binary case (native `P_comm`/`/proc` comm vs `ps comm`); it becomes an owner ruling only if the measured names differ. Until then no difference class is invented and no exclusion entry exists. Legacy matches `basename` of `ps comm`; macOS `P_comm` and Linux `/proc` comm may name the link target instead |
| EC-004 | Glibc vs macOS libc `mktime` in the repeated hour | D1's legacy value is libc-dependent (macOS measured, L3-12/DET-20); Linux D1 expectations are generated on the Linux runner |

## Canonical Test Vectors

Legacy side: fake `ps` table (`pid|ppid comm lstart`), `startPID = 500`, `TZ=America/Chicago`, no cache.
These vectors — and the D1-D4 difference rows above, including the America/Chicago repeated-DST hour
(D1) and the Chicago-valued I1/I2 epochs — are exercised as GO TABLE TESTS in this package's own test
binary, never as parity corpus cases: the P1 corpus validator rejects a non-UTC `tz` (BC-6.02.003 PC-8,
orchestrator call 3, ADV-P6-D05; pass-8 D10 / call 16 widened it to all four rows), so the
`OD-76` closed-set entry's parity half carries NO D1-D4 case at all and
the corpus stays UTC-only.

| Input | Expected Output | Category |
|-------|----------------|----------|
| `500\|400 claude Fri Nov 13 18:10:09 2026`; Go fake 500 = (`claude`, start 1794615009) | both `1794615009.0`; identical cache bytes `{"proc_start": 1794615009.0}` | happy-path (I1) |
| `500\|400 /x/bin/claude Fri Nov  6 18:10:09 2026`; Go start 1794010209 | both `1794010209.0` | edge-case (I2) |
| `500\|400 claude Sun Nov  1 01:59:59 2026`; Go true start 1793516399 | legacy `1793519999.0`, Go `1793516399.0` → exclusion `OD-76` case, Go output = its expected file | edge-case (D1) |
| `500\|400 claude Do Nov 13 18:10:09 2026`; Go start 1794615009 | legacy None (no file); Go `1794615009.0` | edge-case (D2) |
| `500\|400 /opt/App Support/claude Fri Nov 13 18:10:09 2026`; Go comm `claude` | legacy None; Go `1794615009.0` | edge-case (D3) |
| no `ps` on `PATH`; Go start 1794615009 | legacy None; Go `1794615009.0` | error (D4) |

Legacy column verified 2026-11-15 against CPython 3.11.7 on macOS running `claude_window_start` from
`legacy/dgx_statusline.py` with a fake `ps` (all six rows reproduced). Go column is the contract.

## Verification Properties

| VP-NNN | Property | Proof Method |
|--------|----------|-------------|
| VP-033, VP-012 (frontmatter closure) | For seeded `proc_start`, legacy and Go outputs are byte-identical on every corpus case | parity harness (Tier A) |
| VP-033, VP-012 (frontmatter closure) | Every D1-D4 case has exactly one named exclusion entry and a passing dedicated Go table test; no D1-D4 case is a parity corpus case (UTC-only corpus, pass-8 D10) | harness self-check (BC-6.03.004) |

## Traceability

| Field | Value |
|-------|-------|
| L2 Capability | CAP-009 |
| L2 Domain Invariants | DI-012 (named, tested deviations only) |
| Architecture Module | `internal/platform` `proc_darwin.go`, `proc_linux.go` (design §2.5) (BC-COMPONENT-MAP: internal/platform/proc_*.go (named per-OS edges) — ARCH-05) |
| Stories | TBD (filled by story-writer) |
| Source | legacy/dgx_statusline.py:claude_window_start (SL:276-294; parse at SL:284-286) |
| Legacy contract | BC-SL-080 (new in P3r1 §A7; index P3r4 §7.3) |
| Decisions | OD-76 (DEVIATE: true start, legacy off by 3,600 s in the repeated hour), OD-110 (named exclusion entry "OD-76 + native probe on macOS/Linux" with its own table tests), OD-105 (no blanket exclusions), D4-EX-1 (Windows, BC-3.02.001); design tension T2(b), resolved by OD-110 |

## Related BCs (Recommended)

- BC-3.02.001 — composes with (the native probe this contract constrains)
- BC-6.03.004 — depends on (exclusion-list machinery)
- BC-5.04.002 — related to (`LocalToUnix`; the `mktime` path is removed here, PR-14)

## Architecture Anchors (Recommended)

- `architecture/ARCH-05-platform.md#platform-proc` — internal/platform/proc_*.go (named per-OS edges) (per-OS probe sources) (BC-COMPONENT-MAP: ARCH-05 (ARCH-05-platform.md))

## Story Anchor (Recommended)

TBD — window age (design step S7)

## VP Anchors (Recommended)

- VP-033, VP-012 — differences limited to D1-D4

> Names provisional — architect (OD-145): the proposed table-test names
> (`TestWindowStart_OD76_*`) in this contract are delegated to the architect in
> create-architecture, subject to adversarial review. No behavior change.

---

### Brownfield-Specific Sections

#### Source Evidence

| Property | Value |
|----------|-------|
| **Path** | `legacy/dgx_statusline.py` (SL:276-294) |
| **Confidence** | medium (legacy side re-run; native correctness on Linux and symlinked installs unverified; design §8 conf M) |
| **Extraction Date** | 2026-11-15 |

#### Evidence Types Used

- **guard clause**: `if os.path.basename(comm) == "claude" and rest` (SL:285); `except Exception: return None` (SL:293-294)
- **assertion**: pinned runs (P3r1 §A7, P5r2 §A.1 DST table; re-run 2026-11-15)
- **inferred**: Linux `lstart` derivation from procps (I1/I3), pending the per-OS probe test

#### Purity Classification

| Property | Assessment |
|----------|-----------|
| **I/O operations** | reads OS process table |
| **Global state access** | none beyond the process table |
| **Deterministic** | no (live processes) unless faked |
| **Thread safety** | n.a. |
| **Overall classification** | effectful shell |

#### Refactoring Notes

No parse remains in Go. The process name is the configured `statusline.window_age.process_name`
(default `claude`, OD-133), passed into `FindAncestor` as a parameter.
