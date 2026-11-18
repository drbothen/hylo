---
document_type: behavioral-contract
level: L3
version: "1.2.4"
status: draft
producer: product-owner
timestamp: 2026-11-18T01:42:00Z
phase: 1a
inputs:
  - domain-spec/L2-INDEX.md
  - domain-spec/invariants.md
  - behavioral-contracts/BC-ALLOCATION.md
  - semport/hylo-legacy/statusline-target-design.md
  - research/general-go-port-parity-crossplatform-2026-11-14.md
  - owner-decisions-log-2026-11-14.md
  - docs/PLAN.md
input-hash: "d53f404"
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
  - "1.2.1 2026-11-18T01:42:00Z ADV-P3 remediation D40: hostname/username pattern examples confirmed synthetic"
  - "1.2.2 2026-11-18: ADV-P4 remediation D12 - captures/ replays gain a git-ignored captures/exclusions.json validated by the same closed-set machinery (design call 12); CI never runs captures"
  - "1.2.3 2026-11-18T22:00:00Z: pass-4 correction (item 10) - corpus root restored to the OD-148 home internal/statusline/testdata/parity/cases/ (fixtures stay with the subject package); committed-testdata hygiene scan covers internal/statusline/testdata/ including parity/"
  - "1.2.4 2026-11-18: pass-4 sync-check SC-11 — modified history re-spun oldest-first so the version field matches the last entry; no behavioral change"
deprecated: null
deprecated_by: null
replacement: null
retired: null
removed: null
removal_reason: null
---

# Behavioral Contract BC-6.02.001: Committed corpus synthetic-only; owner real inputs replayed from git-ignored captures/

## Description

hylo is a public repository (D2). Every committed parity fixture is synthetic:
`testdata/` cases, generator specs, cache seeds and goldens. The owner's real recorded
inputs (copies of real transcripts and status line stdin) live only in the git-ignored
top-level `captures/` directory. They are replayed by the same harness, locally, and
never written into a tracked path. The real-input replay plus the synthetic CI corpus
together form the P1 success criterion (OD-107).

## Preconditions

1. `.gitignore` contains `/captures/` (present in the repository today) and
   `*.jsonl.local`.
2. Committed fixtures are produced by hand or by a committed Go generator (the
   transcript generator, design §5.2). A committed fixture derived from a real input
   exists only if a committed, reviewed scrub script produced it (CLAUDE.md
   public-repo hygiene).

## Postconditions

1. **Two corpus roots.** The harness loads cases from
   `internal/statusline/testdata/parity/cases/` (committed, synthetic) and, when the directory
   exists, from `captures/` at the repository root (git-ignored, local only).
2. **Captures never leave `captures/`.**
   - When a captures case is run with `-update`, its expected outputs are written under
     `captures/` only.
   - The harness refuses (fails) any write of a captures-derived artifact to a path
     under `internal/` or any other tracked path.
3. **Captures are optional.** When `captures/` is absent (always the case in CI), the
   real-input suite skips with `parity: captures/ absent; real-input replay skipped
   (OD-107, local only)`. The synthetic suite is unaffected.
3b. **Captures exclusion path (ADV-P4-D12, orchestrator design call 12).** Replays from
   `captures/` validate against a git-ignored `captures/exclusions.json` — never committed
   (PC-2 hygiene; real session ids and paths stay local) — using the SAME closed-set
   machinery as the committed exclusion file: identical id registry (the eleven minted ids,
   BC-6.03.004), per-entry expected-output and table-test rules, no blanket exclusions, and
   fail-the-run on an entry without its test. CI never runs captures, so the committed
   suite's closed set is unaffected. This makes the local "0 unexplained diffs on real
   inputs" criterion reachable: real sessions that diverge through D4-EX-2-, OD-76- or
   OD-159-class mechanisms are admissible only as named entries in that file.
4. **Hygiene gate on committed fixtures.** A test (`TestCorpusHygiene`) scans every
   file under every committed `testdata/` directory — `internal/statusline/testdata/`
   (including `parity/`), `internal/pyfmt/testdata/`, `internal/config/testdata/`,
   `cmd/hylo/testdata/` — and fails on any match of:
   - IPv4 addresses outside the RFC 5737 documentation ranges (`192.0.2.0/24`,
     `198.51.100.0/24`, `203.0.113.0/24`) and outside loopback `127.0.0.0/8`;
     RFC 1918 addresses always fail;
   - absolute home paths (`/Users/<name>`, `/home/<name>`, `C:\Users\<name>`) other than
     templated placeholders;
   - username and hostname patterns (macOS/Linux user or host names in paths or
     `username@host` shapes, e.g. `/Users/<name>`, ` boxes.local` — a synthetic example
     shaped like the real pattern, confirmed not a real machine name; ADV-P3-D40)
     other than templated placeholders;
   - e-mail addresses;
   - Claude-Session trailer lines or private session links.
   The legacy placeholder `192.0.2.10` passes. CI also runs gitleaks with
   `--log-opts="--all"` (BC-6.04.001).
