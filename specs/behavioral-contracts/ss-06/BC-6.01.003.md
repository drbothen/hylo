---
document_type: behavioral-contract
level: L3
version: "1.2.6"
status: draft
producer: product-owner
timestamp: 2026-11-18T01:42:00Z
phase: 1a
inputs:
  - domain-spec/L2-INDEX.md
  - domain-spec/invariants.md
  - behavioral-contracts/BC-ALLOCATION.md
  - semport/hylo-legacy/statusline-target-design.md
  - semport/hylo-legacy/hylo-legacy-pass-5-deep-conventions-r3.md
  - research/general-go-port-parity-crossplatform-2026-11-14.md
  - owner-decisions-log-2026-11-14.md
input-hash: "08ebff4"
traces_to: domain-spec/L2-INDEX.md
origin: greenfield
extracted_from: "n.a. (new contract, no legacy source)"
subsystem: "SS-06"
capability: "CAP-009"
legacy_id: "new"
parity_class: "n.a."
confidence: "—"
lifecycle_status: active
introduced: "0.1"
modified:
  - "2026-11-18T01:42:00Z ADV-P3 remediation D23+D10: shim contract lists the UTF-8/newline stdio reconfigure duty with a gating canary leg; tenth clock read SL:889 added to stepped read sites"
  - "2026-11-18T22:00:00Z (1.2.2) ADV-P4 remediation D24+D28 - HYLO_TEST_NOW grammar authority minted here (decimal regex + finite + time.Time range; runtime surpluses rejected); read-site count reconciled to ten (adds SL:889)"
  - "2026-11-19T00:05:00Z (1.2.3) ADV-P5 remediation D02+D19 — the parsed float64 IS the frozen time.time() value, never round-tripped through time.Time ns (owner call 7); grammar range fixed to the asymmetric epoch-seconds span [-62135596800, 253402300799] (D19); shim N anchored to the Pre-3 grammar; canary instant strengthened to the round-trip-discriminating 1794615009.4245193"
  - "2026-11-19T02:00:00Z (1.2.4): sync-check adv-p5 closure (SC-20) — modified history re-ordered chronologically; no behavioral change"
  - "2026-11-19T03:15:00Z (1.2.5): ADV-P6 remediation D11 — canonical vector row 1 realigned to PC-4's strengthened canary instant 1794615009.4245193 (exact stdout); the superseded 1794615009.5 value stays only as EC-004's fractional-grammar case"
  - "2026-11-19T21:00:00Z (1.2.6): ADV-P8 remediation D24 — stdio canary fixture respelled a non-ASCII code point (U+0664, UTF-8 D9 A4) and the probe script specified (testdata/clock_shim/stdio_canary.py, name per OD-145 delegation)"
deprecated: null
deprecated_by: null
replacement: null
retired: null
removed: null
removal_reason: null
---

# Behavioral Contract BC-6.01.003: Clock shim freezes time functions from HYLO_TEST_NOW, stepped per refresh; canary fails if shim absent

## Description

A `sitecustomize.py` shim on the oracle's `PYTHONPATH` replaces `time.time`, and the
default-argument forms of `time.strftime`, `time.localtime` and `time.gmtime`, with
versions that read the frozen instant from `HYLO_TEST_NOW` (OD-58 mode 1). The Go side
reads the same instant through `Env.Now`; the built binary honors `HYLO_TEST_NOW`. The
harness sets one instant per refresh step, so all ten `time.time()` reads within a
refresh see the same value. CPython swallows exceptions raised in `sitecustomize`, and
`-I`/`-E`/`-S` skip the shim without any error. A canary therefore proves, before any
oracle case runs, that the shim actually took effect.

## Preconditions

1. The shim file is `internal/statusline/testdata/pyhooks/sitecustomize.py`. It is
   stdlib-only, about 10 lines, and lives outside `legacy/` (D10). Besides the clock
   patches it performs the stdio reconfiguration assigned in BC-6.01.002 PC-4:
   `sys.stdin` and `sys.stdout` are reconfigured to UTF-8 strict with `newline="\n"`
   on import (ADV-P3-D23; relied on by BC-6.03.002 EC-006).
