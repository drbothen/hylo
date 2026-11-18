---
document_type: behavioral-contract
level: L3
version: "1.2.5"
status: draft
producer: product-owner
timestamp: 2026-11-19T08:30:00Z
phase: 1a
inputs:
  - domain-spec/L2-INDEX.md
  - domain-spec/invariants.md
  - behavioral-contracts/BC-ALLOCATION.md
  - semport/hylo-legacy/statusline-target-design.md
  - semport/hylo-legacy/hylo-legacy-pass-5-deep-conventions-r3.md
  - semport/hylo-legacy/hylo-legacy-pass-5-deep-conventions-r5.md
  - owner-decisions-log-2026-11-14.md
input-hash: "d2e0a2c"
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
  - "2026-11-17T21:45:00Z: patch bump + ADV-P2 pass-2 remediation (owner rulings OD-155..165)"
  - "2026-11-18T23:00:00Z (1.2.2): ADV-P4 remediation D21 - TZ=UTC pinned for both binaries on every leg (OD-171, VP-026 posix-only tag removed); Env.Loc routed through internal/platform.LocalZone"
  - "2026-11-19T03:10:00Z (1.2.3): ADV-P6 remediation D27 + OD-183 - Description pins restated (GP-1..GP-4 forbidden outright, GP-5/GP-6 set to case temp values, nothing inherited); Windows oracle child gains exactly one extra variable PYTHONIOENCODING=utf-8 (stdio only; PYTHONUTF8 stays forbidden; POSIX unchanged), EC-002/CTV/VP rows aligned"
  - "2026-11-19T08:30:00Z (1.2.4): ADV-P7 remediation D05 (orchestrator call 2) + call 4 + OD-190 - this file is AUTHORITATIVE for the per-OS child-env allowlists: PC-1 consolidates the four exact key sets (POSIX/Windows × oracle/Go) with the conditional PATH/COLUMNS/setting keys, HOMEDRIVE/HOMEPATH explicitly not constructed, HOME+USERPROFILE on both OSes; PC-2 drops statusline.Env(Getenv,Home) for the platform.EnvVars seam with HomeDir(env)/LocalZone(env)/CacheDir(env) signatures; PC-4 names the OD-190 LF normalization (UTF-8 + LF on every OS) beside PYTHONIOENCODING=utf-8. ARCH-07 and VP-034 copy these sets verbatim"
  - "2026-11-19T21:00:00Z (1.2.5): ADV-P8 remediation D13+D10 — in-process Go path env lookups respelled EnvVars.Lookup(name) (string, bool) per ARCH-01; the conditional fake-PATH bullet states it has no P1 consumer (OD-76 D1-D4 vectors are Go table tests; machinery kept for the validator rejection rule and later phases)"
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
`PYTHONPATH`, and the pinned variables GP-1..GP-6 are never inherited from the
developer's or the CI runner's shell (DET-43): PC-3 forbids GP-1..GP-4 outright, and
GP-5/GP-6 (temp and home locations) are never inherited either — the builder sets them
to the case's fixed temp values (PC-1), so nothing from the parent shell leaks (ADV-P6-D27).

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
   - `TZ=<case zone>`. The harness pins `TZ=UTC` for BOTH binaries on every leg (OD-171):
     the Windows leg runs the naive local-time cases with no skip (VP-026's `posix-only`
     tag removed by the architect; ADV-P4-D21/ADV-P4-A2-06). Documented limitation
     (OD-171): POSIX-style TZ strings (e.g. `EST5EDT`) may differ between Go's zone loader
     and the MSVC runtime on Windows, so parity cases use `TZ=UTC` only.
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
     Consumer status (pass-8 D10 / orchestrator call 16): NO P1 corpus case declares a
     subprocess-fake table — the OD-76 D1-D4 vectors are Go table tests (BC-3.02.002) —
     so the conditional machinery has no P1 consumer; it is kept for the validator's
     rejection rule (BC-6.02.003 PC-6) and later phases. With
     no `PATH` key, CPython's subprocess fallback searches `os.defpath` (`/bin:/usr/bin`,
     SL:280) — which is why the harness rejects an unseeded case with a truthy
     `session_id` unless a fake table is declared (ADV-P2-D12; BC-6.02.003 PC-6).
   - **Authoritative exact key sets (pass-7 D05, orchestrator call 2 — ARCH-07 and
     VP-034 copy these sets verbatim).** With no fake table and no declared `COLUMNS`,
     the constructed key sets are exactly:
     - POSIX oracle child: `HOME`, `USERPROFILE`, `TMPDIR`, `LANG`, `TZ`,
       `PYTHONPATH`, `HYLO_TEST_NOW`, `LOCAL_MODEL_PREFIXES` (+ the `DGX_SL_*` keys
       the case sets, + `COLUMNS` when declared, + `PATH` when a fake table is
       declared).
     - Windows oracle child: the POSIX set, plus `TMP`, `TEMP`, `SYSTEMROOT` and
       `PYTHONIOENCODING=utf-8` (OD-183; the same conditional additions apply: + the
       `DGX_SL_*` keys the case sets, + `COLUMNS` when declared, + `PATH` when a fake
       table is declared).
     - POSIX Go child: `HOME`, `USERPROFILE`, `TMPDIR`, `XDG_CACHE_HOME`,
       `LOCALAPPDATA`, `HYLO_PATHS_CACHE_DIR`, `LANG`, `TZ`, `HYLO_TEST_NOW`,
       `HYLO_BACKENDS_0_MODEL_PREFIXES` (+ the `HYLO_*` setting keys the case sets, +
       `COLUMNS` when declared; no `PATH` ever — the built binary is started by
       absolute path).
     - Windows Go child: the POSIX Go set, plus `TMP`, `TEMP`, `SYSTEMROOT` (the same
       conditional additions apply).
     `HOMEDRIVE`/`HOMEPATH` are NOT constructed keys on any OS (home is
     `HOME`+`USERPROFILE`); no key set on any OS includes `PATH` unless the fake-table
     condition holds; `HOME` is present on BOTH OSes (Windows included) and
     `USERPROFILE` on BOTH OSes (POSIX included), always the same case-temp value.
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
   The in-process Go path receives the same values through the `platform.EnvVars`
   seam (BC-2.01.001 PC-6, orchestrator call 9 pass-5: `EnvVars` everywhere): env
   lookups via `EnvVars.Lookup(name) (string, bool)` (ARCH-01's interface method;
   pass-8 D13), the home directory via `platform.HomeDir(env EnvVars)`
   and the local zone via `platform.LocalZone(env EnvVars)` (orchestrator call 4,
   pass 7: no platform function reads the real process environment; the child's `TZ`
   feeds `LocalZone`). The same seam supplies `CacheDir(env EnvVars)`. It never reads
   the real process environment.
