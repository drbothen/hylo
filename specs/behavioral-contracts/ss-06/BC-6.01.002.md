---
document_type: behavioral-contract
level: L3
version: "1.2"
status: draft
producer: product-owner
timestamp: 2026-11-17T11:45:00Z
phase: 1a
inputs:
  - domain-spec/L2-INDEX.md
  - domain-spec/invariants.md
  - behavioral-contracts/BC-ALLOCATION.md
  - semport/hylo-legacy/statusline-target-design.md
  - semport/hylo-legacy/hylo-legacy-pass-5-deep-conventions-r3.md
  - semport/hylo-legacy/hylo-legacy-pass-5-deep-conventions-r5.md
  - owner-decisions-log-2026-11-14.md
input-hash: "a8c5a2c"
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

# Behavioral Contract BC-6.01.002: Child environment constructed from scratch: no *_proxy, fixed HOME/TMPDIR/locale

## Description

For every child the harness starts, it builds the environment from an empty list. That
covers the oracle interpreter, its version probe and the built `hylo` binary. Nothing is
inherited from the `go test` process. The child gets only an explicit allowlist: per-case
temp `HOME`/`USERPROFILE`/`TMPDIR`, a fixed UTF-8 locale, the case's `TZ` and `COLUMNS`,
and the translated settings. Proxy variables, `PYTHON*` variables other than
`PYTHONPATH`, and the Go-side pins GP-1..GP-6 can never leak in from the developer's or
the CI runner's shell (DET-43).

## Preconditions

1. The case runner has created a per-case temp tree `<case>` containing `home/`,
   `tmp/`, the fixture tree (transcript, project directory) and, for the Go side,
   `hylo-cache/`.
2. The case declares `TZ` (default `UTC`), optional `COLUMNS` and its settings
   (BC-6.02.003).
3. The process environment of `go test` may contain arbitrary variables, for example
   `HTTPS_PROXY`, `no_proxy`, `PYTHONUTF8`, `PYTHONHOME`, `GODEBUG`, `SSL_CERT_FILE`,
   `XDG_CACHE_HOME`, `HYLO_*`, `DGX_*` or `LOCAL_MODEL_PREFIXES`.

## Postconditions

1. **Oracle child env.** It contains exactly these keys and nothing else:
   - `HOME=<case-home>` and `USERPROFILE=<case-home>`. Both are set because Python 3.8+
     `expanduser` ignores `HOME` on Windows. Legacy then writes its caches to
     `<case-home>/.cache/dgx-llm/` (provenance: `legacy/dgx_statusline.py` SL:78).
   - `TMPDIR=<case>/tmp`; on Windows also `TMP` and `TEMP` set to the same value.
   - `LANG=en_US.UTF-8`.
   - `TZ=<case zone>`.
   - `PYTHONPATH=<abs>/internal/statusline/testdata/pyhooks`, the clock shim of
     BC-6.01.003.
   - `HYLO_TEST_NOW=<step instant>` (BC-6.01.003).
   - `COLUMNS=<value>`, only when the case or step declares it.
   - The legacy-side spelling of the case settings. These are legacy's own env names,
     quoted as provenance from SL:73-77, 89 and 444 (`DGX_SL_TRACE` is at SL:89;
     ADV-P1-D23): `DGX_SL_VM_URL`, `DGX_SL_TTL`,
     `DGX_SL_ROWS`, `DGX_SL_SPARK`, `DGX_SL_GIT`, `DGX_SL_TRACE`, `LOCAL_MODEL_PREFIXES`.
     Only keys the case sets are included, except `LOCAL_MODEL_PREFIXES`, which is always
     set explicitly (OD-111; BC-6.02.003).
   - On Windows only, `SYSTEMROOT` with the runner's value. CPython cannot start without
     it, and Go's `os/exec` adds it on Windows when it is missing.
   - `PATH=<case>/bin`, ONLY when the case declares a subprocess-fake table (the fake
     `ps` of BC-3.02.002). The value is the harness constant, never the runner's
     `PATH`; cases without a fake table get no `PATH` key (ADV-P1-D05 resolution).