5. **Goldens contain no machine paths.** Paths are templated into a per-case temp tree
   at run time (BC-6.02.003), so committed goldens contain only basenames (e.g.
   `home-lab`).

## Invariants

1. No tracked file is ever a copy, excerpt or derived golden of a real transcript,
   ledger, request/response capture or status line stdin, unless it went through a
   committed scrub script.
2. The same harness code path runs both corpora. Real-input replay is not a separate,
   less strict tool.

## Edge Cases

| ID | Description | Expected Behavior |
|----|-------------|-------------------|
| EC-001 | Developer copies a real transcript into `testdata/cases/x/` | `TestCorpusHygiene` fails on the home path or real IP if present. A pattern-clean real transcript is still forbidden by policy; review and the pre-push scan are the backstop |
| EC-002 | `-update` run against a captures case | Expected files written under `captures/<case>/`; nothing under `internal/` changes (`git status` clean for tracked files) |
| EC-003 | `captures/` absent | Real-input suite skips with the documented message; exit status of `go test` unaffected |
| EC-004 | Synthetic fixture uses `http://192.0.2.10:8428` | Passes (RFC 5737 placeholder; SL:73 legacy default) |
| EC-005 | Synthetic fixture contains any RFC 1918 address (the `10/8`, `172.16/12` or `192.168/16` blocks) | `TestCorpusHygiene` fails naming file and line |

## Canonical Test Vectors

| Input | Expected Output | Category |
|-------|----------------|----------|
| Committed case with `transcript_path` = `{{.CaseDir}}/t.jsonl` and URL `http://192.0.2.10:8428` | Hygiene test passes; case runs in CI | happy-path |
| CI checkout (no `captures/`) | Real-input suite skipped with message; synthetic suite runs | edge-case |
| A fixture file containing a literal macOS home path (`/Users/<name>/proj` with a real name in place of `<name>`) | `TestCorpusHygiene` FAIL with path and line number | error |
| Harness asked to write a captures-case golden to `internal/statusline/testdata/goldens/` | Harness FAIL; no file written | error |

## Verification Properties

| VP-NNN | Property | Proof Method |
|--------|----------|-------------|
| VP-035 | No file under `internal/statusline/testdata/` matches a forbidden-category pattern | `TestCorpusHygiene` (table of patterns + allowlist) |
| VP-035 | No harness write path places captures-derived bytes outside `captures/` | table test on the output-path resolver |

## Traceability

| Field | Value |
|-------|-------|
| Source | OD-107 (P1 success criterion = byte parity on the owner's real recorded inputs in local, git-ignored `captures/`, plus the synthetic corpus in CI); D2 (public repository); CLAUDE.md public-repo hygiene (synthetic fixtures or committed scrub script; gitleaks + pattern scan); design §5.2 ("synthetic only; public repo"); research Q3b (paths templated at runtime, goldens contain only basenames) |
| Parity class | n.a. (harness machinery) |
| L2 Capability | CAP-009 |
| L2 Domain Invariants | DI-012 |
| Architecture Module | `internal/parity` parity harness corpus loader (BC-COMPONENT-MAP: internal/parity/corpus.go (synthetic corpus; captures/) — ARCH-07) |
| Stories | TBD (filled by story-writer) |

> Capability anchor rationale (OD-153): the parity harness is verification machinery whose sole purpose is proving CAP-009 byte parity (the D4 exit criterion), governed by DI-012.

## Related BCs (Recommended)

- BC-6.02.002 — composes with: captured sessions replayed as stdin sequences
- BC-6.02.003 — composes with: case model shared by both corpora
- BC-6.04.001 — related to: gitleaks in CI with `--log-opts="--all"`

## Architecture Anchors (Recommended)

- `architecture/ARCH-07-parity-harness.md` — internal/parity/corpus.go (synthetic corpus; captures/) (parity harness corpus layout) (BC-COMPONENT-MAP: ARCH-07 (ARCH-07-parity-harness.md))

## Story Anchor (Recommended)

TBD (filled by story-writer)

## VP Anchors (Recommended)

- VP-035 — corpus hygiene properties above

#### Purity Classification

| Property | Assessment |
|----------|-----------|
| **I/O operations** | spawns interpreters/builds; replay corpus and cache-swap I/O |
| **Global state access** | builds the child environment from scratch |
| **Deterministic** | stepped clock; seeded synthetic corpus |
| **Thread safety** | test-only, single-shot |
| **Overall classification** | infrastructure |

Owning component `internal/parity` (BC-COMPONENT-MAP: par/corpus.go (synthetic corpus; captures/) - ARCH-07); the ARCH-00 package table classifies the package infrastructure - spawns interpreters/builds; test-only, never shipped in the render path.
