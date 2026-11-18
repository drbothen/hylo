---
document_type: behavioral-contract
level: L3
version: "1.2.1"
status: draft
producer: product-owner
timestamp: 2026-11-18T01:42:00Z
phase: 1a
inputs:
  - BC-ALLOCATION.md
  - owner-decisions-log-2026-11-14.md
  - semport/hylo-legacy/statusline-target-design.md
  - semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts.md
  - semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts-r4.md
  - domain-spec/invariants.md
input-hash: "fea6dfc"
traces_to: domain-spec/L2-INDEX.md
origin: brownfield
extracted_from: "legacy/dgx_statusline.py (SL:73-100 import-time tunables)"
subsystem: "SS-02"
capability: "CAP-015"
legacy_id: BC-SL-087
parity_class: D4-EX-3
confidence: H
lifecycle_status: active
introduced: "0.1"
modified:
  - "2026-11-18T01:42:00Z ADV-P3 remediation D18+D32: subagent-mode config error = zero bytes stdout + stderr detail + exit 0 (OD-168); [from ENVNAME] rule covers indexed entries and defaults layer"
deprecated: null
deprecated_by: null
replacement: null
retired: null
removed: null
removal_reason: null
---

# Behavioral Contract BC-2.02.001: D4-EX-3 config-error line: exact format, exit 0, stderr detail, no cache writes

> Notation: `\e` is the byte 0x1B (ESC); `\n` is 0x0A (LF). Byte strings in this file are
> exact.

## Description

When configuration resolution (`config.Load`, BC-2.01.001) finds any invalid value,
`hylo statusline` prints exactly one line, `hylo: config error: <key>=<value> (<reason>)`,
wrapped in the grey SGR pair, exits 0, writes a per-error detail to stderr, and performs no
cache write, network fetch, subprocess or transcript read. This replaces legacy's
import-time crash (empty stdout, traceback, exit 1, blank status line) and is the approved
deviation **D4-EX-3** (OD-102), excluded from the parity diff by name (OD-105).

This file is the canonical home of the line format, the `<value>` escaping rule and the
reason vocabulary that the class contracts BC-2.02.002..006 and BC-2.01.002/003/005 use.

## Preconditions

1. `hylo statusline` was invoked with no unknown flag (an unknown flag takes precedence,
   BC-4.01.002).
2. `config.Load` returned one or more `*config.Error{Key, Value, Reason}` values for the
   resolved environment (P1: `HYLO_*` env + built-in defaults only, OD-107).

## Postconditions

1. **stdout** is exactly
   `\e[90m` + `hylo: config error: ` + `<key>` + `=` + `<value>` + ` (` + `<reason>` + `)` + `\e[0m` + `\n`
   for the **first** error in registry order (BC-2.01.004 `Registry()` order). Nothing else
   is written to stdout. Example (`HYLO_STATUSLINE_TELEMETRY_TTL_S=nan`):
   `\e[90mhylo: config error: statusline.telemetry.ttl_s=nan (not finite)\e[0m\n`.
2. `<key>` is the dotted config key name (e.g. `statusline.telemetry.ttl_s`,
   `backends[0].metrics_url`), never the env var name and never a legacy `DGX_*` name, so the
   line reads the same once the file layer arrives (P4).
3. `<value>` is the raw string as supplied, escaped as follows and otherwise verbatim (no
   truncation, no quoting): each byte 0x00-0x1F, the byte 0x7F, and each byte that is not
   part of a valid UTF-8 sequence is written as `\x` + two lowercase hex digits. A
   backslash in the input is written verbatim. Valid non-ASCII UTF-8 (e.g. `٤`) is written
   verbatim. This guarantees the output is exactly one line.