2. The oracle runs with `-s` and the env of BC-6.01.002, which sets `PYTHONPATH` to the
   shim directory and `HYLO_TEST_NOW` to the step instant.
3. `HYLO_TEST_NOW` is a decimal string produced by the harness with
   `strconv.FormatFloat(now, 'f', -1, 64)`. **Grammar authority (ADV-P4-D24; mirrored by
   BC-5.04.003 Pre-2):** a value is WELL-FORMED iff it matches
   `^[+-]?[0-9]+(\.[0-9]*)?([eE][+-]?[0-9]+)?$`, parses to a finite float64, and lies
   within the `time.Time` representable range expressed in epoch seconds,
   `-62135596800 ≤ s ≤ 253402300799` (year 1 .. year 9999; asymmetric about the 1970
   epoch — ADV-P5-D19 disposes the previously contradictory single-span statement); values
   like `1e300` are malformed. Both shims implement this split identically, rejecting each
   runtime's surplus: the Go shim does NOT accept `strconv.ParseFloat`'s extras (`inf`,
   `NaN`, hex floats like `0x1p3` are malformed), and the Python shim's `float()` surplus
   (surrounding whitespace, `_`, `nan`/`inf` spellings) is likewise malformed. Both sides
   get the identical float64 for every well-formed value (correct decimal rounding,
   research P20). **The parsed float64 IS the frozen `time.time()` value** (ADV-P5-D02,
   owner call 7): it is used directly and is never round-tripped through `time.Time`
   nanoseconds (float64 spacing at 1.79e18 ns is 256 ns; the owner measures ~17% of random
   fractional instants drifting under such a round trip, which would fork the frozen
   `rl_ts`/`ts`/`fetch_ts` repr bytes).

## Postconditions

1. **Frozen functions** (shim, on import). Let `N` be the float64 obtained by parsing
   `HYLO_TEST_NOW` under precondition 3's grammar (the well-formed/malformed split,
   implemented identically by both shims; the harness env builder guarantees
   well-formedness, EC-003) — read when each patched function is called:
   - `time.time()` returns `N`;
   - `time.localtime()` with no argument or `None` returns `<real localtime>(N)`;
   - `time.gmtime()` with no argument or `None` returns `<real gmtime>(N)`;
   - `time.strftime(fmt)` with no tuple returns `<real strftime>(fmt, <real localtime>(N))`.
   Calls that pass an explicit argument are forwarded unchanged. `time.mktime` and
   `time.strptime` are not patched: they run only on the `ps` path (SL:286), which the
   seeded `proc_start` bypasses (design §3.2).
2. **Stepped per refresh.** For step `k` of a case the harness sets
   `HYLO_TEST_NOW = now_k` for both the oracle and Go runs of that step.
   - Within one oracle process every `time.time()` read returns `now_k`. The read sites
     are SL:231, 243, 304, 322, 408, 499, 558, 825, 826 and 889 (the last: the subagent
     renderer's `now_ms`, ADV-P3-D10; it only runs under `--subagent` cases).
   - Between steps the value changes only by the case's step schedule (BC-6.02.002,
     BC-6.02.003).
3. **Go side.** The in-process render receives `Env.Now = now_k` (float seconds; ADV-P5-D02).
   The built binary parses `HYLO_TEST_NOW` once at start into a float64 — which IS the
   frozen `time.time()` value for every clock read of that refresh, never converted
   through `time.Time` nanoseconds (owner call 7). A malformed value (not a valid decimal float) is ignored with exactly one
   stderr warning and the real clock is used — never a config error, never a degraded
   line (spec choice, ADV-P1-D22; mirrors the unknown-`HYLO_*` warning discipline of
   BC-2.01.001 PC-6; echoed in BC-5.04.003 and BC-2.01.001). `HYLO_TEST_NOW` is a test
   hook, not a D15 config key; it is documented under
   "test hooks" in the config reference (design §3.2, risk RK-5).