3. **Forbidden in every child:**
   - every proxy variable in any case: `http_proxy`, `https_proxy`, `no_proxy`,
     `all_proxy` and the upper-case forms (GP-3);
   - `REQUEST_METHOD`;
   - every `PYTHON*` variable except `PYTHONPATH`, including `PYTHONUTF8`,
     `PYTHONIOENCODING`, `PYTHONHOME`, `PYTHONSTARTUP` and `PYTHONSAFEPATH` — with the
     single OD-183 exception: the WINDOWS oracle child adds exactly one variable,
     `PYTHONIOENCODING=utf-8` (stdio only; `PYTHONUTF8` stays forbidden on every OS;
     the POSIX oracle child carries no `PYTHON*` variable beyond `PYTHONPATH`);
   - `GODEBUG` (GP-2), `ZONEINFO` (GP-1), `SSL_CERT_FILE` and `SSL_CERT_DIR` (GP-4);
   - every `HYLO_*` key the case does not set;
   - `DGX_*` and `LOCAL_MODEL_PREFIXES` in the Go child (OD-05);
   - `PATH` is not inherited. A child that needs one gets a fixed constant documented in
     the harness, not the runner's value.
4. **Locale and stdio are pinned.** The shim reconfigures oracle `stdin` and `stdout`
   to UTF-8 strict with `newline="\n"`. Windows text-mode stdout would otherwise write
   `\r\n` and encode as cp1252 (research P25). By OD-183 the Windows oracle child's
   stdio encoding additionally comes from the builder's `PYTHONIOENCODING=utf-8` —
   exactly one variable, stdio only; a table test proves it changes stdio encoding
   only (the constructed env differs from the POSIX builder in that key alone).
   By OD-190 this LF behavior is hylo-wide and named beside the builder variable,
   never hidden in the shim: hylo writes UTF-8 + LF line endings on every OS (OD-190
   extends OD-183), and the Windows oracle's LF normalization is produced by the two
   named mechanisms — the builder's `PYTHONIOENCODING=utf-8` (encoding) and the
   shim's `newline="\n"` reconfigure (LF-only newlines) — both called out here so a
   port knows the normalization is intentional.
   The harness captures child stdout as raw
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
| EC-002 | CI runner sets `PYTHONUTF8=1` or `PYTHONIOENCODING=cp1252` | Absent (inherited values are never copied). Stdio encoding comes only from the shim's reconfigure — except the builder's own `PYTHONIOENCODING=utf-8` on the Windows oracle child (OD-183, stdio only); `PYTHONUTF8` stays absent on every OS |
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
| Same inputs on Windows | As above plus `TMP`, `TEMP`, `SYSTEMROOT` and, on the oracle child only, `PYTHONIOENCODING=utf-8` (OD-183) | edge-case |
| Env builder modified to copy `os.Environ()` | Env-builder unit test fails, listing the leaked keys | error |

## Verification Properties

| VP-NNN | Property | Proof Method |
|--------|----------|-------------|
| VP-034 | For any parent environment, the constructed child env key set equals the per-side allowlist (case-dependent keys aside) | Go property test (testing/quick)-style table test with randomized parent envs |
| VP-034 | No forbidden key (proxy, PYTHON* except PYTHONPATH and the Windows OD-183 variable, GP-1..GP-4, DGX_* on Go side) appears in any child env, and the Windows oracle child carries exactly that one extra variable (`PYTHONIOENCODING=utf-8`) | table test + probe child |

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
