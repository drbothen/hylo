---
document_type: behavioral-contract
level: L3
version: "1.2"
status: draft
producer: product-owner
timestamp: 2026-11-17T12:00:00Z
phase: 1a
inputs:
  - domain-spec/L2-INDEX.md
  - domain-spec/invariants.md
  - behavioral-contracts/BC-ALLOCATION.md
  - ../semport/hylo-legacy/statusline-target-design.md
  - owner-decisions-log-2026-11-14.md
input-hash: "0000000"
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
modified: []
deprecated: null
deprecated_by: null
replacement: null
retired: null
removed: null
removal_reason: null
---

# Behavioral Contract BC-6.03.002: Comparison = stdout bytes + exit code per step; named caches byte-for-byte by file name; stderr never compared

## Description

Tier A (live differential) defines parity for one refresh step as equality of three
things:

- the stdout bytes;
- the process exit code;
- every named cache file, matched by file name across the two sides' cache
  directories.

stderr is never compared. Legacy tracebacks are invisible to Claude Code, and the
D4-EX-3 stderr detail has its own Go table tests. This is the comparison behind the P1
exit criterion (D4, PLAN §7) and the OD-117 parity target of "0 unexplained diffs".

## Preconditions

1. Both sides have run step `k` of a case with identical inputs (BC-6.02.002,
   BC-6.02.003).
2. Cache directories:
   - legacy: `<case-home>/.cache/dgx-llm/` (provenance: SL:78
     `~/.cache/dgx-llm`);
   - Go: `<case>/hylo-cache/` (`paths.cache_dir`, OD-101).
   The directories differ by design, so matching is by file name, never by full path.
3. Child stdout is captured as raw bytes (BC-6.01.002).

## Postconditions

1. **stdout.** `bytes.Equal(oracleStdout, goStdout)` must hold. No normalization is
   applied: no trimming, no CRLF folding, no SGR stripping, no Unicode normalization.
2. **Exit code.** The oracle exit code must equal the Go exit code. Both are expected
   to be 0 on every step (DI-008); a mismatch or a non-zero value on either side is a
   failure.
3. **Named caches.** Let `N_py` and `N_go` be the names of regular files directly in
   each cache dir, after removing mkstemp temp names (BC-6.03.003).
   - `N_py` must equal `N_go` as sets. A cache file present on one side only is a
     failure that names the file.
   - For every name in the set, the file contents must be byte-equal.
4. **stderr ignored.** Neither side's stderr takes part in the comparison. A legacy
   traceback, or a Go diagnostic, never makes a step fail by itself. It is kept in the
   failure report as context only.
5. **Step granularity.** The comparison runs after every step, before the next step
   starts. A later step never masks an earlier divergence.
6. **Exclusions.** If the case/step is listed in the exclusion list (BC-6.03.004),
   the comparison for the excluded artifact is replaced. Go's output is checked
   against the entry's expected file, and the entry's table test must exist. All
   non-excluded artifacts of that step are still compared to the oracle.
7. **Failure report.** Each failure names:
   - the case, the step and the artifact (`stdout` / `exit` / `<cache name>`);
   - the first differing byte offset;
   - a hex-and-escaped excerpt of up to 64 bytes around the offset from each side;
   - both stderr streams (context only).

## Invariants

1. No comparison mode normalizes or tolerates differences. The only allowed
   differences are named exclusion entries (DI-012; OD-105/OD-110).
2. The same comparator serves synthetic cases, captured-session replay and Tier C
   fuzz.

## Edge Cases

