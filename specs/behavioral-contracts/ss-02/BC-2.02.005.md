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
  - semport/hylo-legacy/hylo-legacy-pass-5-deep-conventions-r3.md
input-hash: "720fc73"
traces_to: domain-spec/L2-INDEX.md
origin: greenfield
extracted_from: "n.a. (greenfield; legacy URL handling at legacy/dgx_statusline.py SL:73, SL:165-187)"
subsystem: "SS-02"
capability: "CAP-015"
legacy_id: new
parity_class: D4-EX-3
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

# Behavioral Contract BC-2.02.005: URL class: non-http(s) metrics URL is a config error

## Description

`backends[0].metrics_url` (BC-2.01.002) must be an absolute `http` or `https` URL with a
non-empty host. Legacy accepted any string and, on a bad URL, simply got no sample
(`fetch_sample` catches everything, SL:186-187), so the strip showed the dead state; hylo
rejects such values at load with the config-error line — approved deviation **D4-EX-3**
(URL class).

## Preconditions

1. `HYLO_BACKENDS_0_METRICS_URL` is present (BC-2.01.001). Absent → default
   `http://192.0.2.10:8428` (legacy SL:73).

## Postconditions

Checks run in this order; the first failing one produces the error (rendered per
BC-2.02.001 with `<key>` = `backends[0].metrics_url`):

1. The value contains a byte 0x00-0x1F or 0x7F → `(control character)`.
2. The scheme — the text before the first `://`, compared case-insensitively — is absent or
   is not `http` / `https` → `(scheme must be http or https)`. This covers `""`,
   `192.0.2.10:8428` (no scheme), `ftp://...`, `file:///...`, `unix:///...`.
3. Go `net/url.Parse` fails (e.g. a non-numeric port `http://h:abc`, a bad escape `%zz`)
   → `(not a URL)`.
4. The parsed host is empty (`http://`, `http:///path`) → `(missing host)`.
5. Otherwise the value is accepted and stored with all trailing `/` removed (legacy
   `rstrip("/")`, SL:73). Path, port and query parts are kept as given; the query URL is
   `<stored>/api/v1/query?query=<encoded>` (SL:165).

## Invariants

1. A loaded metrics URL always has scheme http/https and a host; reachability is not checked
   at load (an unreachable host yields the backend telemetry dead ladder at render, as in
   legacy).
2. The metrics request bypasses proxy env (legacy SL:168; Go `Transport{Proxy: nil}`); not
   part of this BC, stated for context.

## Edge Cases

| ID | Description | Expected Behavior |
|----|-------------|-------------------|
| EC-001 | `HTTP://192.0.2.10:8428` | valid (scheme case-insensitive) |
| EC-002 | `https://192.0.2.10/vm/` | valid; stored `https://192.0.2.10/vm` |
| EC-003 | `192.0.2.10:8428` | `scheme must be http or https` |
| EC-004 | `http://` | `missing host` |
| EC-005 | `http://192.0.2.10:abc` | `not a URL` |
| EC-006 | `""` (present, empty) | `backends[0].metrics_url= (scheme must be http or https)` |
| EC-007 | `http://192.0.2.10:99999` | valid at load (port reachability not checked); render shows the dead ladder |
| EC-008 | value with a tab | `control character`, value shown with `\x09` |

## Canonical Test Vectors

`\e` = 0x1B. Error rows: exit 0, no cache writes, no HTTP request.

| Input | Expected Output | Category |
|-------|----------------|----------|
| `HYLO_BACKENDS_0_METRICS_URL=http://192.0.2.10:8428/` | stored `http://192.0.2.10:8428`; normal render | happy-path |
| `HYLO_BACKENDS_0_METRICS_URL=ftp://192.0.2.10:8428` | `\e[90mhylo: config error: backends[0].metrics_url=ftp://192.0.2.10:8428 (scheme must be http or https)\e[0m\n` | error |
| `HYLO_BACKENDS_0_METRICS_URL=http://` | `\e[90mhylo: config error: backends[0].metrics_url=http:// (missing host)\e[0m\n` | edge-case |

## Verification Properties

| VP-NNN | Property | Proof Method |
|--------|----------|-------------|
| VP-016, VP-012 (frontmatter closure) | Accepted URL ⇒ scheme ∈ {http, https}, host ≠ "", no trailing `/` | Go property test (testing/quick) / fuzz |

## Traceability

| Field | Value |
|-------|-------|
| Source | new — OD-114 (T10: non-http(s) metrics URL is a config error), OD-102, OD-123 (key under the backend entry); legacy behavior replaced: legacy/dgx_statusline.py:module tunables (SL:73 `VM_URL ... .rstrip("/")`), fetch_sample (SL:165 URL build, SL:186-187 catch-all → no sample) |
| Parity / exclusion | **Approved deviation D4-EX-3 (URL class).** Named exclusion entry id `D4-EX-3`, cases `ftp://192.0.2.10:8428`, `192.0.2.10:8428`, `http://`, `""`, each with its expected output file; dedicated table test `TestD4EX3_URL` (OD-105, OD-110) |
| L2 Capability | CAP-015 (supports CAP-010) |
| L2 Domain Invariants | DI-008, DI-010 |
| Architecture Module | `internal/config/types.go` (`URL`) (BC-COMPONENT-MAP: internal/config/errors.go (URL class) — ARCH-02) |
| Stories | S-TBD (filled by story-writer) |

## Related BCs (Recommended)

- BC-2.01.002 — depends on (key placement, default)
- BC-2.02.001 — composes with (line format)

## Architecture Anchors (Recommended)

- `architecture/ARCH-02-configuration.md#url` — internal/config/errors.go (URL class) (URL type) (BC-COMPONENT-MAP: ARCH-02 (ARCH-02-configuration.md))

## Story Anchor (Recommended)

S-TBD — D4-EX-3 table tests

## VP Anchors (Recommended)

- VP-016, VP-012 — accepted URL shape

#### Purity Classification

| Property | Assessment |
|----------|-----------|
| **I/O operations** | reads the environment once at startup (`Load`) |
| **Global state access** | none (resolved config immutable) |
| **Deterministic** | yes (given the environment) |
| **Thread safety** | safe for concurrent use (immutable after `Load`) |
| **Overall classification** | boundary |

Owning component `internal/config` (BC-COMPONENT-MAP: cfg/errors.go (URL class) - ARCH-02); the ARCH-00 package table classifies the package boundary - pure registry and grammars, with `Load` reading the environment once at startup.