2. **Go child env** (built binary). It contains exactly these keys:
   - `HOME` and `USERPROFILE` as above.
   - `TMPDIR`, plus `TMP`/`TEMP` on Windows (GP-5).
   - `XDG_CACHE_HOME=<case>/xdg-cache` and `LOCALAPPDATA=<case>/localappdata` (design
     §3.2).
   - The `paths.cache_dir` key in its HYLO_* env form, set to `<case>/hylo-cache`
     (OD-101; design §3.2 names it `HYLO_PATHS_CACHE_DIR`).
   - `LANG=en_US.UTF-8`, `TZ=<case zone>` and `HYLO_TEST_NOW`.
   - `COLUMNS` when declared.
   - The HYLO_* spelling of the case settings (S2 key registry).
   - On Windows, `SYSTEMROOT`.
   The in-process Go path receives the same values through `statusline.Env` (`Getenv`,
   `Home`, `Now`, `Loc`). It never reads the real process environment.
3. **Forbidden in every child:**
   - every proxy variable in any case: `http_proxy`, `https_proxy`, `no_proxy`,
     `all_proxy` and the upper-case forms (GP-3);
   - `REQUEST_METHOD`;
   - every `PYTHON*` variable except `PYTHONPATH`, including `PYTHONUTF8`,
     `PYTHONIOENCODING`, `PYTHONHOME`, `PYTHONSTARTUP` and `PYTHONSAFEPATH`;
   - `GODEBUG` (GP-2), `ZONEINFO` (GP-1), `SSL_CERT_FILE` and `SSL_CERT_DIR` (GP-4);
   - every `HYLO_*` key the case does not set;
   - `DGX_*` and `LOCAL_MODEL_PREFIXES` in the Go child (OD-05);
   - `PATH` is not inherited. A child that needs one gets a fixed constant documented in
     the harness, not the runner's value.
4. **Locale and stdio are pinned.** The shim reconfigures oracle `stdin` and `stdout`
   to UTF-8 strict with `newline="\n"`. Windows text-mode stdout would otherwise write
   `\r\n` and encode as cp1252 (research P25). The harness captures child stdout as raw
   bytes, never through text-mode decoding.
5. **Assertion.** Before the first case, an env-builder unit test checks the exact
   key set of both child envs. It runs with a parent env that contains every forbidden
   variable above set to sentinel values. Separately, a probe child
   (`<python> -s -c "import os,json; print(json.dumps(sorted(os.environ)))"`) must show
   none of the forbidden keys. Variables the interpreter adds itself after start, such
   as `LC_CTYPE` from PEP 538 coercion or macOS `__CF_USER_TEXT_ENCODING`, are not
   failures. The exact-set check applies to the constructed list, not to the child's
   view of it.

## Invariants

1. Child environments are passed per subprocess (`exec.Cmd.Env`), never through
   `os.Setenv`/`t.Setenv`. Cases can therefore run in parallel without cross-talk.
2. Both sides of one step see the same `TZ`, `COLUMNS`, `HYLO_TEST_NOW` and the same
   rendered stdin paths (BC-6.02.003).
3. No value in any child env contains a real home path or host name; all paths are
   under the per-case temp tree.

## Edge Cases

| ID | Description | Expected Behavior |
|----|-------------|-------------------|
| EC-001 | Developer shell exports `HTTPS_PROXY=http://192.0.2.1:8090` (the launcher exports a proxy for its client) | Absent from both children. Legacy would bypass it anyway at SL:168, but it is not present |
| EC-002 | CI runner sets `PYTHONUTF8=1` or `PYTHONIOENCODING=cp1252` | Absent. Stdio encoding comes only from the shim's reconfigure |
| EC-003 | Parent sets `HYLO_STATUSLINE_*` or `DGX_SL_TTL=nan` | Absent unless the case declares the setting; a case cannot inherit config by accident |
| EC-004 | Windows child built without `SYSTEMROOT` | Not allowed: the builder always adds it on Windows. CPython would fail at startup otherwise |
| EC-005 | `PYTHONPATH` missing from the oracle env | Not allowed. If a bug removes it, the shim canary (BC-6.01.003) fails the run |
| EC-006 | Case declares no `COLUMNS` | `COLUMNS` is absent from both children (legacy `term_cols()` then returns 0, SL:1185-1190) |
| EC-007 | Interpreter injects `LC_CTYPE` or `__CF_USER_TEXT_ENCODING` itself | Not a failure; only the constructed env list is checked for exact equality |