| ID | Description | Expected Behavior |
|----|-------------|-------------------|
| EC-001 | Legacy prints `statusline degraded` after a caught traceback on stderr, and Go prints the same 29 bytes with no stderr | Pass. stdout and exit match; stderr is ignored |
| EC-002 | Go writes `statusline-mix-<sid>.json` and legacy does not (Go took a path legacy did not) | FAIL: `cache statusline-mix-<sid>.json present on go only` |
| EC-003 | Session cache JSON identical except key order | FAIL. Byte comparison; key order is part of the format (BC-SL-091) |
| EC-004 | Legacy leaked `x.json.ab12cd34` (sid with `/`) | Temp name removed before comparison (BC-6.03.003); not a failure |
| EC-005 | D4-EX-3 case: Go prints the config-error line, legacy prints a row | stdout compared against the entry's expected file, not legacy; Go writes no cache (asserted by the entry) |
| EC-006 | Windows oracle stdout ends `\r\n` | Cannot happen with the shim (`newline="\n"`). If it does, FAIL. Never normalized |

## Canonical Test Vectors

| Input | Expected Output | Category |
|-------|----------------|----------|
| Step where both sides print golden A bytes, exit 0, and both cache dirs hold `{statusline-sess-golden-1.json, statusline-mix-sess-golden-1.json, statusline-git-<k>.json, cost-history.json}` with equal bytes | PASS | happy-path |
| Same, but legacy stderr has a traceback | PASS (stderr ignored) | edge-case |
| Go stdout `...$17.5/h\e[0m\n` vs legacy `...$17.6/h\e[0m\n` | FAIL: stdout, first difference at the byte of `5`/`6`, excerpts shown | error |

## Verification Properties

| VP-NNN | Property | Proof Method |
|--------|----------|-------------|
| VP-009 | The comparator reports equality iff stdout bytes, exit codes, named-cache name sets and per-file bytes are all equal (excluded artifacts aside) | table test on the comparator with synthetic side outputs |
| VP-009 | stderr content never changes the comparator's verdict | proptest (random stderr) |

## Traceability

| Field | Value |
|-------|-------|
| Source | OD-107 (parity on recorded inputs; sequences compared per step); design §5.3 (per step: stdout bytes and exit code; each named cache file byte for byte, matched by file name across directories, OD-101; never compared: stderr); OD-117 target (1) (0 unexplained byte diffs); D4 / PLAN §7 P1 exit criterion; legacy provenance `legacy/dgx_statusline.py` SL:42 (stderr invisible to Claude Code), SL:78 (legacy cache dir) |
| Parity class | n.a. (harness machinery) |
| L2 Capability | CAP-009 |
| L2 Domain Invariants | DI-012, DI-008 |
| Architecture Module | `internal/statusline` parity harness comparator (BC-COMPONENT-MAP: internal/parity/compare.go (bytes+exit+caches) — ARCH-07) |
| Stories | TBD (filled by story-writer) |

> Capability anchor rationale (OD-153): the parity harness is verification machinery whose sole purpose is proving CAP-009 byte parity (the D4 exit criterion), governed by DI-012.

## Related BCs (Recommended)

- BC-6.03.003 — composes with: temp names removed from the named-cache set
- BC-6.03.004 — composes with: exclusion entries replace the oracle comparison for listed artifacts
- BC-6.02.002 — depends on: per-step execution order
- BC-2.02.001 — related to: D4-EX-3 stderr detail asserted by Go table tests, not by this comparator

## Architecture Anchors (Recommended)

- `architecture/ARCH-07-parity-harness.md` — internal/parity/compare.go (bytes+exit+caches) (parity harness comparator) (BC-COMPONENT-MAP: ARCH-07 (ARCH-07-parity-harness.md))

## Story Anchor (Recommended)

TBD (filled by story-writer)

## VP Anchors (Recommended)

- VP-009 — comparator properties above

#### Purity Classification

| Property | Assessment |
|----------|-----------|
| **I/O operations** | spawns interpreters/builds; replay corpus and cache-swap I/O |
| **Global state access** | builds the child environment from scratch |
| **Deterministic** | stepped clock; seeded synthetic corpus |
| **Thread safety** | test-only, single-shot |
| **Overall classification** | infrastructure |

Owning component `internal/parity` (BC-COMPONENT-MAP: par/compare.go (bytes+exit+caches) - ARCH-07); the ARCH-00 package table classifies the package infrastructure - spawns interpreters/builds; test-only, never shipped in the render path.