4. `<reason>` is one entry of the reason vocabulary below, byte-exact.
5. **Exit status is 0** (DI-008: never blank, never non-zero).
6. **stderr** receives one line per error, in registry order:
   `hylo: config error: <key>=<value> (<reason>) [from <ENVNAME>]\n`, where `<ENVNAME>` is
   the `HYLO_*` variable that actually supplied the value: `EnvName(key)` for scalar keys;
   for array keys the indexed indexed-entry form BC-2.01.002 pins (lowest extra index,
   tie-broken by registry field order, e.g. `HYLO_BACKENDS_1_METRICS_URL` — the `EnvName`
   of the key alone does not fit these entries, ADV-P3-D32); no `[from ...]` suffix when
   the failing value came from the defaults layer. stderr is not part of the parity
   comparison; it is asserted by Go table tests only.
7. **No side effects:** no file under the cache directory (`paths.cache_dir`, OD-101) is
   created, modified, renamed or deleted, and the directory itself is not created; no
   metrics HTTP request is sent; no `git` read and no process-ancestry probe runs; the
   transcript is not opened; stdin need not be read (output is identical for any stdin).
   This matches legacy's "nothing written" (legacy dies at import, before any write;
   design §3.1 step 0).

### Reason vocabulary (exact strings)

| Reason | Class | Raised by |
|--------|-------|-----------|
| `underscore in numeral` | number-grammar | BC-2.02.003 |
| `non-ASCII digit` | number-grammar | BC-2.02.003 |
| `not a number` | number-grammar | BC-2.02.003 (float/Seconds keys) |
| `not an integer` | number-grammar | BC-2.02.003 (Int keys) |
| `not finite` | number-range | BC-2.02.002 |
| `negative` | number-range | BC-2.02.002 |
| `must be > 0` | number-range | BC-2.02.002 (keys whose registry range excludes 0) |
| `out of range` | number-range | BC-2.02.002, BC-2.02.003 (int64 overflow) |
| `not a boolean (true\|false\|1\|0\|yes\|no)` | boolean | BC-2.02.006 (dedicated class contract, OD-140), BC-2.01.005 (grammar) |
| `unknown value (<v1>\|<v2>\|...)` | enum | BC-2.02.004 (`unknown value (rate\|kv\|ttft)` for the trace key) |
| `scheme must be http or https` | URL | BC-2.02.005 |
| `not a URL` | URL | BC-2.02.005 |
| `missing host` | URL | BC-2.02.005 |
| `control character` | URL / text | BC-2.02.005, BC-2.01.003 |
| `not an SGR parameter list` | theme | BC-2.01.003 |
| `empty path` | path | BC-2.01.005 |
| `home directory unknown` | path | BC-2.01.005 |
| `exactly one backend entry until P6` | backends | BC-2.01.002 |

Class-count reconciliation (ADV-P1-D33, mirrored from error-taxonomy.md): the class register
is closed at exactly six classes with dedicated class contracts and D4-EX-3 table tests —
number-range, number-grammar, enum, URL (OD-114), theme (OD-134), boolean (OD-140). The
`path` and `backends` columns above are reason categories without dedicated class contracts;
their reasons map to the raising contracts (BC-2.01.005, BC-2.01.002), and `control
character` maps to the URL class when raised by BC-2.02.005 and to the theme class when
raised by BC-2.01.003. A seventh class needs an owner decision.

(In the table `\|` is a literal `|`.)

8. **Subagent mode (OD-155/OD-168):** when the invocation carries `--subagent` anywhere in
   argv[1:] (BC-4.01.002), a config error writes **zero bytes to stdout** — the grey
   config-error line is not NDJSON and never reaches the agent panel (BC-1.07.004 wire
   grammar) — while stderr still receives the per-error detail lines of PC 6 and the exit
   status stays 0 (OD-168; ADV-P3-D18; legacy's `main_subagent` analog crashes at import
   with blank stdout and exit 1 — the exit status is an approved deviation per DI-008).
   Precedence is unchanged: an unknown flag still wins before config resolution
   (BC-4.01.002 PC-4).

## Invariants

1. The config-error line is printed only when `config.Load` fails; a valid configuration
   never produces it.
