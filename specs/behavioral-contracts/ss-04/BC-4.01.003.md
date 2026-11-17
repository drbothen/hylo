---
document_type: behavioral-contract
level: L3
version: "1.2.1"
status: draft
producer: product-owner
timestamp: 2026-11-17T21:45:00Z
phase: 1a
inputs:
  - BC-ALLOCATION.md
  - semport/hylo-legacy/statusline-target-design.md
  - docs/RESUME.md
input-hash: "3659c75"
traces_to: domain-spec/L2-INDEX.md
origin: greenfield
extracted_from: "n.a. (greenfield; no legacy counterpart)"
subsystem: "SS-04"
capability: "CAP-015"
legacy_id: new
parity_class: "n.a."
confidence: "—"
lifecycle_status: active
introduced: "0.1"
modified:
  - "patch bump + ADV-P2 pass-2 remediation (owner rulings OD-155..165), 2026-11-17T21:45:00Z"
deprecated: null
deprecated_by: null
replacement: null
retired: null
removed: null
removal_reason: null
---

# Behavioral Contract BC-4.01.003: hylo version prints the version string

## Description

`hylo version` prints one line, `hylo <version>`, and exits 0. The version is injected at
build time; an un-injected build falls back to the Go module build info, then to `dev`. The
command reads no configuration, so it works even when `HYLO_*` values are invalid.

## Preconditions

1. Invoked as `hylo version` with no further arguments.

## Postconditions

1. stdout is exactly `hylo ` + `<version>` + `\n`; stderr empty; exit 0.
2. `<version>` is, in order of preference: (a) the string variable `main.version` set by
   `-ldflags "-X main.version=<v>"` when non-empty (release builds, e.g. `v0.1.0`);
   (b) `runtime/debug.ReadBuildInfo().Main.Version` when build info is available and the
   value is non-empty (e.g. a module pseudo-version, or `(devel)` for a local build);
   (c) the literal `dev`.
3. No config resolution, no stdin read, no file or network access.
4. Any extra argument or flag: usage on stderr (BC-4.01.001 golden), exit 2.

## Invariants

1. Output is a single line with no SGR codes.
2. The output names the product `hylo` only (no "Claude" in names, CLAUDE.md trademark rule).

## Edge Cases

| ID | Description | Expected Behavior |
|----|-------------|-------------------|
| EC-001 | Built with `-X main.version=v0.1.0` | `hylo v0.1.0\n` |
| EC-002 | `go run ./cmd/hylo version` (no ldflags) | `hylo (devel)\n` — verified go1.26.5 (ADV-P2-D16): `go run` reports `Main.Version = "(devel)"` inside and outside a VCS checkout |
| EC-003 | Build info unavailable, no ldflags | `hylo dev\n` |
| EC-004 | `HYLO_STATUSLINE_ROWS=x` set | version printed normally, exit 0 |
| EC-005 | `hylo version --short` | usage on stderr, exit 2 |
| EC-006 | `go build` without ldflags in a VCS checkout (verified go1.26.5, ADV-P2-D16) | the binary prints a module pseudo-version, e.g. `hylo v0.0.0-20261117205840-<sha>\n` — `go build` stamps `Main.Version` from VCS state (readable via `go version -m`), unlike `go run`, which stays `(devel)` |

## Canonical Test Vectors

| Input | Expected Output | Category |
|-------|----------------|----------|
| argv `version`, binary built with `-X main.version=v0.1.0` | stdout `hylo v0.1.0\n`; exit 0 | happy-path |
| argv `version`, `main.version` empty, build info `(devel)` (go run) | stdout `hylo (devel)\n`; exit 0 | edge-case |
| argv `version extra` | stdout empty; stderr = `usage.golden`; exit 2 | error |

## Verification Properties

| VP-NNN | Property | Proof Method |
|--------|----------|-------------|
| VP-004 | stdout matches `^hylo [^\n]+\n$` for every build mode | table test |

## Traceability

| Field | Value |
|-------|-------|
| Source | new — RESUME P1 step 1 (`hylo version` in the skeleton dispatch), design §2.1 (`version.go`) |
| Parity / exclusion | n.a. |
| L2 Capability | CAP-015 (configuration management: emits the build-injected product version — product metadata owned by the CAP-015 verb family in this breakdown, alongside the S2.03 config subcommands; the command reads no runtime config; PRD §1 lists S4 under CAP-009, CAP-015) |
| L2 Domain Invariants | n.a. |
| Architecture Module | `cmd/hylo/version.go` (BC-COMPONENT-MAP: cmd/hylo/version.go — ARCH-01) |
| Stories | S-TBD (filled by story-writer) |

## Related BCs (Recommended)

- BC-4.01.001 — depends on (dispatch)

## Architecture Anchors (Recommended)

- `architecture/ARCH-01-binary-cli.md#version` — cmd/hylo/version.go (version command) (BC-COMPONENT-MAP: ARCH-01 (ARCH-01-binary-cli.md))

## Story Anchor (Recommended)

S-TBD — skeleton + dispatch

## VP Anchors (Recommended)

- VP-004 — version line shape

#### Purity Classification

| Property | Assessment |
|----------|-----------|
| **I/O operations** | `os.Args`/`os.Std*`, `os.Exit` |
| **Global state access** | process exit status |
| **Deterministic** | no (process boundary) |
| **Thread safety** | n.a. |
| **Overall classification** | effectful shell |

Owning component `cmd/hylo` (BC-COMPONENT-MAP: cmd/hylo/version.go - ARCH-01); the ARCH-00 package table classifies the package effectful shell - `os.Args`/`os.Std*`, `os.Exit`, no logic.
