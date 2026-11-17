---
document_type: architecture-section
level: L3
section: "overview"
version: "1.1"
status: draft
producer: architect
timestamp: 2026-11-17T23:59:00Z
phase: 1b
inputs: [prd.md, product-brief.md, domain-spec/invariants.md, semport/hylo-legacy/statusline-target-design.md]
traces_to: ARCH-INDEX.md
input-hash: "4deb873"
---

# ARCH-00 — System Overview

> hylo P1 is one static Go binary per OS (`github.com/drbothen/hylo`, D1) whose only
> active subcommand family this cycle is `hylo statusline` (+ `version`, `config`).
> The status line is a pure function of stdin + transcript + metrics + caches (DI-007),
> ported byte-exact from `legacy/dgx_statusline.py` under the CPython 3.11.x oracle
> (OD-104). Rendering never fails: every fault lands on the degraded ladder — one-line
> output, exit 0 (DI-008). Reference for all idiom rows (IM-nn), pitfalls (PR-nn),
> thresholds and the BC mapping: `../semport/hylo-legacy/statusline-target-design.md`
> ("the design doc"); this architecture diverges from it only where an AD below says so.

## Principles

1. **D4 parity first** — the Go port reproduces legacy byte-for-byte on the fixture
   corpus and the owner's recorded inputs before any behavior change. Every deviation
   rides the closed named exclusion set (DI-012: D4-EX-1/2/3 + OD-110/OD-136 entries).
2. **D15 config over code** — every behavior-shaping value is a registry key with type,
   range, default and rationale; no magic numbers in logic. Protocol/format constants
   (29-byte line, D7 ledger schema, cache file-name formats) are named constants with a
   "why not config" comment.
3. **Pure core / effects shell** — widgets, parsers and format helpers are pure functions
   over plain values; all I/O is injected through the `Env` seam set and executed in
   legacy's exact side-effect order (BC-1.01.009) by one orchestrator.
4. **Never blank / exit 0** — any panic or typed degrade prints the 29-byte grey line and
   returns 0 (DI-008, NFR-002); config errors and unknown flags are themselves one-line
   outputs. Non-zero exits exist only in validate/usage/harness contexts.
5. **Stdlib first** — the only runtime dependency in P1 is `golang.org/x/sys` (process
   probes); the YAML library arrives with the P4 file layer (OD-107).

## Package map and dependency direction (AD-01, AD-02)

```mermaid
graph TD
    cmd["cmd/hylo<br/>(dispatch, run modes)"] --> sl["internal/statusline<br/>(frame, widgets, parser, store)"]
    cmd --> cfg["internal/config<br/>(registry, grammars, Load)"]
    cmd --> plat["internal/platform<br/>(paths, probes; build tags)"]
    sl --> cost["internal/cost<br/>(cost history read/record)"]
    sl --> cfg
    sl --> plat
    cfg --> plat

    par["internal/parity<br/>(harness runner; test-only)"] --> sl
    par --> cfg
    par --> plat
    py["internal/pyfmt<br/>(Python semantics helpers)"]
    sl --> py
    cost --> py
    cfg --> py
    par --> py
```

Strictly acyclic: arrows point from importer to imported; `internal/pyfmt` and
`internal/platform` are sinks (nothing imports through them back upward). Package-level
purity classification (file detail in the per-section maps):

| Package | Classification | I/O boundary |
|---|---|---|
| `internal/pyfmt` | **pure core** | none — bytes/values in, values out; clock never read |
| `internal/config` | **boundary** | pure registry/grammars; `Load` reads env once at startup and delegates path-default resolution, `~` expansion and the Windows case-insensitive env lookup to `internal/platform` (ADV-P1-A16/D21) |
| `internal/statusline` | **mixed (core-dominant)** | pure widgets + effect script (AD-03); I/O only via `Env` seams |
| `internal/cost` | **boundary** | pure percentile math; writes via injected `Store` |
| `internal/platform` | **infrastructure** | syscalls, `/proc`, `sysctl`, Win32; build-tag confined |
| `cmd/hylo` | **effectful shell** | `os.Args`/`os.Std*`, `os.Exit`; no logic |
| `internal/parity` | **infrastructure** | spawns interpreters/builds; test-only, never shipped in render path |

## Component architecture

Single-responsibility components and their explicit interfaces are defined per section:
binary/CLI (ARCH-01), config (ARCH-02), statusline render pipeline (ARCH-03), data files
(ARCH-04), platform (ARCH-05), pyfmt (ARCH-06), parity harness (ARCH-07), build/CI
(ARCH-08), reserved boundaries (ARCH-09). Every component appears in exactly one ARCH
section as its home; cross-references are by Go interface.

## Verification feasibility (iron law, package level)

- **Provable (pure core):** pyfmt arithmetic/JSON/string/time helpers; width/trim math;
  widget segment formatting; transcript state transitions; sample TTL machine; config
  grammars and registry ordering. Strategy: oracle-pinned tables + property/fuzz targets
  (design doc §2.6); mutation target >= 95% (AD-01 classes S1/S5, OD-135). **Mutation
  tool (P19): gremlins** (go-gremlins/gremlins) — it drives the standard `go test`
  suite per mutant and reports per-package mutation coverage, so it plugs into the
  3-OS gate unchanged; go-mutesting is an aging research prototype needing custom
  driver integration. **Oracle for random property samples (ADV-P1-A07):** CPython is
  available only as committed expectation tables, never live, so a random sample is
  asserted against a metamorphic oracle (round-trip, idempotence, monotonicity,
  first-wins/positional identity invariants) and additionally spot-pinned: each
  generator deterministically re-draws a fixed sample list and checks those cases
  against the committed CPython tables.

- **Testable-only (effects):** env reads, cache file I/O, HTTP fetch, process probes,
  interpreter spawning. Strategy: fake-server and fake-seam integration tests plus seeded
  parity cases; no proof claimed — side effects are confined to thin, table-covered shells.
- **Testable-only (effects):** env reads, cache file I/O, HTTP fetch, process probes,
  interpreter spawning. Strategy: fake-server and fake-seam integration tests plus seeded
  parity cases; no proof claimed — side effects are confined to thin, table-covered shells.
- The purity boundary is drawn **before** implementation design (ARCH-03, AD-03); a widget
  that needs I/O is redesigned, not patched (Critical Rules).