2. The SGR pair is the built-in literal `\e[90m` / `\e[0m`, independent of
   `statusline.theme.*` (BC-2.01.003), because the theme itself may be the invalid value.
   It is a named constant with a "why not config" comment.
3. The set of inputs that produce this line is exactly the set for which
   `hylo config validate` exits non-zero (BC-2.03.001).
4. Exit status 0 on every path (DI-008).

## Edge Cases

| ID | Description | Expected Behavior |
|----|-------------|-------------------|
| EC-001 | Two invalid keys (`HYLO_STATUSLINE_ROWS=2.0` and `HYLO_STATUSLINE_TELEMETRY_TTL_S=nan`) | stdout shows the one earlier in registry order; stderr shows both, registry order |
| EC-002 | Value contains a newline: `HYLO_STATUSLINE_SPARKLINE_TRACE=$'ra\nte'` | stdout `\e[90mhylo: config error: statusline.sparkline.trace=ra\x0ate (unknown value (rate\|kv\|ttft))\e[0m\n` (one line) |
| EC-003 | Value is the empty string (`HYLO_STATUSLINE_TELEMETRY_TTL_S=`) | `...ttl_s= (not a number)...`; legacy CP-X01 crashed (blank line, exit 1) |
| EC-004 | Cache dir does not exist beforehand | still does not exist afterwards |
| EC-005 | stdin is empty, invalid JSON or a valid session object | identical output in all three cases |
| EC-006 | Invalid value plus an unknown flag on the same run | the unknown-flag line wins (BC-4.01.002); no config-error line |
| EC-007 | Legacy `DGX_SL_TTL=four` set, no `HYLO_*` set | no error (DGX_* never read, BC-2.01.001); normal render |
| EC-008 | Value with an invalid UTF-8 byte 0xFF (`HYLO_STATUSLINE_ROWS=$'\xff'`) | `<value>` rendered `\xff`; reason `not an integer` |

## Canonical Test Vectors

| Input | Expected Output | Category |
|-------|----------------|----------|
| env `HYLO_STATUSLINE_TELEMETRY_TTL_S=nan`; any stdin | stdout `\e[90mhylo: config error: statusline.telemetry.ttl_s=nan (not finite)\e[0m\n`; exit 0; stderr `hylo: config error: statusline.telemetry.ttl_s=nan (not finite) [from HYLO_STATUSLINE_TELEMETRY_TTL_S]\n`; cache dir unchanged | error (number) |
| env `HYLO_STATUSLINE_GIT_ENABLED=on` | stdout `\e[90mhylo: config error: statusline.git.enabled=on (not a boolean (true\|false\|1\|0\|yes\|no))\e[0m\n`; exit 0 | error (boolean) |
| env `HYLO_BACKENDS_0_METRICS_URL=ftp://192.0.2.10:8428` | stdout `\e[90mhylo: config error: backends[0].metrics_url=ftp://192.0.2.10:8428 (scheme must be http or https)\e[0m\n`; exit 0 | error (URL) |
| env `HYLO_STATUSLINE_SPARKLINE_TRACE=mine` | stdout `\e[90mhylo: config error: statusline.sparkline.trace=mine (unknown value (rate\|kv\|ttft))\e[0m\n`; exit 0 | error (enum) |
| env `HYLO_STATUSLINE_ROWS=2.0` (legacy CP-X02 input) | stdout `\e[90mhylo: config error: statusline.rows=2.0 (not an integer)\e[0m\n`; exit 0 | edge-case (legacy crash input) |
| env empty (all defaults) | no config-error line; normal render per S1 | happy-path |

## Verification Properties

| VP-NNN | Property | Proof Method |
|--------|----------|-------------|
| VP-016, VP-012 (frontmatter closure) | For every env map, stdout is either the config-error line (exactly one LF, ending `\e[0m\n`) or not; exit is always 0 | Go property test (testing/quick) (Go fuzz over env maps) |
| VP-016, VP-012 (frontmatter closure) | A config-error run leaves the cache directory byte-identical (snapshot before/after) | table test |
| VP-016, VP-012 (frontmatter closure) | statusline prints the config-error line iff `config validate` exits non-zero | Go property test (testing/quick) |

