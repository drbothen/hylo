---
document_type: behavioral-contract
level: L3
version: "1.2"
status: draft
producer: product-owner
timestamp: 2026-11-17T11:45:00Z
phase: 1a
inputs:
  - BC-ALLOCATION.md
  - owner-decisions-log-2026-11-14.md
  - semport/hylo-legacy/statusline-target-design.md
input-hash: "51f00c6"
traces_to: domain-spec/L2-INDEX.md
origin: greenfield
extracted_from: "n.a. (greenfield; no legacy counterpart)"
subsystem: "SS-02"
capability: "CAP-015"
legacy_id: new
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

# Behavioral Contract BC-2.03.001: hylo config validate exits non-zero on the same errors as D4-EX-3

## Description

`hylo config validate` resolves configuration exactly as `hylo statusline` does
(BC-2.01.001) and reports the result through its exit status: 0 when every key is valid, 1
when `config.Load` returns any error. The error set is identical to the set that makes
`hylo statusline` print the D4-EX-3 config-error line (OD-102). It ships in P1 (OD-107).

## Preconditions

1. Invoked as `hylo config validate` with no further arguments.

## Postconditions

1. **Valid config:** stdout is exactly `hylo: config ok\n`; stderr carries only
   unknown-setting warnings (BC-2.01.001 PC-6), if any; exit 0.
2. **Invalid config:** stdout is empty; stderr carries one line per error in registry order,
   in the same form as the statusline stderr detail,
   `hylo: config error: <key>=<value> (<reason>) [from <ENVNAME>]\n` (value escaping and
   reasons per BC-2.02.001, no SGR codes), followed by any unknown-setting warnings; exit 1.
3. No stdin read, no cache read or write, no network request, no subprocess.
4. Unknown-setting warnings alone never change the exit status.
5. Extra arguments or flags (`hylo config validate --x`, `hylo config validate foo`): usage
   text on stderr (golden `cmd/hylo/testdata/usage.golden`, BC-4.01.001), exit 2. This
   subcommand is not the status line, so the never-non-zero rule does not apply.

## Invariants

1. For every environment E: `hylo config validate` exits non-zero under E ⇔
   `hylo statusline` prints the config-error line under E (with no unknown flag).
2. P1 checks env + defaults only; a config file at the resolved path is not read
   (OD-107) and does not affect the result.

## Edge Cases

| ID | Description | Expected Behavior |
|----|-------------|-------------------|
| EC-001 | No `HYLO_*` set | stdout `hylo: config ok\n`, exit 0 |
| EC-002 | Two invalid keys | two stderr lines (registry order), exit 1 |
| EC-003 | Only `HYLO_FOO=1` | stdout `hylo: config ok\n`, stderr warning, exit 0 |
| EC-004 | `DGX_SL_TTL=nan` only | ok, exit 0 (legacy names never read) |
| EC-005 | `HYLO_BACKENDS_1_METRICS_URL=http://192.0.2.11` | stderr `hylo: config error: backends=2 (exactly one backend entry until P6) [from HYLO_BACKENDS_1_METRICS_URL]`, exit 1 |

## Canonical Test Vectors

| Input | Expected Output | Category |
|-------|----------------|----------|
| env `{}` | stdout `hylo: config ok\n`; stderr empty; exit 0 | happy-path |
| env `{HYLO_STATUSLINE_TELEMETRY_TTL_S: "nan"}` | stdout empty; stderr `hylo: config error: statusline.telemetry.ttl_s=nan (not finite) [from HYLO_STATUSLINE_TELEMETRY_TTL_S]\n`; exit 1 | error |
| env `{HYLO_STATUSLINE_TELEMETRY_TTL_S: "0"}` | stdout `hylo: config ok\n`; exit 0 | edge-case |

## Verification Properties

| VP-NNN | Property | Proof Method |
|--------|----------|-------------|
| VP-004, VP-016 | validate exit ≠ 0 ⇔ statusline prints the config-error line, over generated env maps | Go property test (testing/quick) (shared generator with BC-2.02.001) |

## Traceability

| Field | Value |
|-------|-------|
| Source | new — OD-102 (`hylo config validate` exits non-zero for the same errors), OD-107 (ships in P1; env + defaults only), tension T6 |
| Parity / exclusion | n.a. (not a legacy surface); part of the D4-EX-3 test set named in design §5.4 ("+ `config validate`") |
| L2 Capability | CAP-015 |
| L2 Domain Invariants | DI-010 |
| Architecture Module | `cmd/hylo/config.go` (BC-COMPONENT-MAP: cmd/hylo/config.go (validate exit 1) — ARCH-01) |
| Stories | S-TBD (filled by story-writer) |

## Related BCs (Recommended)

- BC-2.02.001 — related to (same error set; statusline counterpart)
- BC-2.01.001 — depends on (resolution)
- BC-4.01.001 — depends on (dispatch)

## Architecture Anchors (Recommended)

- `architecture/ARCH-01-binary-cli.md#config` — cmd/hylo/config.go (validate exit 1) (config subcommands) (BC-COMPONENT-MAP: ARCH-01 (ARCH-01-binary-cli.md))

## Story Anchor (Recommended)

S-TBD — config subcommands

## VP Anchors (Recommended)

- VP-004, VP-016 — validate/statusline error-set equivalence

#### Purity Classification

| Property | Assessment |
|----------|-----------|
| **I/O operations** | `os.Args`/`os.Std*`, `os.Exit` |
| **Global state access** | process exit status |
| **Deterministic** | no (process boundary) |
| **Thread safety** | n.a. |
| **Overall classification** | effectful shell |

Owning component `cmd/hylo` (BC-COMPONENT-MAP: cmd/hylo/config.go (validate exit 1) - ARCH-01); the ARCH-00 package table classifies the package effectful shell - `os.Args`/`os.Std*`, `os.Exit`, no logic.
