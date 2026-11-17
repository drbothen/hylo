---
document_type: behavioral-contract
level: L3
version: "1.2.1"
status: draft
producer: product-owner
timestamp: 2026-11-17T13:05:00Z
phase: 1a
inputs:
  - BC-ALLOCATION.md
  - owner-decisions-log-2026-11-14.md
  - domain-spec/entities.md
  - domain-spec/ubiquitous-language.md
  - semport/hylo-legacy/statusline-target-design.md
  - semport/hylo-legacy/hylo-legacy-pass-5-deep-conventions-r3.md
input-hash: "5ade8f5"
traces_to: domain-spec/L2-INDEX.md
origin: greenfield
extracted_from: "n.a. (greenfield; replaces legacy DGX_SL_VM_URL at SL:73 and LOCAL_MODEL_PREFIXES at SL:444-445)"
subsystem: "SS-02"
capability: "CAP-015"
legacy_id: new
parity_class: "n.a."
confidence: "—"
lifecycle_status: active
introduced: "0.1"
modified: ["1.2.1 2026-11-17: VP citation reconciliation — VP-016 added"]
deprecated: null
deprecated_by: null
replacement: null
retired: null
removed: null
removal_reason: null
---

# Behavioral Contract BC-2.01.002: backends array: exactly one entry validated until P6; backends[0].metrics_url / backends[0].model_prefixes; default prefixes claude-sonnet

## Description

Configuration models the backend as an array `backends` from the start (OD-123). Through
P5 the array must hold exactly one entry; zero or more than one entry is a config error. In
P1 the entry carries the two keys the status line needs: `backends[0].metrics_url` (the
metrics store the backend telemetry strip queries; legacy `DGX_SL_VM_URL`) and
`backends[0].model_prefixes` (the prefix rule that derives the client-view lane; legacy
`LOCAL_MODEL_PREFIXES`), with defaults `http://192.0.2.10:8428` and `claude-sonnet`.

## Preconditions

1. Resolution per BC-2.01.001 (P1: `HYLO_*` env + defaults).
2. Env names for array entries follow `EnvName` (BC-2.01.004): `HYLO_BACKENDS_<i>_<FIELD>`,
   with `<i>` a decimal index without leading zeros. P1 names:
   `HYLO_BACKENDS_0_METRICS_URL`, `HYLO_BACKENDS_0_MODEL_PREFIXES`.

## Postconditions

1. With no `HYLO_BACKENDS_*` variable present, `backends` has exactly one entry with
   `metrics_url = "http://192.0.2.10:8428"` (legacy default SL:73, RFC 5737 placeholder) and
   `model_prefixes = ["claude-sonnet"]` (OD-111; one key, one default).
2. `backends[0].metrics_url` is validated per BC-2.02.005 (http/https, non-empty host); the
   stored value is the input with **all** trailing `/` removed (legacy `rstrip("/")`, SL:73),
   so the query URL is `<metrics_url>/api/v1/query?query=...` exactly as SL:165 builds it.
3. `backends[0].model_prefixes` is a comma list (BC-2.01.005): split on `,`, each item
   stripped with Python `str.strip()` semantics, empty items dropped, order kept (legacy
   SL:444-445). A present-but-empty value yields the empty list, which makes the client-view
   lane unknown (`◨ ?`, BC-1.02.001).
4. A present variable `HYLO_BACKENDS_<i>_<FIELD>` with `<i>` ≠ `0` (any field name) defines
   an additional entry. If the entry count is not exactly 1, `Load` returns the error
   `backends=<count> (exactly one backend entry until P6)`, rendered per BC-2.02.001, where
   `<count>` is the number of distinct indices present plus index 0 (always present through
   its defaults); the `[from <ENVNAME>]` detail (BC-2.02.001) names the variable with the
   lowest extra index present, tie-broken by registry field order — for a single extra
   entry that is that entry's own variable (e.g. `HYLO_BACKENDS_1_METRICS_URL`) (spec
   choice pinning BC-2.03.001 EC-005, ADV-P1-D12). Example:
   `HYLO_BACKENDS_1_METRICS_URL=http://192.0.2.11:8428` →
   `hylo: config error: backends=2 (exactly one backend entry until P6)`. A variable
   `HYLO_BACKENDS_<i>_<FIELD>` whose `<FIELD>` is not a P1 key warns as an unknown setting
   for every index, `0` included (same discipline as PC-5).
5. `HYLO_BACKENDS_0_<FIELD>` for a field that is not a P1 key (e.g. `..._URL`,
   `..._NAME`) is an unknown setting: ignored with a stderr warning (BC-2.01.001 PC-6). The
   other OD-123 entry fields (name, url, protocol flavor, credential, CA, routing rules)
   join the registry in the phases that use them.
6. A malformed index (`HYLO_BACKENDS_00_METRICS_URL`, `HYLO_BACKENDS_X_METRICS_URL`) is an
   unknown setting (warning), not an entry.
7. The legacy top-level placements (`statusline.telemetry.url`,
   `routing.local_model_prefixes`, and env `HYLO_STATUSLINE_TELEMETRY_URL`,
   `HYLO_ROUTING_LOCAL_MODEL_PREFIXES`) are not registry keys (OD-123 supersedes OD-111's
   placement); setting them produces only the unknown-setting warning.