## Traceability

| Field | Value |
|-------|-------|
| Source | legacy/dgx_statusline.py:module tunables (SL:73-100), import-time parse at SL:74 (`float(DGX_SL_TTL)`) and SL:75 (`int(DGX_SL_ROWS)`); guard that does NOT cover import at SL:1238-1245; legacy contract BC-SL-087 + crash paths CP-X01/CP-X02 (pass-3 r1 §B) |
| Decisions | OD-102 (format, exit 0, stderr, validate parity), OD-114 (error classes), OD-105/OD-110 (named exclusion), OD-05, OD-107, D15 |
| Parity / exclusion | **Approved deviation D4-EX-3.** Exclusion-list entry id `D4-EX-3` in `internal/statusline/testdata/parity/exclusions.json` (`{id, case, expected_output_file, table_test}`, OD-105); dedicated table tests `TestConfigError_D4EX3_Number`, `TestConfigError_D4EX3_Boolean`, `TestConfigError_D4EX3_URL`, `TestConfigError_D4EX3_Enum` plus the `config validate` test (BC-2.03.001). No blanket exclusion; an excluded case without its test fails the harness (BC-6.03.004) |
| L2 Capability | CAP-015 (also CAP-009) |
| L2 Domain Invariants | DI-008, DI-010 |
| Architecture Module | `internal/config/errors.go` (`Error.StatusLine()`), `cmd/hylo/statusline.go` (BC-COMPONENT-MAP: internal/config/errors.go (D4-EX-3 line) — ARCH-02) |
| Stories | S-TBD (filled by story-writer) |

## Related BCs (Recommended)

- BC-2.01.001 — depends on (resolution produces the errors)
- BC-2.02.002, BC-2.02.003, BC-2.02.004, BC-2.02.005, BC-2.02.006 — composes with (one error class each: number-range, number-grammar, enum, URL, boolean)
- BC-2.01.003 — composes with (theme class, OD-134)
- BC-2.01.005 — composes with (boolean / list / path grammar errors)
- BC-2.03.001 — related to (same error set, non-zero exit)
- BC-4.01.002 — related to (same one-line/exit-0 rule for unknown flags; takes precedence)
- BC-1.01.001 — related to (degraded line, the other one-line fallback)
- BC-6.03.004 — related to (exclusion-list machinery)

## Architecture Anchors (Recommended)

- `architecture/ARCH-02-configuration.md#errors` — internal/config/errors.go (D4-EX-3 line) (error type and line rendering) (BC-COMPONENT-MAP: ARCH-02 (ARCH-02-configuration.md))

## Story Anchor (Recommended)

S-TBD — config subset + D4-EX-3 (design §4 step S2)

## VP Anchors (Recommended)

- VP-016, VP-012 — config-error line iff validate fails

---

### Brownfield-Specific Sections

#### Source Evidence

| Property | Value |
|----------|-------|
| **Path** | `legacy/dgx_statusline.py` SL:73-100, SL:1238-1245 |
| **Confidence** | high (pass-3 r1 pinned CP-X01/X02: stdout 0 bytes, `ValueError` traceback, exit 1) |
| **Extraction Date** | 2026-11-15 |

#### Evidence Types Used

- **guard clause**: absent at import; the `try` at SL:1239 starts after module load
- **inferred**: legacy writes nothing before the crash (import precedes `main()`)

#### Purity Classification

| Property | Assessment |
|----------|-----------|
| **I/O operations** | reads env; writes stdout/stderr only |
| **Global state access** | reads process environment |
| **Deterministic** | yes (given env) |
| **Thread safety** | n.a. (single run) |
| **Overall classification** | effectful shell over a pure `Load(env) -> (*Config, []*Error)` |

#### Refactoring Notes

`config.Load` takes the environment as a map (seam) so the error set is table-testable
without a process; `Error.StatusLine()` is pure.