## Canonical Test Vectors

| Input | Expected Output | Category |
|-------|----------------|----------|
| Parent env `{HTTPS_PROXY, no_proxy, PYTHONUTF8, GODEBUG, SSL_CERT_FILE, HYLO_X, DGX_SL_TTL, HOME=/real}`; case `TZ=UTC`, no COLUMNS, settings `{}` (Linux) | Oracle env keys exactly `{HOME, USERPROFILE, TMPDIR, LANG, TZ, PYTHONPATH, HYLO_TEST_NOW, LOCAL_MODEL_PREFIXES}`, with `HOME` under the case temp tree | happy-path |
| Same parent env; Go binary child (Linux) | Keys exactly `{HOME, USERPROFILE, TMPDIR, XDG_CACHE_HOME, LOCALAPPDATA, <paths.cache_dir env>, LANG, TZ, HYLO_TEST_NOW, <backends[0].model_prefixes env>}` | happy-path |
| Same inputs on Windows | As above plus `TMP`, `TEMP`, `SYSTEMROOT` | edge-case |
| Env builder modified to copy `os.Environ()` | Env-builder unit test fails, listing the leaked keys | error |

## Verification Properties

| VP-NNN | Property | Proof Method |
|--------|----------|-------------|
| VP-034 | For any parent environment, the constructed child env key set equals the per-side allowlist (case-dependent keys aside) | Go property test (testing/quick)-style table test with randomized parent envs |
| VP-034 | No forbidden key (proxy, PYTHON* except PYTHONPATH, GP-1..GP-4, DGX_* on Go side) appears in any child env | table test + probe child |

## Traceability

| Field | Value |
|-------|-------|
| Source | OD-109 ("the harness constructs the child environment from scratch (no inherited vars)"); P5r3 §B.3 DET-43 (env from scratch for both the oracle and the Go binary), GP-1..GP-6; P5r3/r5 §B.4 P1 pin set (temp `HOME`+`USERPROFILE`, `LANG=en_US.UTF-8`, `TZ`, `COLUMNS`); design §3.2 "Cache dir", "Locale / stdio", "Env from scratch" rows; OD-05 (no DGX_* on the Go side); OD-101 (Go cache dir) |
| Parity class | n.a. (harness machinery) |
| L2 Capability | CAP-009 |
| L2 Domain Invariants | DI-012 |
| Architecture Module | `internal/parity` parity harness env builder (BC-COMPONENT-MAP: internal/parity/env.go (child env from scratch) — ARCH-07) |
| Stories | TBD (filled by story-writer) |

> Capability anchor rationale (OD-153): the parity harness is verification machinery whose sole purpose is proving CAP-009 byte parity (the D4 exit criterion), governed by DI-012.

## Related BCs (Recommended)

- BC-6.01.001 — composes with: the oracle exec that uses this env
- BC-6.01.003 — depends on: `PYTHONPATH` and `HYLO_TEST_NOW` are set here
- BC-6.02.003 — depends on: case settings and their two-sided translation
- BC-2.01.001 — related to: the Go binary resolves HYLO_* env over defaults only; DGX_* never read

## Architecture Anchors (Recommended)

- `architecture/ARCH-07-parity-harness.md` — internal/parity/env.go (child env from scratch) (parity harness child-process construction) (BC-COMPONENT-MAP: ARCH-07 (ARCH-07-parity-harness.md))

## Story Anchor (Recommended)

TBD (filled by story-writer)

## VP Anchors (Recommended)

- VP-034 — child-env allowlist properties above

#### Purity Classification

| Property | Assessment |
|----------|-----------|
| **I/O operations** | spawns interpreters/builds; replay corpus and cache-swap I/O |
| **Global state access** | builds the child environment from scratch |
| **Deterministic** | stepped clock; seeded synthetic corpus |
| **Thread safety** | test-only, single-shot |
| **Overall classification** | infrastructure |

Owning component `internal/parity` (BC-COMPONENT-MAP: par/env.go (child env from scratch) - ARCH-07); the ARCH-00 package table classifies the package infrastructure - spawns interpreters/builds; test-only, never shipped in the render path.