## Invariants

1. `len(backends) == 1` for every successfully loaded config through P5.
2. Zero entries is unreachable in P1 (index 0 always exists via defaults); the zero-entry
   error becomes reachable with the P4 file layer and uses the same message
   (`backends=0 (...)`).

## Edge Cases

| ID | Description | Expected Behavior |
|----|-------------|-------------------|
| EC-001 | `HYLO_BACKENDS_0_METRICS_URL=http://192.0.2.10:8428///` | stored `http://192.0.2.10:8428` |
| EC-002 | `HYLO_BACKENDS_0_MODEL_PREFIXES=" claude-sonnet , ,claude-haiku"` | `["claude-sonnet","claude-haiku"]` |
| EC-003 | `HYLO_BACKENDS_0_MODEL_PREFIXES=` | `[]`; lane unknown |
| EC-004 | `HYLO_BACKENDS_1_MODEL_PREFIXES=x` and `HYLO_BACKENDS_2_METRICS_URL=http://192.0.2.12` | `backends=3 (exactly one backend entry until P6)` |
| EC-005 | `HYLO_STATUSLINE_TELEMETRY_URL=http://192.0.2.99:8428` only | warning; metrics_url stays default |
| EC-006 | `HYLO_BACKENDS_0_METRICS_URL=https://192.0.2.10/vm` | valid; query URL `https://192.0.2.10/vm/api/v1/query?query=...` |

## Canonical Test Vectors

| Input | Expected Output | Category |
|-------|----------------|----------|
| env `{}` | `backends = [{metrics_url: "http://192.0.2.10:8428", model_prefixes: ["claude-sonnet"]}]` | happy-path |
| env `{HYLO_BACKENDS_0_MODEL_PREFIXES: ""}` | `model_prefixes = []` | edge-case |
| env `{HYLO_BACKENDS_1_METRICS_URL: "http://192.0.2.11:8428"}` | statusline stdout `\e[90mhylo: config error: backends=2 (exactly one backend entry until P6)\e[0m\n` (`\e` = 0x1B), exit 0 | error |

## Verification Properties

| VP-NNN | Property | Proof Method |
|--------|----------|-------------|
| VP-017 | Successful `Load` ⇒ exactly one backend entry | Go property test (testing/quick) over env maps |
| VP-017 | `metrics_url` stored value never ends with `/` | Go property test (testing/quick) |
| VP-016 | The backends-cardinality reason rides the closed six-class register (no seventh class): exact one-line E-CFG-001 stdout, exit 0, no cache writes (vector 3) | table test (class register) |

## Traceability

| Field | Value |
|-------|-------|
| Source | new — OD-123 (N backends in config, exactly one validated until P6, keys under the entry), OD-111 (default `claude-sonnet`), OD-120 (term backend); legacy inputs replaced: legacy/dgx_statusline.py:module tunables (SL:73 `VM_URL ... .rstrip("/")`), fetch_sample (SL:165 URL build), render_lane (SL:444-445 prefix split/strip) |
| Parity / exclusion | n.a.; legacy SL default for the prefixes is `""` (lane unknown) — parity cases for an unset prefix set `HYLO_BACKENDS_0_MODEL_PREFIXES=` explicitly (OD-111) |
| L2 Capability | CAP-015 (supports CAP-009, CAP-010) |
| L2 Domain Invariants | DI-010 |
| Architecture Module | `internal/config/statusline_keys.go`, `load.go` (BC-COMPONENT-MAP: internal/config/statusline_keys.go (backends[0] validator) — ARCH-02) |
| Stories | S-TBD (filled by story-writer) |

## Related BCs (Recommended)

- BC-2.01.001 — depends on (resolution)
- BC-2.01.005 — depends on (comma-list grammar)
- BC-2.02.005 — composes with (URL validation of metrics_url)
- BC-1.02.001 — consumer (lane pill from prefixes)
- BC-2.02.001 — composes with (error rendering)

## Architecture Anchors (Recommended)

- `architecture/ARCH-02-configuration.md#backends` — internal/config/statusline_keys.go (backends[0] validator) (backend entry schema) (BC-COMPONENT-MAP: ARCH-02 (ARCH-02-configuration.md))

## Story Anchor (Recommended)

S-TBD — config subset (design §4 step S2)

## VP Anchors (Recommended)

- VP-017 — exactly one backend entry; VP-016 — cardinality-reason error surface

#### Purity Classification

| Property | Assessment |
|----------|-----------|
| **I/O operations** | reads the environment once at startup (`Load`) |
| **Global state access** | none (resolved config immutable) |
| **Deterministic** | yes (given the environment) |
| **Thread safety** | safe for concurrent use (immutable after `Load`) |
| **Overall classification** | boundary |

Owning component `internal/config` (BC-COMPONENT-MAP: cfg/statusline_keys.go (backends[0] validator) - ARCH-02); the ARCH-00 package table classifies the package boundary - pure registry and grammars, with `Load` reading the environment once at startup.