4. **Canary (gating).** Before the first oracle case of every Tier A run, the harness
   runs `<python> -s -c "import time; print(repr(time.time()))"`. It uses the same
   interpreter and env builder, with `HYLO_TEST_NOW=1794615009.4245193` (strengthened per
   ADV-P5-D02: a fractional instant whose repr changes under a `time.Time` ns round trip —
   `1794615009.4245193` becomes `1794615009.4245195` — so the canary also discriminates the
   frozen-value round-trip the plain `.5` value hid).
   - Stdout must equal exactly `1794615009.4245193\n`.
   - On any other output the run fails, not skips, with
     `parity: clock shim not loaded (OD-109 canary): got "<stdout>"`. No oracle case runs.
   - A second canary leg proves the stdio duty (ADV-P3-D23): the harness feeds the probe
     a non-ASCII CODE POINT — `\u0664` (U+0664 ARABIC-INDIC DIGIT FOUR, UTF-8 `D9 A4`; the
     sibling example of BC-2.02.001 EC-008; pass-8 D24: a lone byte \u2265 0x80 is not valid
     UTF-8, so the fixture is the encoded code point, not a "non-ASCII byte") — through
     stdin and reads stdout as raw bytes; with the shim loaded, a `\r\n`-free,
     UTF-8-strict round trip is observed (the probe prints the decoded code point back,
     UTF-8-encoded, `newline="\n"`). The probe script is the harness's stdio canary,
     `testdata/clock_shim/stdio_canary.py` — it reads stdin as strict UTF-8 text
     (CPython default), prints the first code point, exits 0 (proposed name, settled by
     the implementer per the OD-145 delegation). Failure leg message:
     `parity: stdio shim not loaded (ADV-P3-D23 canary): got "<raw bytes>"`. No oracle
     case runs on failure.
5. **Canary negative control.** A table test runs the same canary probe with `-I`
   instead of `-s`, and separately with `PYTHONPATH` removed. Each must be reported as
   "shim not loaded". This proves the canary can discriminate.

## Invariants

1. Every oracle refresh runs with the shim loaded. Any change that could drop it
   (`-I`, `-E`, `-S`, a lost `PYTHONPATH`, a shim exception) is caught by the canary,
   not by a later byte diff.
2. The harness never uses the real wall clock to produce a value a comparison depends
   on.

## Edge Cases

| ID | Description | Expected Behavior |
|----|-------------|-------------------|
| EC-001 | Shim raises at import (e.g. syntax error) | CPython prints `Error in sitecustomize; set PYTHONVERBOSE for traceback:` to stderr and continues on the real clock (observed on a local CPython 3.9.6; same `site.py` logic in 3.11; not re-run on 3.11 in this stage). The canary sees a real-clock value and fails the run |
| EC-002 | Oracle invoked with `-I` | The shim is silently skipped (observed locally: exit 0, no stderr). Canary fails; the argv test of BC-6.01.001 also fails |
| EC-003 | `HYLO_TEST_NOW` missing from an oracle step env | `time.time()` raises `KeyError` inside legacy `main()`; the guard prints `statusline degraded` (SL:1238-1245); the byte comparison fails. The env builder's unit test forbids this state |
| EC-004 | Fractional instant `1794615009.5` | Both sides get float64 `1794615009.5`; `repr` prints `1794615009.5` |
| EC-005 | Two steps with the same instant | Allowed. Both refreshes see the same `N`; TTL logic sees zero elapsed time |
| EC-006 | Windows oracle under the shim | The shim loads the same way; the canary runs on all three OSes (BC-6.04.001) |

## Canonical Test Vectors

