---
document_type: behavioral-contract
level: L3
version: "1.2.1"
status: draft
producer: product-owner
timestamp: 2026-11-18T01:42:00Z
phase: 1a
inputs:
  - behavioral-contracts/BC-ALLOCATION.md
  - owner-decisions-log-2026-11-14.md
input-hash: "4638cd2"
traces_to: domain-spec/L2-INDEX.md
origin: greenfield
extracted_from: "n.a. (greenfield; grammar from OD-05 as pinned in BC-2.01.005)"
subsystem: "SS-02"
capability: "CAP-015"
legacy_id: new
parity_class: "D4-EX-3"
confidence: "—"
lifecycle_status: active
introduced: "0.1"
modified:
  - "2026-11-18T01:42:00Z ADV-P3 remediation D07: P1 Bool set completed with queue.yellow (P1 ruling, amending joins-in-P4) and subagent.enabled"
deprecated: null
deprecated_by: null
replacement: null
retired: null
removed: null
removal_reason: null
---

# Behavioral Contract BC-2.02.006: Boolean class: a non-typed-boolean value is a config error (true|false|1|0|yes|no)

## Description

The sixth config-error class (OD-140, completing OD-114's register): every `Bool` key
accepts exactly the typed grammar `true|false|1|0|yes|no` (case-sensitive, OD-05), and any
other value is a D4-EX-3 config error. Before this contract the boolean grammar lived only
inside BC-2.01.005 (parsing) with its D4-EX-3 test merely named in BC-2.02.001; this
contract gives the class its own S2.02 contract, symmetric with number-range, number-
grammar, enum and URL (BC-2.02.002..005). Register count discipline (ADV-P1-D33): the
register stays closed at six; the `path` and `backends` reason strings of the Reason
Vocabulary map to their raising contracts (BC-2.01.005, BC-2.01.002) and are not
additional classes.

## Preconditions

1. Resolution per BC-2.01.001; the value is the raw env string of a `Bool` key (P1 bool
   keys enumerated in BC-2.01.005 postcondition 1: `statusline.sparkline.enabled`,
   `statusline.git.enabled`, `statusline.queue.yellow` (P1 per the 2026-11-18 owner
   ruling; ADV-P3-D07, amending the earlier "joins in P4") and
   `statusline.subagent.enabled` (OD-155) — the complete P1 set).
2. Rendering context per BC-2.02.001 (D4-EX-3 line, exit 0, stderr detail, no cache writes).

## Postconditions

1. The accepted set is exactly `true`, `false`, `1`, `0`, `yes`, `no` — lower-case, no
   surrounding whitespace, no quotes. `true`/`1`/`yes` parse as true; `false`/`0`/`no`
   parse as false.
2. Any other value — including `""` (empty), `TRUE`, `Yes`, `ON`, `2`, `-1`, ` 1`, `on` —
   is a boolean-class config error: reason string `not a boolean (true|false|1|0|yes|no)`,
   rendered as
   `\e[90mhylo: config error: <key>=<value> (not a boolean (true|false|1|0|yes|no))\e[0m\n`
   (value control-escaped per BC-2.02.001), exit 0, full list on stderr.
3. The error participates in registry-order reporting: the first error in registry order is
   rendered on stdout; boolean errors hold no precedence over other classes.
4. `config validate` reports the same reason line for the same value, exit 1 (BC-2.03.001).
5. Legacy values legacy accepted that are outside this grammar (e.g. legacy turned any
   non-`"0"` string on, SL:76-77) are behavior changes covered by the D4-EX-3 exclusion
   (BC-2.01.005 traceability), not silent conversions.

## Invariants

1. The grammar is exactly the six-token set `true|false|1|0|yes|no` of OD-05; it does not
   grow with the registry.
2. The reason string is a fixed vocabulary entry (error-taxonomy Reason Vocabulary); the
   parenthesized token list is part of the observable bytes.

## Edge Cases

| ID | Description | Expected Behavior |
|----|-------------|-------------------|
| EC-001 | `HYLO_STATUSLINE_GIT_ENABLED=yes` | true; segment renders |
| EC-002 | `HYLO_STATUSLINE_GIT_ENABLED=Yes` | boolean-class error (`not a boolean (...)`) |
| EC-003 | `HYLO_STATUSLINE_GIT_ENABLED=` (empty) | boolean-class error (empty is not in the set) |
| EC-004 | `HYLO_STATUSLINE_GIT_ENABLED= 1` (leading space) | boolean-class error |
| EC-005 | `HYLO_STATUSLINE_GIT_ENABLED=2` | boolean-class error (legacy treated `"2"` as on — D4-EX-3) |
| EC-006 | `HYLO_STATUSLINE_GIT_ENABLED=-1` | boolean-class error |
| EC-007 | Two errors, a boolean and a number-range, in registry order | the registry-earlier one renders on stdout; both on stderr |

## Canonical Test Vectors

| Input | Expected Output | Category |
|-------|----------------|----------|
| env `{HYLO_STATUSLINE_GIT_ENABLED: "no"}` | git segment omitted; normal render, exit 0 | happy-path |
| env `{HYLO_STATUSLINE_GIT_ENABLED: "2"}` | stdout `\e[90mhylo: config error: statusline.git.enabled=2 (not a boolean (true\|false\|1\|0\|yes\|no))\e[0m\n`, exit 0 | error |
| env `{HYLO_STATUSLINE_GIT_ENABLED: "True"}` | same line with `statusline.git.enabled=True`; exit 0 | error |

Pinned against the D4-EX-3 golden format (BC-2.02.001); the grammar itself is OD-05, whose
byte observability here is the error line, so no CPython run is owed.

## Verification Properties

| VP-NNN | Property | Proof Method |
|--------|----------|-------------|
| VP-016, VP-012 (frontmatter closure) | Every string outside the six-token set produces the boolean-class line; every token inside it parses | Go property test (testing/quick) over random value strings |
| VP-016, VP-012 (frontmatter closure) | `TestConfigError_D4EX3_Boolean` covers one valid token and one invalid value per P1 bool key | table test |

## Traceability

| Field | Value |
|-------|-------|
| Source | new — OD-140 (dedicated boolean-class contract), OD-05 (typed booleans), OD-102/OD-114 (D4-EX-3 reporting) |
| Parity / exclusion | D4-EX-3 (boolean class) |
| L2 Capability | CAP-015 |
| L2 Domain Invariants | DI-010 |
| Architecture Module | `internal/config` (bool parse + class), `internal/statusline` (render) (BC-COMPONENT-MAP: internal/config/errors.go (boolean class) — ARCH-02) |
| Stories | S-TBD (filled by story-writer) |

## Related BCs (Recommended)

- BC-2.01.005 — composes with (the grammar this class validates)
- BC-2.02.001 — composes with (line format, registry order, stderr detail)
- BC-2.02.002..005 — related to (sibling classes)
- BC-2.03.001 — related to (validate exit 1)

## Architecture Anchors (Recommended)

- `architecture/ARCH-02-configuration.md#classes` — internal/config/errors.go (boolean class) (config-error classes) (BC-COMPONENT-MAP: ARCH-02 (ARCH-02-configuration.md))

## Story Anchor (Recommended)

S-TBD — config-error classes

## VP Anchors (Recommended)

- VP-016, VP-012 — grammar is exactly the six-token set

#### Purity Classification

| Property | Assessment |
|----------|-----------|
| **I/O operations** | reads the environment once at startup (`Load`) |
| **Global state access** | none (resolved config immutable) |
| **Deterministic** | yes (given the environment) |
| **Thread safety** | safe for concurrent use (immutable after `Load`) |
| **Overall classification** | boundary |

Owning component `internal/config` (BC-COMPONENT-MAP: cfg/errors.go (boolean class) - ARCH-02); the ARCH-00 package table classifies the package boundary - pure registry and grammars, with `Load` reading the environment once at startup.