| Input | Expected Output | Category |
|-------|----------------|----------|
| Canary probe, `-s`, `HYLO_TEST_NOW=1794615009.4245193`, shim present | stdout `1794615009.4245193\n`; harness proceeds (PC-4's round-trip-discriminating canary; ADV-P6-D11) | happy-path |
| Step `k` with `now_k = 1794615009` and a case whose limits countdown depends on `now` | Oracle and Go both render the countdown computed from `1794615009.0` (e.g. golden A `->2h41m` for `resets_at = NOW+9690`, BC-6.03.001) | edge-case |
| Canary probe with `-I` (negative control) | Reported "shim not loaded"; the negative-control test passes because it was detected | error |
| Shim file containing `raise RuntimeError` | Canary FAIL: `parity: clock shim not loaded (OD-109 canary): got "<real time>"` | error |

## Verification Properties

| VP-NNN | Property | Proof Method |
|--------|----------|-------------|
| VP-034 | With the shim loaded, `time.time()` == `float(HYLO_TEST_NOW)` for every read within one oracle process | canary + table test over several instants |
| VP-034 | The canary fails whenever the shim is not active (`-I`, `-E`, `-S`, missing PYTHONPATH, shim exception) | negative-control table test |
| VP-034 | Python `float(s)` and Go `ParseFloat(s, 64)` agree on every harness-formatted instant | table test (shortest round-trip formatting) |

## Traceability

| Field | Value |
|-------|-------|
| Source | OD-58 (extended clock shim, mode 1 frozen P1-P3); OD-109 (`-s` never `-I`; canary fails the harness if the shim did not load); design §3.2 "Clock" row (freezes `time.time`, `time.strftime`, `time.localtime`, `time.gmtime` from `HYLO_TEST_NOW`, stepped between refreshes); P5r3 §B.3 DET-01..08, DET-15..18; research P20 (decimal string parsed by both sides); the TEN legacy read sites `legacy/dgx_statusline.py` SL:231, 243, 304, 322, 408, 499, 558, 825, 826, 889 (reconciled with PC-2's list and legacy's grep, ADV-P4-D28) |
| Parity class | n.a. (harness machinery) |
| L2 Capability | CAP-009 |
| L2 Domain Invariants | DI-012 |
| Architecture Module | `internal/statusline/testdata/pyhooks/sitecustomize.py`; `statusline.Env.Now` (BC-COMPONENT-MAP: internal/parity/shim_canary.go + internal/statusline/testdata/pyhooks/sitecustomize.py — ARCH-07) |
| Stories | TBD (filled by story-writer) |

> Capability anchor rationale (OD-153): the parity harness is verification machinery whose sole purpose is proving CAP-009 byte parity (the D4 exit criterion), governed by DI-012.

## Related BCs (Recommended)

- BC-6.01.001 — depends on: `-s` invocation keeps the shim on `PYTHONPATH`
- BC-6.01.002 — depends on: env builder sets `PYTHONPATH` and `HYLO_TEST_NOW`
- BC-6.02.002 — composes with: per-step clock advance for captured-session replay
- BC-6.02.003 — composes with: case `now` and step schedule

## Architecture Anchors (Recommended)

- `architecture/ARCH-07-parity-harness.md` — internal/parity/shim_canary.go + internal/statusline/testdata/pyhooks/sitecustomize.py (determinism seams (design §3.2)) (BC-COMPONENT-MAP: ARCH-07 (ARCH-07-parity-harness.md))

## Story Anchor (Recommended)

TBD (filled by story-writer)

## VP Anchors (Recommended)

> Names provisional — architect (OD-145): harness flag names, the timing method, proposed
> test names and seed paths in this contract are delegated to the architect in
> create-architecture, subject to adversarial review. No behavior change.

- VP-034 — clock freeze and canary properties above

#### Purity Classification

| Property | Assessment |
|----------|-----------|
| **I/O operations** | spawns interpreters/builds; replay corpus and cache-swap I/O |
| **Global state access** | builds the child environment from scratch |
| **Deterministic** | stepped clock; seeded synthetic corpus |
| **Thread safety** | test-only, single-shot |
| **Overall classification** | infrastructure |

Owning component `internal/parity` (BC-COMPONENT-MAP: par/shim_canary.go + sl/testdata/pyhooks/sitecustomize.py - ARCH-07); the ARCH-00 package table classifies the package infrastructure - spawns interpreters/builds; test-only, never shipped in the render path.
